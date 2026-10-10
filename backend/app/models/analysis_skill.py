from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalysisSkill(Base):
    __tablename__ = "analysis_skills"

    analysis_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "analysis_results.id",
            ondelete="CASCADE"
        ),
        primary_key=True,
        nullable=False
    )

    skill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("skills.id"),
        primary_key=True,
        nullable=False
    )