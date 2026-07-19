import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.report import Report, Dashboard, DashboardComponent
from app.models.auth import User
from app.schemas.report import (
    ReportCreate, ReportUpdate, ReportOut, ReportResult,
    DashboardCreate, DashboardOut, DashboardComponentBase, DashboardComponentOut,
)
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services import report_service as rsvc

router = APIRouter(prefix="/api/reports", tags=["reports"])
dashboard_router = APIRouter(prefix="/api/dashboards", tags=["dashboards"])


# ── Reports ─────────────────────────────────────────────────────────

@router.get("", response_model=list[ReportOut])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Report).order_by(Report.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    report = Report(
        name=payload.name,
        object_type=payload.object_type,
        report_type=payload.report_type,
        filters=json.dumps(payload.filters) if payload.filters else None,
        grouping=json.dumps(payload.grouping) if payload.grouping else None,
        aggregations=json.dumps(payload.aggregations) if payload.aggregations else None,
        columns=json.dumps(payload.columns) if payload.columns else None,
        owner_id=current_user.id,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/{report_id}", response_model=ReportOut)
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put("/{report_id}", response_model=ReportOut)
async def update_report(
    report_id: str,
    payload: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key in ["filters", "grouping", "aggregations", "columns"]:
        if key in update_data:
            update_data[key] = json.dumps(update_data[key]) if update_data[key] else None

    for key, value in update_data.items():
        setattr(report, key, value)

    await db.commit()
    await db.refresh(report)
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    await db.delete(report)
    await db.commit()


@router.post("/{report_id}/run", response_model=ReportResult)
async def run_report(
    report_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    filters = json.loads(report.filters) if report.filters else None
    grouping = json.loads(report.grouping) if report.grouping else None
    aggregations = json.loads(report.aggregations) if report.aggregations else None
    columns = json.loads(report.columns) if report.columns else None

    return await rsvc.execute_report(
        db, report.object_type, report.report_type,
        filters, grouping, aggregations, columns,
        page, page_size,
    )


# ── Dashboards ──────────────────────────────────────────────────────

@dashboard_router.get("", response_model=list[DashboardOut])
async def list_dashboards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Dashboard)
        .options(selectinload(Dashboard.components))
        .order_by(Dashboard.created_at.desc())
    )
    return result.scalars().all()


@dashboard_router.post("", response_model=DashboardOut, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    payload: DashboardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    dash = Dashboard(name=payload.name, owner_id=current_user.id)
    db.add(dash)
    await db.commit()
    await db.refresh(dash)
    # Reload with empty components
    result = await db.execute(
        select(Dashboard)
        .options(selectinload(Dashboard.components))
        .where(Dashboard.id == dash.id)
    )
    return result.scalar_one()


@dashboard_router.get("/{dashboard_id}", response_model=DashboardOut)
async def get_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Dashboard)
        .options(selectinload(Dashboard.components))
        .where(Dashboard.id == dashboard_id)
    )
    dash = result.scalar_one_or_none()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dash


@dashboard_router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dash = result.scalar_one_or_none()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    await db.delete(dash)
    await db.commit()


@dashboard_router.post("/{dashboard_id}/components", response_model=DashboardComponentOut)
async def add_component(
    dashboard_id: str,
    payload: DashboardComponentBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dash = result.scalar_one_or_none()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    comp = DashboardComponent(dashboard_id=dashboard_id, **payload.model_dump())
    db.add(comp)
    await db.commit()
    await db.refresh(comp)
    return comp


@dashboard_router.delete("/{dashboard_id}/components/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_component(
    dashboard_id: str,
    component_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(
        select(DashboardComponent).where(
            DashboardComponent.id == component_id,
            DashboardComponent.dashboard_id == dashboard_id,
        )
    )
    comp = result.scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")
    await db.delete(comp)
    await db.commit()
