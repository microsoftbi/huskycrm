"""
CSV parsing and field mapping service for import/export.
"""
import csv
import io
import json
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.crm import Account, Contact, Product, Opportunity


# Object field definitions: {api_name: {label, type, required}}
OBJECT_FIELDS = {
    "account": {
        "name": {"label": "名称", "type": "text", "required": True},
        "industry": {"label": "行业", "type": "text", "required": False},
        "phone": {"label": "电话", "type": "text", "required": False},
        "website": {"label": "网站", "type": "text", "required": False},
        "email": {"label": "邮箱", "type": "text", "required": False},
        "billing_street": {"label": "街道", "type": "text", "required": False},
        "billing_city": {"label": "城市", "type": "text", "required": False},
        "billing_state": {"label": "省份", "type": "text", "required": False},
        "billing_postal_code": {"label": "邮编", "type": "text", "required": False},
        "billing_country": {"label": "国家", "type": "text", "required": False},
        "description": {"label": "描述", "type": "text", "required": False},
    },
    "contact": {
        "first_name": {"label": "名", "type": "text", "required": True},
        "last_name": {"label": "姓", "type": "text", "required": True},
        "email": {"label": "邮箱", "type": "text", "required": False},
        "phone": {"label": "电话", "type": "text", "required": False},
        "mobile": {"label": "手机", "type": "text", "required": False},
        "title": {"label": "职位", "type": "text", "required": False},
        "department": {"label": "部门", "type": "text", "required": False},
    },
    "product": {
        "name": {"label": "产品名称", "type": "text", "required": True},
        "product_code": {"label": "产品编码", "type": "text", "required": False},
        "category": {"label": "分类", "type": "text", "required": False},
        "standard_price": {"label": "标准价格", "type": "number", "required": True},
        "cost": {"label": "成本", "type": "number", "required": False},
        "description": {"label": "描述", "type": "text", "required": False},
        "is_active": {"label": "是否启用", "type": "boolean", "required": False},
    },
    "opportunity": {
        "name": {"label": "机会名称", "type": "text", "required": True},
        "amount": {"label": "金额", "type": "number", "required": False},
        "close_date": {"label": "预计关闭日期", "type": "date", "required": False},
        "description": {"label": "描述", "type": "text", "required": False},
    },
}

# Model class mapping for import
IMPORT_MODELS = {
    "account": Account,
    "contact": Contact,
    "product": Product,
    "opportunity": Opportunity,
}

# Auto-mapping: common Chinese column names -> field names
AUTO_MAP = {
    "名称": "name", "姓名": "name", "账户名称": "name",
    "行业": "industry", "电话": "phone", "网站": "website",
    "邮箱": "email", "街道": "billing_street", "城市": "billing_city",
    "省份": "billing_state", "邮编": "billing_postal_code", "国家": "billing_country",
    "描述": "description", "名": "first_name", "姓": "last_name",
    "手机": "mobile", "职位": "title", "部门": "department",
    "产品名称": "name", "产品编码": "product_code", "分类": "category",
    "标准价格": "standard_price", "成本": "cost",
    "机会名称": "name", "金额": "amount", "预计关闭日期": "close_date",
    "是否启用": "is_active",
}

# Store preview data in memory (keyed by preview_id)
_preview_store: dict[str, dict] = {}


def parse_csv(content: bytes) -> tuple[list[str], list[list[str]]]:
    """Parse CSV content and return (headers, rows)."""
    text = content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise ValueError("Empty CSV file")
    headers = [h.strip() for h in rows[0]]
    data_rows = [[cell.strip() for cell in row] for row in rows[1:] if any(cell.strip() for cell in row)]
    return headers, data_rows


def auto_map_fields(headers: list[str], object_type: str) -> dict[str, str | None]:
    """Auto-map CSV column headers to field names."""
    fields = OBJECT_FIELDS.get(object_type, {})
    mapping = {}
    for header in headers:
        # Try exact match
        if header in AUTO_MAP:
            field = AUTO_MAP[header]
            if field in fields:
                mapping[header] = field
                continue
        # Try label match
        for field_name, field_def in fields.items():
            if field_def["label"] == header:
                mapping[header] = field_name
                break
        else:
            mapping[header] = None
    return mapping


def create_preview(headers: list[str], rows: list[list[str]], object_type: str) -> dict:
    """Create a preview and store it for later confirmation."""
    mapping = auto_map_fields(headers, object_type)
    fields = OBJECT_FIELDS.get(object_type, {})
    available = [{"name": k, "label": v["label"], "type": v["type"], "required": v["required"]}
                 for k, v in fields.items()]

    preview_id = str(uuid.uuid4())[:8]
    _preview_store[preview_id] = {
        "object_type": object_type,
        "headers": headers,
        "rows": rows,
        "mapping": mapping,
    }

    return {
        "preview_id": preview_id,
        "columns": headers,
        "mapping_suggestions": mapping,
        "available_fields": available,
        "preview_rows": rows[:10],
    }


async def confirm_import(db: AsyncSession, preview_id: str, mapping: dict[str, str], user_id: str) -> dict:
    """Execute the import with confirmed field mapping."""
    preview = _preview_store.get(preview_id)
    if not preview:
        raise ValueError("Preview not found or expired")

    object_type = preview["object_type"]
    headers = preview["headers"]
    rows = preview["rows"]
    model_class = IMPORT_MODELS.get(object_type)
    if not model_class:
        raise ValueError(f"Unknown object type: {object_type}")

    fields = OBJECT_FIELDS.get(object_type, {})
    success_rows = 0
    error_rows = 0
    errors = []

    for row_idx, row in enumerate(rows):
        try:
            record_data = {}
            for col_idx, header in enumerate(headers):
                field_name = mapping.get(header)
                if field_name and col_idx < len(row):
                    value = row[col_idx].strip()
                    if value:
                        field_def = fields.get(field_name, {})
                        if field_def.get("type") == "number":
                            try:
                                value = float(value)
                            except ValueError:
                                pass
                        elif field_def.get("type") == "boolean":
                            value = value.lower() in ("true", "yes", "是", "1", "active")
                        record_data[field_name] = value

            # Check required fields
            missing = [f_name for f_name, f_def in fields.items()
                       if f_def.get("required") and f_name not in record_data]
            if missing:
                raise ValueError(f"Missing required fields: {', '.join(missing)}")

            record = model_class(**record_data)
            db.add(record)
            success_rows += 1
        except Exception as e:
            error_rows += 1
            errors.append({"row": row_idx + 2, "error": str(e)})

    if success_rows > 0:
        await db.commit()

    # Clean up preview
    _preview_store.pop(preview_id, None)

    return {
        "success_rows": success_rows,
        "error_rows": error_rows,
        "errors": errors,
    }


def generate_csv(object_type: str, records: list[dict]) -> str:
    """Generate CSV content from a list of record dicts."""
    fields = OBJECT_FIELDS.get(object_type, {})
    if not fields:
        fields = {k: {"label": k} for k in (records[0].keys() if records else [])}

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    headers = [f["label"] for f in fields.values()]
    writer.writerow(headers)

    # Data rows
    for record in records:
        row = [str(record.get(f_name, "") or "") for f_name in fields.keys()]
        writer.writerow(row)

    return output.getvalue()