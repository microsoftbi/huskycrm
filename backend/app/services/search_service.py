"""
Search service using SQLite FTS5 for full-text search across all objects.
"""
from sqlalchemy import text, select, or_
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
from app.models.crm import Account, Contact, Opportunity, Product
from app.models.event import Event


FTS5_TABLE = "search_idx"

# SQL to create the FTS5 virtual table
CREATE_FTS5_SQL = f"""
CREATE VIRTUAL TABLE IF NOT EXISTS {FTS5_TABLE} USING fts5(
    object_type, object_id, name, content,
    tokenize='unicode61'
);
"""

# Triggers for core objects
TRIGGERS = {
    "accounts": {
        "table": "accounts",
        "object_type": "account",
        "name_col": "name",
        "content_cols": "COALESCE(name, '') || ' ' || COALESCE(industry, '') || ' ' || COALESCE(email, '')",
        "id_col": "id",
    },
    "contacts": {
        "table": "contacts",
        "object_type": "contact",
        "name_col": "first_name || ' ' || last_name",
        "content_cols": "COALESCE(first_name, '') || ' ' || COALESCE(last_name, '') || ' ' || COALESCE(email, '')",
        "id_col": "id",
    },
    "opportunities": {
        "table": "opportunities",
        "object_type": "opportunity",
        "name_col": "name",
        "content_cols": "COALESCE(name, '') || ' ' || COALESCE(description, '')",
        "id_col": "id",
    },
    "products": {
        "table": "products",
        "object_type": "product",
        "name_col": "name",
        "content_cols": "COALESCE(name, '') || ' ' || COALESCE(product_code, '') || ' ' || COALESCE(description, '')",
        "id_col": "id",
    },
    "events": {
        "table": "events",
        "object_type": "event",
        "name_col": "subject",
        "content_cols": "COALESCE(subject, '') || ' ' || COALESCE(purpose, '')",
        "id_col": "id",
    },
}


async def setup_fts5(conn: AsyncConnection):
    """Create the FTS5 table and triggers."""
    await conn.execute(text(CREATE_FTS5_SQL))

    for key, cfg in TRIGGERS.items():
        # Insert trigger
        await conn.execute(text(f"""
            CREATE TRIGGER IF NOT EXISTS trg_{key}_fts_insert AFTER INSERT ON {cfg['table']}
            BEGIN
                INSERT INTO {FTS5_TABLE} (object_type, object_id, name, content)
                VALUES ('{cfg['object_type']}', NEW.{cfg['id_col']}, {cfg['name_col']}, {cfg['content_cols']});
            END;
        """))
        # Update trigger
        await conn.execute(text(f"""
            CREATE TRIGGER IF NOT EXISTS trg_{key}_fts_update AFTER UPDATE ON {cfg['table']}
            BEGIN
                UPDATE {FTS5_TABLE} SET
                    name = {cfg['name_col']},
                    content = {cfg['content_cols']}
                WHERE object_id = NEW.{cfg['id_col']} AND object_type = '{cfg['object_type']}';
            END;
        """))
        # Delete trigger
        await conn.execute(text(f"""
            CREATE TRIGGER IF NOT EXISTS trg_{key}_fts_delete AFTER DELETE ON {cfg['table']}
            BEGIN
                DELETE FROM {FTS5_TABLE} WHERE object_id = OLD.{cfg['id_col']} AND object_type = '{cfg['object_type']}';
            END;
        """))


async def search_all(db: AsyncSession, query: str, limit: int = 5) -> dict:
    """Search across all indexed objects and return grouped results."""
    if not query or len(query.strip()) < 1:
        return {}

    search_term = query.strip()
    results = {
        "accounts": [],
        "contacts": [],
        "opportunities": [],
        "products": [],
        "events": [],
        "custom_objects": {},
    }

    # Search using FTS5
    fts_query = f"\"{search_term}\" OR {search_term}*"
    sql = text(f"""
        SELECT object_type, object_id, name, content
        FROM {FTS5_TABLE}
        WHERE {FTS5_TABLE} MATCH :q
        ORDER BY rank
        LIMIT :lim
    """)
    try:
        result = await db.execute(sql, {"q": fts_query, "lim": limit * 10})
        rows = result.fetchall()
    except Exception:
        # Fallback to LIKE search if FTS5 fails
        return await _search_like_fallback(db, search_term, limit)

    # Group by object_type
    for row in rows:
        obj_type = row[0]
        obj_id = row[1]
        name = row[2]

        if obj_type == "account" and len(results["accounts"]) < limit:
            results["accounts"].append({"id": obj_id, "name": name})
        elif obj_type == "contact" and len(results["contacts"]) < limit:
            results["contacts"].append({"id": obj_id, "name": name})
        elif obj_type == "opportunity" and len(results["opportunities"]) < limit:
            results["opportunities"].append({"id": obj_id, "name": name})
        elif obj_type == "product" and len(results["products"]) < limit:
            results["products"].append({"id": obj_id, "name": name})
        elif obj_type == "event" and len(results["events"]) < limit:
            results["events"].append({"id": obj_id, "name": name})

    return results


async def _search_like_fallback(db: AsyncSession, query: str, limit: int) -> dict:
    """Fallback to LIKE search for all objects."""
    results = {"accounts": [], "contacts": [], "opportunities": [], "products": [], "events": [], "custom_objects": {}}
    q = f"%{query}%"

    # Accounts
    result = await db.execute(select(Account).where(Account.name.ilike(q)).limit(limit))
    for a in result.scalars().all():
        results["accounts"].append({"id": a.id, "name": a.name})

    # Contacts
    result = await db.execute(
        select(Contact).where(or_(Contact.first_name.ilike(q), Contact.last_name.ilike(q), Contact.email.ilike(q))).limit(limit)
    )
    for c in result.scalars().all():
        results["contacts"].append({"id": c.id, "name": f"{c.first_name} {c.last_name}"})

    # Opportunities
    result = await db.execute(select(Opportunity).where(Opportunity.name.ilike(q)).limit(limit))
    for o in result.scalars().all():
        results["opportunities"].append({"id": o.id, "name": o.name})

    # Products
    result = await db.execute(select(Product).where(Product.name.ilike(q)).limit(limit))
    for p in result.scalars().all():
        results["products"].append({"id": p.id, "name": p.name})

    # Events
    result = await db.execute(select(Event).where(Event.subject.ilike(q)).limit(limit))
    for e in result.scalars().all():
        results["events"].append({"id": e.id, "name": e.subject})

    return results