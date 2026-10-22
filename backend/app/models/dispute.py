"""Dispute model."""

import enum
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DisputeCategory(str, enum.Enum):
    QUALITY = "QUALITY"
    QUANTITY = "QUANTITY"
    DELIVERY = "DELIVERY"
    PAYMENT = "PAYMENT"
    FRAUD = "FRAUD"
    OTHER = "OTHER"


class DisputeStatus(str, enum.Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    raised_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    against_user: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    category: Mapped[DisputeCategory] = mapped_column(Enum(DisputeCategory), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[DisputeStatus] = mapped_column(
        Enum(DisputeStatus), default=DisputeStatus.OPEN, nullable=False
    )
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    order: Mapped["Order"] = relationship("Order", lazy="selectin")
    raiser: Mapped["User"] = relationship("User", foreign_keys=[raised_by], lazy="selectin")
    against: Mapped["User"] = relationship("User", foreign_keys=[against_user], lazy="selectin")
    admin: Mapped["User | None"] = relationship("User", foreign_keys=[admin_id], lazy="selectin")
