"""
Lead service — assignment rules, conversion, and Web-to-Lead.
"""
import json
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead, LeadAssignmentRule
from app.models.crm import Account, Contact, Opportunity
from app.services.workflow_service import evaluate_conditions


async def apply_assignment_rules(
    db: AsyncSession,
    lead_data: dict,
) -> str | None:
    """
    Apply assignment rules to determine which user a lead should be assigned to.
    Returns the user_id or None if no rules match.
    """
    result = await db.execute(
        select(LeadAssignmentRule)
        .where(LeadAssignmentRule.is_active == True)
        .order_by(LeadAssignmentRule.priority.desc())
    )
    rules = result.scalars().all()

    for rule in rules:
        conditions = rule.condition_expression
        if isinstance(conditions, str):
            conditions = json.loads(conditions) if conditions else []

        if evaluate_conditions(lead_data, conditions or []):
            return rule.assign_to_user_id

    return None


async def convert_lead(
    db: AsyncSession,
    lead: Lead,
    account_name: str | None = None,
    account_id: str | None = None,
    create_opportunity: bool = True,
    opportunity_name: str | None = None,
    opportunity_amount: float | None = None,
) -> dict:
    """
    Convert a lead to Account + Contact + (optionally) Opportunity.
    """
    if lead.is_converted:
        raise ValueError("Lead is already converted")

    # Create or find Account
    if account_id:
        # Use existing account
        result = await db.execute(select(Account).where(Account.id == account_id))
        account = result.scalar_one_or_none()
        if not account:
            raise ValueError("Account not found")
    else:
        # Create new account
        name = account_name or lead.company
        account = Account(name=name, industry=lead.industry)
        db.add(account)
        await db.flush()

    # Create Contact
    contact = Contact(
        account_id=account.id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        email=lead.email,
        phone=lead.phone,
        mobile_phone=lead.mobile_phone,
        title=lead.title,
    )
    db.add(contact)
    await db.flush()

    # Create Opportunity (optional)
    opportunity = None
    if create_opportunity:
        # Get the first stage as default
        from app.models.crm import Stage
        stage_result = await db.execute(select(Stage).order_by(Stage.sort_order).limit(1))
        first_stage = stage_result.scalar_one_or_none()

        opp_name = opportunity_name or f"{lead.company} - {lead.first_name} {lead.last_name}"
        opportunity = Opportunity(
            name=opp_name,
            account_id=account.id,
            stage_id=first_stage.id if first_stage else None,
            amount=opportunity_amount or 0,
            description=lead.description,
        )
        db.add(opportunity)
        await db.flush()

    # Update lead as converted
    lead.is_converted = True
    lead.converted_account_id = account.id
    lead.converted_contact_id = contact.id
    if opportunity:
        lead.converted_opportunity_id = opportunity.id
    lead.converted_at = datetime.now()
    lead.status = "Converted"

    await db.commit()

    return {
        "lead_id": lead.id,
        "account_id": account.id,
        "contact_id": contact.id,
        "opportunity_id": opportunity.id if opportunity else None,
        "message": "Lead converted successfully",
    }