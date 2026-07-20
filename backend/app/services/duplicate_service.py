"""
Duplicate detection service — checks for duplicate records based on matching rules.
"""
import json
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.duplicate_rule import DuplicateRule
from app.models.crm import Account, Contact


# Map object types to models
DUPLICATE_MODELS = {
    "account": Account,
    "contact": Contact,
}


async def check_duplicates(
    db: AsyncSession,
    object_type: str,
    record_data: dict,
    exclude_id: str | None = None,
) -> list[dict]:
    """
    Check a record for duplicates against active rules.
    Returns a list of duplicate matches.
    Each match: {"id": str, "name": str, "matched_fields": [str]}
    """
    model = DUPLICATE_MODELS.get(object_type)
    if not model:
        return []

    # Get active rules for this object type
    result = await db.execute(
        select(DuplicateRule).where(
            DuplicateRule.object_type == object_type,
            DuplicateRule.is_active == True,
        )
    )
    rules = result.scalars().all()

    if not rules:
        return []

    matches = []
    seen_ids = set()

    for rule in rules:
        fields = json.loads(rule.matching_fields) if rule.matching_fields else []

        # Build query: find records where ANY of the matching fields match
        conditions = []
        for field_name in fields:
            value = record_data.get(field_name)
            if not value or not str(value).strip():
                continue

            field = getattr(model, field_name, None)
            if field is not None:
                conditions.append(field.ilike(f"%{str(value).strip()}%"))

        if not conditions:
            continue

        query = select(model).where(model.is_deleted == False, or_(*conditions))
        if exclude_id:
            query = query.where(model.id != exclude_id)

        result = await db.execute(query)
        records = result.scalars().all()

        for record in records:
            if record.id in seen_ids:
                continue
            seen_ids.add(record.id)

            # Determine which fields matched
            matched_fields = []
            for field_name in fields:
                value = record_data.get(field_name)
                if not value:
                    continue
                rv = getattr(record, field_name, None)
                if rv and str(value).strip().lower() in str(rv).lower():
                    matched_fields.append(field_name)

            if object_type == "contact":
                name = f"{record.first_name} {record.last_name}"
            else:
                name = getattr(record, "name", "")

            matches.append({
                "id": record.id,
                "name": name,
                "matched_fields": matched_fields,
            })

    return matches


async def merge_records(
    db: AsyncSession,
    object_type: str,
    master_id: str,
    slave_id: str,
) -> dict:
    """
    Merge two records. The slave record is soft-deleted after merging.
    Fields from the slave fill in empty fields on the master.
    """
    model = DUPLICATE_MODELS.get(object_type)
    if not model:
        raise ValueError(f"Unsupported object type: {object_type}")

    master = await db.execute(select(model).where(model.id == master_id, model.is_deleted == False))
    master = master.scalar_one_or_none()
    if not master:
        raise ValueError("Master record not found")

    slave = await db.execute(select(model).where(model.id == slave_id, model.is_deleted == False))
    slave = slave.scalar_one_or_none()
    if not slave:
        raise ValueError("Slave record not found")

    # Merge: fill empty fields on master with slave's values
    for column in model.__table__.columns:
        col_name = column.name
        if col_name in ("id", "created_at", "updated_at", "is_deleted", "deleted_at", "owner_id"):
            continue
        master_value = getattr(master, col_name, None)
        slave_value = getattr(slave, col_name, None)
        if not master_value and slave_value:
            setattr(master, col_name, slave_value)

    # Soft-delete the slave
    from datetime import datetime
    slave.is_deleted = True
    slave.deleted_at = datetime.now()

    await db.commit()

    return {
        "master_id": master_id,
        "slave_id": slave_id,
        "object_type": object_type,
        "message": "记录已合并",
    }