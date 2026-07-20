"""
Approval service — manages approval request lifecycle.
"""
import json
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.approval import ApprovalRule, ApprovalRequest, ApprovalStep
from app.models.auth import User
from app.services.workflow_service import evaluate_conditions


async def trigger_approval(
    db: AsyncSession,
    object_type: str,
    object_id: str,
    record_data: dict,
    submitter_id: str,
) -> ApprovalRequest | None:
    """
    Check if any approval rules match the record data and create an approval request.
    Returns the ApprovalRequest if created, or None if no rules match.
    """
    result = await db.execute(
        select(ApprovalRule).where(
            ApprovalRule.object_type == object_type,
            ApprovalRule.is_active == True,
        ).order_by(ApprovalRule.approval_order)
    )
    rules = result.scalars().all()

    if not rules:
        return None

    # Group rules by approval_order to determine total steps
    rule_groups: dict[int, list[ApprovalRule]] = {}
    for rule in rules:
        conditions = rule.condition_expression
        if isinstance(conditions, str):
            conditions = json.loads(conditions) if conditions else []
        if evaluate_conditions(record_data, conditions or []):
            rule_groups.setdefault(rule.approval_order, []).append(rule)

    if not rule_groups:
        return None

    total_steps = max(rule_groups.keys())

    # For now, use the first rule of the first matching group
    first_group = rule_groups[min(rule_groups.keys())]
    primary_rule = first_group[0]

    # Determine approver
    approver_id = await _resolve_approver(db, primary_rule, submitter_id)
    if not approver_id:
        return None

    # Create request
    approval_request = ApprovalRequest(
        rule_id=primary_rule.id,
        object_type=object_type,
        object_id=object_id,
        submitter_id=submitter_id,
        status="pending",
        current_step=1,
        total_steps=total_steps,
    )
    db.add(approval_request)
    await db.flush()

    # Create first step
    step = ApprovalStep(
        request_id=approval_request.id,
        step_order=1,
        approver_id=approver_id,
        status="pending",
    )
    db.add(step)
    await db.commit()

    # Send notification to approver
    try:
        from app.services.notification_service import create_notification
        await create_notification(
            db,
            user_id=approver_id,
            title="审批请求",
            message=f"您有一个新的审批请求需要处理",
            notification_type="approval",
            reference_type=object_type,
            reference_id=object_id,
        )
    except Exception:
        pass  # Notification is non-critical

    # Re-query with steps loaded to avoid MissingGreenlet on response serialization
    result = await db.execute(
        select(ApprovalRequest)
        .options(selectinload(ApprovalRequest.steps), selectinload(ApprovalRequest.rule))
        .where(ApprovalRequest.id == approval_request.id)
    )
    return result.scalar_one()


async def _resolve_approver(
    db: AsyncSession,
    rule: ApprovalRule,
    submitter_id: str,
) -> str | None:
    """Resolve the approver for a rule."""
    if rule.approver_type == "specific_user" and rule.approver_user_id:
        return rule.approver_user_id
    elif rule.approver_type == "manager":
        # Get the submitter's manager (owner_id or similar)
        # For simplicity, return the first admin user
        result = await db.execute(
            select(User).join(User.profile).where(User.profile.has(profile_type="admin"))
        )
        admin = result.scalars().first()
        if admin:
            return admin.id
    return None


async def approve_request(
    db: AsyncSession,
    request_id: str,
    approver_id: str,
    comment: str | None = None,
) -> ApprovalRequest:
    """Approve the current step of an approval request."""
    request = await db.execute(
        select(ApprovalRequest)
        .options(selectinload(ApprovalRequest.steps))
        .where(ApprovalRequest.id == request_id)
    )
    request = request.scalar_one_or_none()
    if not request:
        raise ValueError("Approval request not found")
    if request.status != "pending":
        raise ValueError("Approval request is already processed")

    # Find current pending step
    current_step = None
    for step in request.steps:
        if step.step_order == request.current_step and step.status == "pending":
            current_step = step
            break

    if not current_step:
        raise ValueError("No pending step found")

    if current_step.approver_id != approver_id:
        raise ValueError("You are not the approver for this step")

    # Approve the step
    current_step.status = "approved"
    current_step.comment = comment
    current_step.acted_at = datetime.now()

    # Check if there are more steps
    if request.current_step >= request.total_steps:
        request.status = "approved"
    else:
        request.current_step += 1
        # Create next step
        # Find the next rule group
        result = await db.execute(
            select(ApprovalRule).where(
                ApprovalRule.object_type == request.object_type,
                ApprovalRule.is_active == True,
                ApprovalRule.approval_order == request.current_step,
            )
        )
        next_rules = result.scalars().all()
        if next_rules:
            next_rule = next_rules[0]
            next_approver = await _resolve_approver(db, next_rule, request.submitter_id)
            if next_approver:
                next_step = ApprovalStep(
                    request_id=request.id,
                    step_order=request.current_step,
                    approver_id=next_approver,
                    status="pending",
                )
                db.add(next_step)

    await db.commit()

    # Re-query with steps loaded
    result = await db.execute(
        select(ApprovalRequest)
        .options(selectinload(ApprovalRequest.steps), selectinload(ApprovalRequest.rule))
        .where(ApprovalRequest.id == request.id)
    )
    return result.scalar_one()


async def reject_request(
    db: AsyncSession,
    request_id: str,
    approver_id: str,
    comment: str | None = None,
) -> ApprovalRequest:
    """Reject the current step (rejects the entire request)."""
    request = await db.execute(
        select(ApprovalRequest)
        .options(selectinload(ApprovalRequest.steps))
        .where(ApprovalRequest.id == request_id)
    )
    request = request.scalar_one_or_none()
    if not request:
        raise ValueError("Approval request not found")
    if request.status != "pending":
        raise ValueError("Approval request is already processed")

    # Find current pending step
    current_step = None
    for step in request.steps:
        if step.step_order == request.current_step and step.status == "pending":
            current_step = step
            break

    if not current_step:
        raise ValueError("No pending step found")

    if current_step.approver_id != approver_id:
        raise ValueError("You are not the approver for this step")

    current_step.status = "rejected"
    current_step.comment = comment
    current_step.acted_at = datetime.now()
    request.status = "rejected"

    await db.commit()

    # Re-query with steps loaded
    result = await db.execute(
        select(ApprovalRequest)
        .options(selectinload(ApprovalRequest.steps), selectinload(ApprovalRequest.rule))
        .where(ApprovalRequest.id == request.id)
    )
    return result.scalar_one()


async def get_my_queue(
    db: AsyncSession,
    user_id: str,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ApprovalRequest], int]:
    """Get the approval queue for a user."""
    query = (
        select(ApprovalRequest)
        .options(selectinload(ApprovalRequest.steps), selectinload(ApprovalRequest.rule), selectinload(ApprovalRequest.submitter))
        .join(ApprovalStep, ApprovalStep.request_id == ApprovalRequest.id)
        .where(
            ApprovalStep.approver_id == user_id,
            ApprovalStep.status == "pending",
        )
    )
    count_query = (
        select(func.count(ApprovalRequest.id))
        .join(ApprovalStep, ApprovalStep.request_id == ApprovalRequest.id)
        .where(
            ApprovalStep.approver_id == user_id,
            ApprovalStep.status == "pending",
        )
    )

    if status_filter:
        query = query.where(ApprovalRequest.status == status_filter)
        count_query = count_query.where(ApprovalRequest.status == status_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(ApprovalRequest.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    # Deduplicate (same request may appear multiple times due to join)
    seen = set()
    unique = []
    for item in items:
        if item.id not in seen:
            seen.add(item.id)
            unique.append(item)

    return unique, total