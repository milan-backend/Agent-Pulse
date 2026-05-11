import uuid
from sqlalchemy import Column, String, Boolean, JSON,ForeignKey,Integer,Float
from app.db.session import Base
from sqlalchemy.dialects.postgresql import UUID


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    api_key_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    key_id = Column(String, nullable=False, unique=True)

    allowed_tasks = Column(JSON, default=list)

    user_id = Column(UUID(as_uuid=True),
                     ForeignKey("users.id"))
    
    max_steps = Column(Integer, default=20)

    max_retries = Column(Integer, default=3)

    max_cost = Column(Float, default=5.0)

    max_repeated_tasks = Column(Integer, default=5)

    is_killed = Column(Boolean, default=False)