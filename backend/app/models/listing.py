"""Listing model."""

import enum
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    String, Enum, DateTime, ForeignKey, Numeric, Text, Boolean, Date, JSON, func, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.commodity import CommodityUnit


class QualityGrade(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    UNGRADED = "UNGRADED"


class ListingStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    ACTIVE = "ACTIVE"
    PARTIALLY_RESERVED = "PARTIALLY_RESERVED"
    SOLD_OUT = "SOLD_OUT"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farmer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    commodity_id: Mapped[int] = mapped_column(
        ForeignKey("commodities.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    variety: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quality_grade: Mapped[QualityGrade] = mapped_column(
        Enum(QualityGrade), default=QualityGrade.UNGRADED, nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    available_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit: Mapped[CommodityUnit] = mapped_column(Enum(CommodityUnit), nullable=False)
    price_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    min_order_quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    images: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus), default=ListingStatus.DRAFT, nullable=False, index=True
    )
    harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    available_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    available_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    pickup_location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    delivery_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    delivery_radius_km: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    farmer: Mapped["User"] = relationship("User", foreign_keys=[farmer_id], lazy="selectin")
    commodity: Mapped["Commodity"] = relationship("Commodity", lazy="selectin")

    __table_args__ = (
        Index("ix_listings_status_commodity", "status", "commodity_id"),
    )
