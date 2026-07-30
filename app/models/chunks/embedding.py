import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    chunk_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chunks.id", ondelete="CASCADE"),
        index=True,
    )

    vector_id: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(150),
    )