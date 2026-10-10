from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIInsight(Base):
    __tablename__ = "ai_insights"

    analysis_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "analysis_results.id",
            ondelete="CASCADE"
        ),
        primary_key=True,
        nullable=False
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    strengths: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    weaknesses: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    achievements: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    recommendations: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )