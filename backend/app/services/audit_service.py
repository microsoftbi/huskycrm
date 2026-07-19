"""
Audit log service — SQLAlchemy event listeners for automatic change tracking.

Uses a context variable to pass the current user ID from the request middleware
to the event listeners, which fire synchronously on the same connection.
"""
import contextvars
from sqlalchemy import event
from sqlalchemy.orm.attributes import get_history
from app.models.audit_log import AuditLog

# Context variable to hold current user ID for audit logging
current_user_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_user_id", default=None
)

# Fields to exclude from audit logging (sensitive or auto-generated)
EXCLUDED_FIELDS = {"password_hash", "updated_at", "created_at"}

_audit_listeners_attached = False


def setup_audit_listeners():
    """Mark that audit listeners should be used.

    Actual listener attachment happens via attach_listeners() called
    for each model class from database.py.
    """
    global _audit_listeners_attached
    _audit_listeners_attached = True


def attach_listeners(model_class):
    """Attach after_insert/after_update/after_delete listeners to a model class."""
    @event.listens_for(model_class, "after_insert")
    def receive_after_insert(mapper, connection, target):
        _record_audit(connection, target, "create")

    @event.listens_for(model_class, "after_update")
    def receive_after_update(mapper, connection, target):
        _record_audit(connection, target, "update")

    @event.listens_for(model_class, "after_delete")
    def receive_after_delete(mapper, connection, target):
        _record_audit(connection, target, "delete")


def _record_audit(connection, target, action: str):
    """Record an audit log entry for the given target object and action."""
    object_type = target.__class__.__name__
    object_id = str(target.id)
    user_id = current_user_id.get() or "system"

    if action == "create":
        connection.execute(
            AuditLog.__table__.insert().values(
                object_type=object_type,
                object_id=object_id,
                field_name=None,
                old_value=None,
                new_value=None,
                action="create",
                user_id=user_id,
            )
        )
    elif action == "delete":
        connection.execute(
            AuditLog.__table__.insert().values(
                object_type=object_type,
                object_id=object_id,
                field_name=None,
                old_value=None,
                new_value=None,
                action="delete",
                user_id=user_id,
            )
        )
    elif action == "update":
        for col in target.__table__.columns:
            field_name = col.name
            if field_name in EXCLUDED_FIELDS or field_name == "id":
                continue

            hist = get_history(target, field_name)
            if hist.has_changes():
                old_val = str(hist.deleted[0]) if hist.deleted else None
                new_val = str(hist.added[0]) if hist.added else None
                connection.execute(
                    AuditLog.__table__.insert().values(
                        object_type=object_type,
                        object_id=object_id,
                        field_name=field_name,
                        old_value=old_val,
                        new_value=new_val,
                        action="update",
                        user_id=user_id,
                    )
                )