"""
Dynamic DDL utilities for custom objects engine.

Each custom object gets a real SQLite table (e.g. `obj_1`).
Fields become typed columns. Table and column names are validated
against metadata to prevent SQL injection.

Uses named parameters (:p0, :p1, ...) for SQL parameter binding
to work correctly with SQLAlchemy async mode.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

FIELD_TYPE_MAP = {
    "text": "VARCHAR(255)", "textarea": "TEXT", "number": "FLOAT",
    "integer": "INTEGER", "boolean": "BOOLEAN", "date": "DATE",
    "datetime": "DATETIME", "email": "VARCHAR(255)", "phone": "VARCHAR(50)",
    "url": "VARCHAR(500)", "picklist": "VARCHAR(100)", "lookup": "INTEGER",
}

SYSTEM_COLUMNS = {"id", "created_at", "updated_at", "owner_id"}


def validate_table_name(name: str) -> bool:
    return name.startswith("obj_") and name.replace("_", "").isalnum()


def validate_column_name(name: str) -> bool:
    return name.replace("_", "").isalnum()


def validate_field_type(ftype: str) -> bool:
    return ftype in FIELD_TYPE_MAP


def _params_to_dict(params: list) -> dict:
    """Convert a positional params list to a named-params dict (:p0, :p1, ...)."""
    return {f"p{i}": v for i, v in enumerate(params)}


def _replace_placeholders(sql: str) -> str:
    """Replace ? with :p0, :p1, etc. Must be called BEFORE building the param dict."""
    return sql


def build_create_table_sql(table_name: str, fields: list[dict]) -> str:
    if not validate_table_name(table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    columns = [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "record_id TEXT UNIQUE NOT NULL DEFAULT (lower(hex(randomblob(16))))",
        "owner_id INTEGER REFERENCES users(id)",
    ]
    for field in fields:
        col_name = f"f_{field['api_name']}"
        if not validate_column_name(col_name):
            raise ValueError(f"Invalid column name: {col_name}")
        col_type = FIELD_TYPE_MAP.get(field["field_type"], "VARCHAR(255)")
        constraints = []
        if field.get("is_required"):
            constraints.append("NOT NULL")
        if field.get("is_unique"):
            constraints.append("UNIQUE")
        if field.get("default_value") is not None:
            constraints.append(f"DEFAULT '{field['default_value']}'")
        columns.append(f"{col_name} {col_type} {' '.join(constraints)}".strip())
    columns.append("created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
    columns.append("updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
    return f"CREATE TABLE {table_name} ({', '.join(columns)})"


def build_add_column_sql(table_name: str, field: dict) -> str:
    if not validate_table_name(table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    col_name = f"f_{field['api_name']}"
    if not validate_column_name(col_name):
        raise ValueError(f"Invalid column name: {col_name}")
    if not validate_field_type(field["field_type"]):
        raise ValueError(f"Invalid field type: {field['field_type']}")
    col_type = FIELD_TYPE_MAP[field["field_type"]]
    constraints = []
    if field.get("is_required"):
        constraints.append("NOT NULL")
    if field.get("default_value") is not None:
        constraints.append(f"DEFAULT '{field['default_value']}'")
    return f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type} {' '.join(constraints)}".strip()


def build_drop_column_sql(table_name: str, field_api_name: str) -> str:
    col_name = f"f_{field_api_name}"
    if not validate_column_name(col_name) or not validate_table_name(table_name):
        raise ValueError("Invalid name")
    return f"ALTER TABLE {table_name} DROP COLUMN {col_name}"


def _build_where_clause(filters: dict | None) -> tuple[str, list]:
    if not filters:
        return "", []
    clauses = []
    params = []
    for key, value in filters.items():
        col = f"f_{key}"
        if validate_column_name(col) and value is not None:
            clauses.append(f"{col} = :p{len(params)}")
            params.append(value)
    if clauses:
        return " WHERE " + " AND ".join(clauses), params
    return "", []


def build_select_sql(
    table_name: str, field_names: list[str], filters: dict | None = None,
    sort: str | None = None, sort_dir: str = "desc",
    page: int = 1, page_size: int = 20,
) -> tuple[str, dict]:
    """Build a SELECT query with named params. Returns (sql, params_dict)."""
    if not validate_table_name(table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    safe_cols = ["id", "record_id", "owner_id", "created_at", "updated_at"]
    for fname in field_names:
        cname = f"f_{fname}" if not fname.startswith("f_") else fname
        if validate_column_name(cname):
            safe_cols.append(cname)
    sql = f"SELECT {', '.join(safe_cols)} FROM {table_name}"
    where_clause, where_params = _build_where_clause(filters)
    sql += where_clause
    param_dict = _params_to_dict(where_params)
    next_idx = len(where_params)

    if sort:
        col = f"f_{sort}" if not sort.startswith("f_") and sort not in SYSTEM_COLUMNS else sort
        if validate_column_name(col) or col in SYSTEM_COLUMNS:
            dir_sql = "ASC" if sort_dir.lower() == "asc" else "DESC"
            sql += f" ORDER BY {col} {dir_sql}"
    else:
        sql += " ORDER BY id DESC"

    sql += f" LIMIT :p{next_idx} OFFSET :p{next_idx + 1}"
    param_dict[f"p{next_idx}"] = page_size
    param_dict[f"p{next_idx + 1}"] = (page - 1) * page_size
    return sql, param_dict


def build_insert_sql(table_name: str, field_names: list[str]) -> tuple[str, list]:
    """Build INSERT SQL. Returns (sql, field_names_list)."""
    if not validate_table_name(table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    cols = []
    placeholders = []
    for i, fname in enumerate(field_names):
        col = f"f_{fname}" if not fname.startswith("f_") else fname
        if validate_column_name(col):
            cols.append(col)
            placeholders.append(f":p{i}")
    return f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})", field_names


def build_update_sql(table_name: str, field_names: list[str]) -> tuple[str, list]:
    """Build UPDATE SQL. Returns (sql, field_names_list)."""
    if not validate_table_name(table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    set_clauses = []
    for i, fname in enumerate(field_names):
        col = f"f_{fname}" if not fname.startswith("f_") else fname
        if validate_column_name(col):
            set_clauses.append(f"{col} = :p{i}")
    set_clauses.append(f"updated_at = :p{len(field_names)}")
    field_names_with_updated = field_names + ["__updated_at"]
    return f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = :p{len(field_names) + 1}", field_names_with_updated


# ── Async execution helpers ─────────────────────────────────────────

async def execute_ddl(db: AsyncSession, sql: str):
    await db.execute(text(sql))
    await db.commit()


async def execute_query(db: AsyncSession, sql: str, params: dict | None = None):
    result = await db.execute(text(sql), params or {})
    rows = result.fetchall()
    if not rows:
        return []
    keys = result.keys()
    return [dict(zip(keys, row)) for row in rows]


async def execute_insert(db: AsyncSession, table_name: str, field_names: list, values: list) -> int:
    """Execute INSERT on a dynamic table with named params."""
    params = _params_to_dict(values)
    cols = [f"f_{fname}" if not fname.startswith("f_") else fname for fname in field_names]
    placeholders = ", ".join(f":p{i}" for i in range(len(field_names)))
    sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})"
    result = await db.execute(text(sql), params)
    await db.commit()
    return result.lastrowid


async def execute_update(db: AsyncSession, table_name: str, field_names: list, values: list, record_id: int):
    set_clauses = []
    params = {}
    for i, fname in enumerate(field_names):
        if fname == "__updated_at":
            continue
        col = f"f_{fname}" if not fname.startswith("f_") else fname
        if validate_column_name(col):
            set_clauses.append(f"{col} = :p{i}")
            params[f"p{i}"] = values[i]
    # Also update updated_at
    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    params[f"p{len(field_names)}"] = record_id
    sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = :p{len(field_names)}"
    await db.execute(text(sql), params)
    await db.commit()


async def execute_delete(db: AsyncSession, sql: str, params: dict | None = None):
    await db.execute(text(sql), params or {})
    await db.commit()


async def count_records(db: AsyncSession, table_name: str, filters: dict | None = None) -> int:
    if not validate_table_name(table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    sql = f"SELECT COUNT(*) as cnt FROM {table_name}"
    where_clause, where_params = _build_where_clause(filters)
    sql += where_clause
    params = _params_to_dict(where_params)
    result = await db.execute(text(sql), params)
    row = result.fetchone()
    return row[0] if row else 0