import uuid
from sqlalchemy import Column, String, JSON, Integer,DateTime,Boolean
from app.db.session import Base
from sqlalchemy.sql import func


class DurableStep(Base):
    __tablename__ = "durable_steps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    agent_id = Column(String, nullable=False)
    task_name = Column(String, nullable=False)

    status = Column(String, default="pending")

    input_data = Column(JSON)
    output_data = Column(JSON)

    idempotency_key = Column(String, unique=True)

    retry_count = Column(Integer, default=0)

    error_message = Column(String, nullable=True)

    cache_key = Column(String, index=True)

    created_at = Column(DateTime(timezone=True),server_default=func.now())
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())

    cache_hit = Column(Boolean, default=False)

    event_type = Column(String, nullable=True)