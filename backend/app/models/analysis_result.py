import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()"
    )

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False
    )

    ats_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        server_default="CURRENT_TIMESTAMP"
    )

    jd_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id"),
        nullable=False
    )

    __table_args__ = (
        Index("idx_analysis_results_jd_id", "jd_id"),
        Index("idx_analysis_results_resume_id", "resume_id"),

        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="analysis_restatus_check"
        ),

        CheckConstraint(
            "ats_score >= 0 AND ats_score <= 100",
            name="analysis_results_ats_score_check"
        ),
    )