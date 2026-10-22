"""Farmer profile model."""

import enum
from datetime import datetime

from sqlalchemy import String, Boolean, Enum, DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class District(str, enum.Enum):
    UDUPI = "UDUPI"
    DAKSHINA_KANNADA = "DAKSHINA_KANNADA"


class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    farm_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    farm_location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    district: Mapped[District | None] = mapped_column(Enum(District), nullable=True)
    taluk: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village: Mapped[str | None] = mapped_column(String(100), nullable=True)
    farm_size_acres: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    primary_crops: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False
    )
    verification_document_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bank_account_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="farmer_profile")
