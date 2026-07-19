import pytest
import io
import csv
from app.services.csv_service import parse_csv, auto_map_fields, OBJECT_FIELDS


def test_parse_csv():
    content = "名称,行业,电话\n测试公司,Tech,13800138000\n"
    headers, rows = parse_csv(content.encode("utf-8"))
    assert headers == ["名称", "行业", "电话"]
    assert len(rows) == 1
    assert rows[0] == ["测试公司", "Tech", "13800138000"]


def test_parse_csv_utf8_bom():
    """CSV with UTF-8 BOM should be handled correctly."""
    content = "名称,行业\n测试公司,Tech\n"
    # Encode with BOM, then decode — utf-8-sig should strip it
    headers, rows = parse_csv(content.encode("utf-8-sig"))
    assert headers == ["名称", "行业"]
    assert len(rows) == 1


def test_parse_csv_skips_empty_rows():
    """Empty rows should be skipped."""
    content = "名称,行业\n测试公司,Tech\n\n\n另一家公司,Finance\n"
    headers, rows = parse_csv(content.encode("utf-8"))
    assert len(rows) == 2


def test_auto_map_fields():
    mapping = auto_map_fields(["名称", "行业", "电话"], "account")
    assert mapping["名称"] == "name"
    assert mapping["行业"] == "industry"
    assert mapping["电话"] == "phone"


def test_auto_map_fields_unknown_column():
    """Unknown columns should map to None."""
    mapping = auto_map_fields(["名称", "未知列"], "account")
    assert mapping["名称"] == "name"
    assert mapping["未知列"] is None


def test_create_preview():
    from app.services.csv_service import create_preview
    headers = ["名称", "行业"]
    rows = [["测试公司", "Tech"]]
    preview = create_preview(headers, rows, "account")
    assert preview["preview_id"] is not None
    assert preview["columns"] == ["名称", "行业"]
    assert len(preview["preview_rows"]) == 1
    assert len(preview["available_fields"]) > 0


@pytest.mark.asyncio
async def test_import_account(db_session):
    from app.services.csv_service import create_preview, confirm_import
    from app.models.crm import Account
    from sqlalchemy import select

    # Create a preview
    headers = ["名称", "行业"]
    rows = [["导入测试公司", "Tech"], ["导入测试公司2", "Finance"]]
    preview = create_preview(headers, rows, "account")
    preview_id = preview["preview_id"]

    # Confirm import
    mapping = {"名称": "name", "行业": "industry"}
    result = await confirm_import(db_session, preview_id, mapping, "test_user")

    assert result["success_rows"] == 2
    assert result["error_rows"] == 0

    # Verify records were created
    db_result = await db_session.execute(select(Account).where(Account.name.ilike("导入测试%")))
    accounts = db_result.scalars().all()
    assert len(accounts) == 2


@pytest.mark.asyncio
async def test_import_contact(db_session):
    from app.services.csv_service import create_preview, confirm_import
    from app.models.crm import Contact
    from sqlalchemy import select

    headers = ["姓", "名"]
    rows = [["张", "三"], ["李", "四"]]
    preview = create_preview(headers, rows, "contact")
    result = await confirm_import(db_session, preview["preview_id"], {"姓": "last_name", "名": "first_name"}, "test_user")

    assert result["success_rows"] == 2

    db_result = await db_session.execute(select(Contact).where(Contact.last_name == "张"))
    contacts = db_result.scalars().all()
    assert len(contacts) == 1
    assert contacts[0].first_name == "三"


@pytest.mark.asyncio
async def test_import_missing_required_field(db_session):
    from app.services.csv_service import create_preview, confirm_import

    headers = ["行业"]  # name is required but missing
    rows = [["Tech"]]
    preview = create_preview(headers, rows, "account")
    result = await confirm_import(db_session, preview["preview_id"], {"行业": "industry"}, "test_user")

    assert result["success_rows"] == 0
    assert result["error_rows"] == 1
    assert "Missing required" in result["errors"][0]["error"]


def test_generate_csv():
    from app.services.csv_service import generate_csv
    records = [{"name": "Test", "industry": "Tech"}]
    csv_content = generate_csv("account", records)
    assert "名称" in csv_content
    assert "Test" in csv_content