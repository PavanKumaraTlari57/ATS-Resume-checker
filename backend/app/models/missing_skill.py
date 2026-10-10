import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MissingSkill(Base):
    __tablename__ = "missing_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()"
    )

    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "analysis_results.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "analysis_id",
            "skill_id",
            name="missing_skills_analysis_id_skill_id_key"
        ),
    )