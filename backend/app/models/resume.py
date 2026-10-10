import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    file_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    uploaded_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        server_default="CURRENT_TIMESTAMP"
    )

    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    file_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    __table_args__ = (
        Index("idx_resumes_user_id", "user_id"),
    )