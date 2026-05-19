import uuid
from sqlalchemy import Column, String, JSON, Integer,DateTime,Boolean
from app.db.session import Base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint


class DurableStep(Base):
    __tablename__ = "durable_steps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    agent_id = Column(String, nullable=False)
    task_name = Column(String, nullable=False)

    status = Column(String, default="pending")

    input_data = Column(JSON)
    output_data = Column(JSON)

    idempotency_key = Column(String)

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "idempotency_key",
            name = "uq_workspace_idempotency"
        ),
    )

    retry_count = Column(Integer, default=0)

    error_message = Column(String, nullable=True)

    cache_key = Column(String, index=True)

    created_at = Column(DateTime(timezone=True),server_default=func.now())
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)

    cache_hit = Column(Boolean, default=False)

    event_type = Column(String, nullable=True)

    paused_at = Column(DateTime(timezone=True), nullable=True)

    killed_at = Column(DateTime(timezone=True), nullable=True)

    resumed_at = Column(DateTime(timezone=True), nullable=True)

    killed_by = Column(String, nullable=True)

    resumed_by = Column(String, nullable=True)

    pause_reason = Column(String, nullable=True)

    runtime_controlled = Column(Boolean, default=False)

    workspace_id = Column(UUID(as_uuid=True), nullable=True)