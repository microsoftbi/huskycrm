"""
Report execution service.

Executes saved report definitions against both standard and custom objects,
handling filtering, aggregation, and grouping dynamically.
"""
import json
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm import Account, Contact, Opportunity
from app.models.custom_object import CustomObjectDef, CustomFieldDef
from app.schemas.report import ReportResult


# ── Standard object field maps ────────────────────────────────────

STANDARD_OBJECTS = {
    "account": {
        "table": "accounts",
        "model": Account,
        "fields": ["id", "name", "industry", "phone", "email", "website",
                    "billing_city", "billing_state", "billing_country",
                    "owner_id", "created_at"],
    },
    "contact": {
        "table": "contacts",
        "model": Contact,
        "fields": ["id", "first_name", "last_name", "email", "phone",
                    "title", "department", "account_id", "owner_id", "created_at"],
    },
    "opportunity": {
        "table": "opportunities",
        "model": Opportunity,
        "fields": ["id", "name", "amount", "stage_id", "probability",
                    "close_date", "account_id", "owner_id", "created_at"],
    },
}


async def execute_report(
    db: AsyncSession,
    object_type: str,
    report_type: str = "tabular",
    filters: list[dict] | None = None,
    grouping: list[str] | None = None,
    aggregations: list[dict] | None = None,
    columns: list[str] | None = None,
    page: int = 1,
    page_size: int = 100,
) -> ReportResult:
    """Execute a report and return results."""
    # Check if it's a standard or custom object
    if object_type in STANDARD_OBJECTS:
        return await _execute_standard_report(
            db, object_type, report_type, filters, grouping, aggregations, columns, page, page_size
        )
    else:
        return await _execute_custom_report(
            db, object_type, report_type, filters, grouping, aggregations, columns, page, page_size
        )


async def _execute_standard_report(
    db: AsyncSession, object_type: str, report_type: str,
    filters: list[dict] | None, grouping: list[str] | None,
    aggregations: list[dict] | None, columns: list[str] | None,
    page: int, page_size: int,
) -> ReportResult:
    """Execute a report on a standard object."""
    obj_info = STANDARD_OBJECTS[object_type]
    table = obj_info["table"]
    all_fields = obj_info["fields"]

    display_cols = columns or all_fields[:6]
    safe_cols = [c for c in display_cols if c in all_fields]

    # Build WHERE clause
    where_clauses = []
    params = {}
    if filters:
        for i, f in enumerate(filters):
            field = f.get("field")
            op = f.get("operator", "eq")
            val = f.get("value")
            if field in all_fields and val is not None:
                pname = f"p{i}"
                if op == "eq":
                    where_clauses.append(f"{field} = :{pname}")
                elif op == "gt":
                    where_clauses.append(f"{field} > :{pname}")
                elif op == "gte":
                    where_clauses.append(f"{field} >= :{pname}")
                elif op == "lt":
                    where_clauses.append(f"{field} < :{pname}")
                elif op == "lte":
                    where_clauses.append(f"{field} <= :{pname}")
                elif op == "contains":
                    where_clauses.append(f"{field} LIKE :{pname}")
                    val = f"%{val}%"
                params[pname] = val

    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Count
    count_sql = f"SELECT COUNT(*) as cnt FROM {table}{where_sql}"
    count_result = await db.execute(text(count_sql), params)
    total = count_result.fetchone()[0]

    if report_type == "summary" and grouping:
        # GROUP BY query
        group_cols = [c for c in grouping if c in all_fields]
        agg_cols = []
        for agg in (aggregations or []):
            field = agg.get("field")
            func_name = agg.get("function", "SUM")
            if field in all_fields:
                agg_cols.append(f"{func_name}({field}) as {func_name}_{field}")

        if group_cols and agg_cols:
            sql = f"SELECT {', '.join(group_cols + agg_cols)} FROM {table}{where_sql} GROUP BY {', '.join(group_cols)}"
            result = await db.execute(text(sql), params)
            rows = result.fetchall()
            keys = result.keys()
            return ReportResult(
                columns=list(keys),
                rows=[list(row) for row in rows],
                total=total,
            )

    # Tabular: SELECT with LIMIT
    safe_cols_str = ", ".join(safe_cols)
    sql = f"SELECT {safe_cols_str} FROM {table}{where_sql} ORDER BY id DESC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = (page - 1) * page_size

    result = await db.execute(text(sql), params)
    rows = result.fetchall()
    return ReportResult(
        columns=safe_cols,
        rows=[list(row) for row in rows],
        total=total,
    )


async def _execute_custom_report(
    db: AsyncSession, object_type: str, report_type: str,
    filters: list[dict] | None, grouping: list[dict] | None,
    aggregations: list[dict] | None, columns: list[str] | None,
    page: int, page_size: int,
) -> ReportResult:
    """Execute a report on a custom object."""
    # Get object definition
    result = await db.execute(
        select(CustomObjectDef).where(CustomObjectDef.api_name == object_type)
    )
    obj_def = result.scalar_one_or_none()
    if not obj_def:
        return ReportResult(columns=[], rows=[], total=0)

    # Get field definitions
    field_result = await db.execute(
        select(CustomFieldDef)
        .where(CustomFieldDef.object_id == obj_def.id)
        .order_by(CustomFieldDef.display_order)
    )
    field_defs = field_result.scalars().all()
    field_map = {f.api_name: f for f in field_defs}

    display_cols = columns or [f.api_name for f in field_defs[:6]]
    safe_cols = [f"f_{c}" for c in display_cols if c in field_map]
    display_names = [f"f_{c}" for c in display_cols if c in field_map]

    # Build WHERE clause
    where_clauses = []
    params = {}
    if filters:
        for i, f in enumerate(filters):
            field = f.get("field")
            op = f.get("operator", "eq")
            val = f.get("value")
            col = f"f_{field}"
            if field in field_map and val is not None:
                pname = f"p{i}"
                if op == "eq":
                    where_clauses.append(f"{col} = :{pname}")
                elif op == "gt":
                    where_clauses.append(f"{col} > :{pname}")
                elif op == "contains":
                    where_clauses.append(f"{col} LIKE :{pname}")
                    val = f"%{val}%"
                params[pname] = val

    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Count
    count_sql = f"SELECT COUNT(*) as cnt FROM {obj_def.table_name}{where_sql}"
    count_result = await db.execute(text(count_sql), params)
    total = count_result.fetchone()[0]

    # Select
    safe_cols_str = ", ".join(safe_cols)
    sql = f"SELECT {safe_cols_str} FROM {obj_def.table_name}{where_sql} ORDER BY id DESC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = (page - 1) * page_size

    result = await db.execute(text(sql), params)
    rows = result.fetchall()
    return ReportResult(
        columns=display_cols,
        rows=[list(row) for row in rows],
        total=total,
    )