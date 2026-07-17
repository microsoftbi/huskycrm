"""
Migration: Create contact_accounts table and migrate existing account_id data.

Usage:
    cd backend && source venv/bin/activate
    python ../migrate_contact_accounts.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from sqlalchemy import select, delete
from app.database import engine, Base
from app.models.crm import Contact, ContactAccount


async def migrate():
    # Create tables (idempotent)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Clean any bad data first
    async with engine.begin() as conn:
        await conn.execute(delete(ContactAccount))
        print("🧹 Cleared existing ContactAccount data")

    # Migrate existing data using column names
    async with engine.begin() as conn:
        # Find all contacts with account_id
        result = await conn.execute(
            select(Contact.id, Contact.account_id).where(Contact.account_id.isnot(None))
        )
        rows = result.fetchall()

        count = 0
        for row in rows:
            contact_id = row.id
            account_id = row.account_id
            # Insert into contact_accounts
            await conn.execute(
                ContactAccount.__table__.insert().values(
                    contact_id=contact_id,
                    account_id=account_id,
                )
            )
            count += 1

        print(f"✅ Migrated {count} contact-account associations.")

    # Verify
    async with engine.begin() as conn:
        total = await conn.execute(select(ContactAccount))
        rows = total.fetchall()
        print(f"📊 Total ContactAccount rows: {len(rows)}")
        # Show a sample
        for r in rows[:3]:
            print(f"   id={r.id}, contact_id={r.contact_id}, account_id={r.account_id}")


if __name__ == "__main__":
    asyncio.run(migrate())
