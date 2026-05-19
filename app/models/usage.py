import uuid
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Usage(Base):
    __tablename__ = "usage"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    agent_id = Column(String, nullable=False)

    step_id = Column(String, nullable=False)

    action = Column(String)  

    timestamp = Column(DateTime, default=datetime.utcnow)

    cost = Column(Float , default=0)

    prompt_tokens = Column(Integer, default=0)

    completion_tokens = Column(Integer, default=0)

    usage_events = Column(JSON)

    workspace_id = Column(UUID(as_uuid=True), nullable=True)