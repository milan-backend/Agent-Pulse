import uuid
from sqlalchemy import Column, String, JSON, DateTime
from datetime import datetime

from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    agent_id = Column(String, nullable=False)
    step_id = Column(String, nullable=False)

    action = Column(String)  # created, completed, failed, retried

    input_data = Column(JSON)
    output_data = Column(JSON)

    error_message = Column(String, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)