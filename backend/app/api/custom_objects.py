from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.custom_object import CustomObjectDef, CustomFieldDef
from app.models.auth import User
from app.schemas.custom_object import (
    ObjectDefCreate, ObjectDefUpdate, ObjectDefOut,
    FieldDefCreate, FieldDefOut,
    RecordData, RecordOut,
)
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services import custom_object_service as svc

router = APIRouter(prefix="/api/custom-objects", tags=["custom-objects"])


# ── Object Definition CRUD ──────────────────────────────────────────

@router.get("", response_model=list[ObjectDefOut])
async def list_objects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(CustomObjectDef)
        .options(selectinload(CustomObjectDef.fields))
        .order_by(CustomObjectDef.created_at)
    )
    return result.scalars().all()


@router.post("", response_model=ObjectDefOut, status_code=status.HTTP_201_CREATED)
async def create_object(
    payload: ObjectDefCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    fields = [f.model_dump() for f in payload.fields]
    # Convert picklist_values from list to JSON string
    for f in fields:
        if f.get("picklist_values") and isinstance(f["picklist_values"], list):
            import json
            f["picklist_values"] = json.dumps(f["picklist_values"])

    obj = await svc.create_object(
        db,
        api_name=payload.api_name,
        label=payload.label,
        plural_label=payload.plural_label,
        description=payload.description,
        fields=fields,
    )
    # Re-fetch with fields loaded for response
    result = await db.execute(
        select(CustomObjectDef)
        .options(selectinload(CustomObjectDef.fields))
        .where(CustomObjectDef.id == obj.id)
    )
    return result.scalar_one()


@router.get("/{obj_id}", response_model=ObjectDefOut)
async def get_object(
    obj_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(CustomObjectDef)
        .options(selectinload(CustomObjectDef.fields))
        .where(CustomObjectDef.id == obj_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj


@router.put("/{obj_id}", response_model=ObjectDefOut)
async def update_object(
    obj_id: str,
    payload: ObjectDefUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    obj = await svc.get_object_by_id(db, obj_id)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_object(
    obj_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    await svc.delete_object(db, obj_id)


# ── Field Definition Management ─────────────────────────────────────

@router.post("/{obj_id}/fields", response_model=FieldDefOut, status_code=status.HTTP_201_CREATED)
async def add_field(
    obj_id: str,
    payload: FieldDefCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    field_data = payload.model_dump()
    if field_data.get("picklist_values") and isinstance(field_data["picklist_values"], list):
        import json
        field_data["picklist_values"] = json.dumps(field_data["picklist_values"])
    field = await svc.add_field(db, obj_id, field_data)
    return field


@router.delete("/{obj_id}/fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field(
    obj_id: str,
    field_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    await svc.delete_field(db, obj_id, field_id)


# ── Record CRUD (via object ID) ─────────────────────────────────────

@router.get("/{obj_id}/records")
async def list_records(
    obj_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    obj = await svc.get_object_by_id(db, obj_id)
    items, total = await svc.list_records(db, obj, page=page, page_size=page_size)
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.post("/{obj_id}/records", status_code=status.HTTP_201_CREATED)
async def create_record(
    obj_id: str,
    payload: RecordData,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    obj = await svc.get_object_by_id(db, obj_id)
    record = await svc.create_record(db, obj, payload.fields, owner_id=current_user.id)
    return record


@router.get("/{obj_id}/records/{record_id}")
async def get_record(
    obj_id: str,
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    obj = await svc.get_object_by_id(db, obj_id)
    return await svc.get_record(db, obj, record_id)


@router.put("/{obj_id}/records/{record_id}")
async def update_record(
    obj_id: str,
    record_id: int,
    payload: RecordData,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    obj = await svc.get_object_by_id(db, obj_id)
    return await svc.update_record(db, obj, record_id, payload.fields)


@router.delete("/{obj_id}/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    obj_id: str,
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    obj = await svc.get_object_by_id(db, obj_id)
    await svc.delete_record(db, obj, record_id)


# ── Universal API (by object API name) ──────────────────────────────

@router.get("/by-name/{api_name}/records")
async def list_records_by_name(
    api_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    obj = await svc.get_object_by_name(db, api_name)
    items, total = await svc.list_records(db, obj, page=page, page_size=page_size)
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.post("/by-name/{api_name}/records", status_code=status.HTTP_201_CREATED)
async def create_record_by_name(
    api_name: str,
    payload: RecordData,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    obj = await svc.get_object_by_name(db, api_name)
    return await svc.create_record(db, obj, payload.fields, owner_id=current_user.id)


@router.get("/by-name/{api_name}/records/{record_id}")
async def get_record_by_name(
    api_name: str,
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    obj = await svc.get_object_by_name(db, api_name)
    return await svc.get_record(db, obj, record_id)


@router.put("/by-name/{api_name}/records/{record_id}")
async def update_record_by_name(
    api_name: str,
    record_id: int,
    payload: RecordData,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    obj = await svc.get_object_by_name(db, api_name)
    return await svc.update_record(db, obj, record_id, payload.fields)


@router.delete("/by-name/{api_name}/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record_by_name(
    api_name: str,
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    obj = await svc.get_object_by_name(db, api_name)
    await svc.delete_record(db, obj, record_id)