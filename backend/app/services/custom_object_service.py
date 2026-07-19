"""
Service layer for custom objects engine.

Coordinates between the metadata models (CustomObjectDef, CustomFieldDef)
and the dynamic DDL utilities to provide a clean API for managing
custom objects and their records.
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.custom_object import CustomObjectDef, CustomFieldDef
from app.utils import dynamic_ddl as ddl


# ── Object Definition Management ────────────────────────────────────

async def create_object(
    db: AsyncSession,
    api_name: str,
    label: str,
    plural_label: str | None = None,
    description: str | None = None,
    fields: list[dict] | None = None,
) -> CustomObjectDef:
    """Create a custom object definition, its dynamic table, and fields."""
    # Check for duplicate api_name
    existing = await db.execute(
        select(CustomObjectDef).where(CustomObjectDef.api_name == api_name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Object '{api_name}' already exists")

    fields = fields or []

    # Create metadata entry first (need the ID for table name)
    table_name = f"obj_{0}"  # placeholder, will update
    obj_def = CustomObjectDef(
        api_name=api_name,
        label=label,
        plural_label=plural_label or label,
        description=description,
        table_name=table_name,
    )
    db.add(obj_def)
    await db.flush()  # Get the ID

    # Update table name with actual ID
    obj_def.table_name = f"obj_{obj_def.id}"

    # Create the dynamic table
    ddl_sql = ddl.build_create_table_sql(obj_def.table_name, fields)
    await ddl.execute_ddl(db, ddl_sql)

    # Create field definitions
    field_objs = []
    for f in fields:
        field = CustomFieldDef(
            object_id=obj_def.id,
            api_name=f["api_name"],
            label=f["label"],
            field_type=f["field_type"],
            is_required=f.get("is_required", False),
            is_unique=f.get("is_unique", False),
            default_value=f.get("default_value"),
            max_length=f.get("max_length"),
            picklist_values=f.get("picklist_values"),
            precision_total=f.get("precision_total"),
            precision_scale=f.get("precision_scale"),
            lookup_object_id=f.get("lookup_object_id"),
            display_order=f.get("display_order", 0),
        )
        db.add(field)
        field_objs.append(field)

    await db.commit()
    await db.refresh(obj_def)
    return obj_def


async def delete_object(db: AsyncSession, obj_id: str):
    """Delete a custom object definition and its dynamic table."""
    result = await db.execute(
        select(CustomObjectDef).where(CustomObjectDef.id == obj_id)
    )
    obj_def = result.scalar_one_or_none()
    if not obj_def:
        raise HTTPException(status_code=404, detail="Object not found")

    # Drop the dynamic table
    await ddl.execute_ddl(db, f"DROP TABLE IF EXISTS {obj_def.table_name}")

    # Delete metadata (cascades to field defs)
    await db.delete(obj_def)
    await db.commit()


async def add_field(db: AsyncSession, obj_id: str, field_data: dict) -> CustomFieldDef:
    """Add a field to an existing custom object."""
    result = await db.execute(
        select(CustomObjectDef).where(CustomObjectDef.id == obj_id)
    )
    obj_def = result.scalar_one_or_none()
    if not obj_def:
        raise HTTPException(status_code=404, detail="Object not found")

    # Check for duplicate field name
    existing = await db.execute(
        select(CustomFieldDef).where(
            CustomFieldDef.object_id == obj_id,
            CustomFieldDef.api_name == field_data["api_name"],
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Field '{field_data['api_name']}' already exists")

    # ALTER TABLE to add the column
    alter_sql = ddl.build_add_column_sql(obj_def.table_name, field_data)
    await ddl.execute_ddl(db, alter_sql)

    # Create field def
    field = CustomFieldDef(
        object_id=obj_id,
        api_name=field_data["api_name"],
        label=field_data["label"],
        field_type=field_data["field_type"],
        is_required=field_data.get("is_required", False),
        is_unique=field_data.get("is_unique", False),
        default_value=field_data.get("default_value"),
        max_length=field_data.get("max_length"),
        picklist_values=field_data.get("picklist_values"),
        precision_total=field_data.get("precision_total"),
        precision_scale=field_data.get("precision_scale"),
        lookup_object_id=field_data.get("lookup_object_id"),
        display_order=field_data.get("display_order", 0),
    )
    db.add(field)
    await db.commit()
    await db.refresh(field)
    return field


async def delete_field(db: AsyncSession, obj_id: str, field_id: str):
    """Delete a field from a custom object."""
    result = await db.execute(
        select(CustomFieldDef).where(
            CustomFieldDef.id == field_id,
            CustomFieldDef.object_id == obj_id,
        )
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    obj_result = await db.execute(
        select(CustomObjectDef).where(CustomObjectDef.id == obj_id)
    )
    obj_def = obj_result.scalar_one_or_none()
    if not obj_def:
        raise HTTPException(status_code=404, detail="Object not found")

    # Drop the column
    drop_sql = ddl.build_drop_column_sql(obj_def.table_name, field.api_name)
    await ddl.execute_ddl(db, drop_sql)

    await db.delete(field)
    await db.commit()


# ── Record CRUD ─────────────────────────────────────────────────────

async def get_field_defs(db: AsyncSession, obj_id: str) -> list[CustomFieldDef]:
    """Get all field definitions for an object."""
    result = await db.execute(
        select(CustomFieldDef)
        .where(CustomFieldDef.object_id == obj_id)
        .order_by(CustomFieldDef.display_order)
    )
    return result.scalars().all()


async def get_object_by_name(db: AsyncSession, api_name: str) -> CustomObjectDef:
    """Get a custom object definition by its API name."""
    result = await db.execute(
        select(CustomObjectDef).where(CustomObjectDef.api_name == api_name)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Object '{api_name}' not found")
    return obj


async def get_object_by_id(db: AsyncSession, obj_id: str) -> CustomObjectDef:
    """Get a custom object definition by its ID."""
    result = await db.execute(
        select(CustomObjectDef).where(CustomObjectDef.id == obj_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj


async def list_records(
    db: AsyncSession, obj_def: CustomObjectDef,
    page: int = 1, page_size: int = 20,
    filters: dict | None = None,
    sort: str | None = None, sort_dir: str = "desc",
) -> tuple[list[dict], int]:
    """List records from a dynamic table with pagination."""
    field_defs = await get_field_defs(db, obj_def.id)
    field_api_names = [f.api_name for f in field_defs]

    # Count
    total = await ddl.count_records(db, obj_def.table_name, filters)

    # Select
    sql, params = ddl.build_select_sql(
        obj_def.table_name, field_api_names,
        filters=filters, sort=sort, sort_dir=sort_dir,
        page=page, page_size=page_size,
    )
    rows = await ddl.execute_query(db, sql, params)

    # Convert rows to structured format
    items = []
    for row in rows:
        fields = {}
        for fname in field_api_names:
            col = f"f_{fname}"
            if col in row:
                fields[fname] = row[col]
        items.append({
            "id": row["id"],
            "record_id": row.get("record_id", ""),
            "owner_id": row.get("owner_id"),
            "fields": fields,
            "created_at": str(row.get("created_at", "")),
            "updated_at": str(row.get("updated_at", "")),
        })

    return items, total


async def get_record(db: AsyncSession, obj_def: CustomObjectDef, record_id: int) -> dict:
    """Get a single record from a dynamic table."""
    field_defs = await get_field_defs(db, obj_def.id)
    field_api_names = [f.api_name for f in field_defs]

    sql, params = ddl.build_select_sql(
        obj_def.table_name, field_api_names,
        page=1, page_size=1,
    )
    # Override to filter by ID
    rows = await ddl.execute_query(
        db,
        f"SELECT * FROM {obj_def.table_name} WHERE id = :p0",
        {"p0": record_id},
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Record not found")

    row = rows[0]
    fields = {}
    for fname in field_api_names:
        col = f"f_{fname}"
        if col in row:
            fields[fname] = row[col]

    return {
        "id": row["id"],
        "record_id": row.get("record_id", ""),
        "owner_id": row.get("owner_id"),
        "fields": fields,
        "created_at": str(row.get("created_at", "")),
        "updated_at": str(row.get("updated_at", "")),
    }


async def create_record(
    db: AsyncSession, obj_def: CustomObjectDef, field_values: dict, owner_id: str | None = None,
) -> dict:
    """Create a record in a dynamic table."""
    field_defs = await get_field_defs(db, obj_def.id)
    field_map = {f.api_name: f for f in field_defs}

    # Validate required fields
    for f in field_defs:
        if f.is_required and f.api_name not in field_values:
            raise HTTPException(status_code=400, detail=f"Field '{f.label}' is required")

    # Build field values
    field_names = [k for k in field_values if k in field_map]
    field_params = [field_values[k] for k in field_names]

    # Build INSERT SQL
    row_id = await ddl.execute_insert(db, obj_def.table_name, field_names, field_params)

    return await get_record(db, obj_def, row_id)


async def update_record(
    db: AsyncSession, obj_def: CustomObjectDef, record_id: int, field_values: dict,
) -> dict:
    """Update a record in a dynamic table."""
    field_defs = await get_field_defs(db, obj_def.id)
    field_map = {f.api_name: f for f in field_defs}

    # Check record exists
    check = await ddl.execute_query(
        db, f"SELECT id FROM {obj_def.table_name} WHERE id = :p0", {"p0": record_id}
    )
    if not check:
        raise HTTPException(status_code=404, detail="Record not found")

    # Build field values
    field_names = [k for k in field_values if k in field_map]
    if not field_names:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    field_params = [field_values[k] for k in field_names]

    await ddl.execute_update(db, obj_def.table_name, field_names, field_params, record_id)

    return await get_record(db, obj_def, record_id)


async def delete_record(db: AsyncSession, obj_def: CustomObjectDef, record_id: int):
    """Delete a record from a dynamic table."""
    await ddl.execute_delete(db, f"DELETE FROM {obj_def.table_name} WHERE id = :p0", {"p0": record_id})