import pytest
from app.models.crm import Account


@pytest.mark.asyncio
async def test_search_like_fallback(db_session):
    """Test the LIKE search fallback works."""
    from app.services.search_service import _search_like_fallback

    # Create a test account
    account = Account(name="SearchTest Corp", industry="Tech")
    db_session.add(account)
    await db_session.commit()

    # Search for it
    results = await _search_like_fallback(db_session, "SearchTest", 5)
    assert len(results["accounts"]) >= 1
    assert results["accounts"][0]["name"] == "SearchTest Corp"


@pytest.mark.asyncio
async def test_search_like_fallback_no_match(db_session):
    """Test fallback returns empty results for non-matching query."""
    from app.services.search_service import _search_like_fallback

    results = await _search_like_fallback(db_session, "NonExistentXYZ", 5)
    assert len(results["accounts"]) == 0
    assert len(results["contacts"]) == 0
    assert len(results["opportunities"]) == 0
    assert len(results["products"]) == 0
    assert len(results["events"]) == 0


@pytest.mark.asyncio
async def test_search_like_fallback_multi_type(db_session):
    """Test searching across multiple object types."""
    from app.services.search_service import _search_like_fallback

    # Create an account and a contact with similar names
    from app.models.crm import Contact
    account = Account(name="Acme Corp", industry="Manufacturing")
    db_session.add(account)
    contact = Contact(first_name="Acme", last_name="Contact", email="acme@test.com")
    db_session.add(contact)
    await db_session.commit()

    results = await _search_like_fallback(db_session, "Acme", 5)
    assert len(results["accounts"]) >= 1
    assert len(results["contacts"]) >= 1