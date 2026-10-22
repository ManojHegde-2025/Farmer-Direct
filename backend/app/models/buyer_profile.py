"""Buyer profile model."""

import enum
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.farmer_profile import VerificationStatus


class BusinessType(str, enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"
    RETAILER = "RETAILER"
    WHOLESALER = "WHOLESALER"
    PROCESSOR = "PROCESSOR"
    EXPORTER = "EXPORTER"


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    business_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    business_type: Mapped[BusinessType | None] = mapped_column(Enum(BusinessType), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    taluk: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False
    )
    gst_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="buyer_profile")
