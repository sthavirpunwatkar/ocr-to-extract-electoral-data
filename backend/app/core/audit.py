from sqlalchemy.orm import Session
from app.db.models import AuditLog
from typing import Any, Optional

def log_action(
    db: Session,
    action: str,
    target_type: str,
    target_id: str,
    user_id: Optional[str] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None
):
    """Logs an action to the audit_logs table."""
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        old_value=old_value,
        new_value=new_value
    )
    db.add(log_entry)
    db.commit()
