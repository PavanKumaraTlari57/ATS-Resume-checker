import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    plan: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    is_active: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        server_default="false"
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        server_default="CURRENT_TIMESTAMP"
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    __table_args__ = (
        Index(
            "idx_subscriptions_user_id",
            "user_id"
        ),

        CheckConstraint(
            "plan IN ('Basic', 'Pro', 'Premium')",
            name="subscriptions_plan_check"
        ),
    )