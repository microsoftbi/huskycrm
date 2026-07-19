import json
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.auth import User
from app.models.import_job import ImportJob
from app.models.crm import Account, Contact, Product, Opportunity
from app.schemas.import_export import (
    ImportPreviewResponse, ImportConfirmRequest, ImportResultResponse, ImportJobOut,
)
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services.csv_service import parse_csv, create_preview, confirm_import, generate_csv
from app.services.audit_service import current_user_id

router = APIRouter(prefix="/api/import", tags=["import"])

# Export models
EXPORT_MODELS = {
    "account": Account,
    "contact": Contact,
    "product": Product,
    "opportunity": Opportunity,
}

# ── Import ─────────────────────────────────────────────────────────────

@router.post("/upload", response_model=ImportPreviewResponse)
async def upload_csv(
    file: UploadFile = File(...),
    object_type: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    """Upload a CSV file, parse it, and return preview data."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    try:
        headers, rows = parse_csv(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if object_type not in ("account", "contact", "product", "opportunity"):
        raise HTTPException(status_code=400, detail=f"Unsupported object type: {object_type}")

    return ImportPreviewResponse(**create_preview(headers, rows, object_type))


@router.post("/confirm", response_model=ImportResultResponse)
async def confirm_import_endpoint(
    payload: ImportConfirmRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    """Confirm and execute the import."""
    token = current_user_id.set(current_user.id)
    try:
        result = await confirm_import(db, payload.preview_id, payload.mapping, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        current_user_id.reset(token)

    # Save import job record
    job = ImportJob(
        object_type="account",
        filename="import.csv",
        total_rows=result["success_rows"] + result["error_rows"],
        success_rows=result["success_rows"],
        error_rows=result["error_rows"],
        errors=json.dumps(result["errors"]) if result["errors"] else None,
        status="completed" if result["error_rows"] == 0 else "completed",
        created_by=current_user.id,
    )
    db.add(job)
    await db.commit()

    return ImportResultResponse(**result)


@router.get("/jobs", response_model=dict)
async def list_import_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """List import history."""
    query = (
        select(ImportJob)
        .order_by(ImportJob.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    count_result = await db.execute(select(func.count(ImportJob.id)))
    total = count_result.scalar() or 0

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [ImportJobOut.model_validate(j).model_dump() for j in items],
    }


# ── Export ─────────────────────────────────────────────────────────────

@router.get("/export/{object_type}")
async def export_csv(
    object_type: str,
    q: str = Query("", max_length=255),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """Export records as CSV."""
    model_class = EXPORT_MODELS.get(object_type)
    if not model_class:
        # Check if it's a custom object
        from app.models.custom_object import CustomObjectDef
        result = await db.execute(
            select(CustomObjectDef).where(CustomObjectDef.api_name == object_type)
        )
        obj_def = result.scalar_one_or_none()
        if obj_def:
            from app.services.custom_object_service import list_records
            records = await list_records(db, obj_def, page=1, page_size=10000)
            if records["items"]:
                csv_content = generate_csv(object_type, records["items"])
            else:
                csv_content = "No data"
            return PlainTextResponse(csv_content, media_type="text/csv",
                                     headers={"Content-Disposition": f"attachment; filename={object_type}.csv"})

        raise HTTPException(status_code=404, detail=f"Unknown object type: {object_type}")

    # Build query
    query = select(model_class)
    if q:
        if hasattr(model_class, "name"):
            query = query.where(model_class.name.ilike(f"%{q}%"))
    query = query.order_by(model_class.created_at.desc())

    result = await db.execute(query)
    records = result.scalars().all()

    # Convert to dicts for CSV generation
    record_dicts = []
    for r in records:
        d = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        record_dicts.append(d)

    csv_content = generate_csv(object_type, record_dicts)
    return PlainTextResponse(csv_content, media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={object_type}.csv"})