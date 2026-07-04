import uuid
from sqlalchemy import Column, String, JSON, DateTime
from datetime import datetime
from app.db.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # 🟢 NEW: Identity snapshot columns
    workspace_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    user_name = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    user_role = Column(String, nullable=True)

    # 🟡 UPDATED: Made nullable=True so we can log non-agent actions too
    agent_id = Column(
        String,
        nullable=True
    )

    step_id = Column(
        String,
        nullable=True
    )

    action = Column(
        String
    )

    input_data = Column(
        JSON,
        nullable=True
    )

    output_data = Column(
        JSON,
        nullable=True
    )

    error_message = Column(
        String,
        nullable=True
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )