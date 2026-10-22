"""Buyer requirement model."""

from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BuyerRequirement(Base):
    __tablename__ = "buyer_requirements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    commodity_id: Mapped[int] = mapped_column(
        ForeignKey("commodities.id"), nullable=False, index=True
    )
    variety_preference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quality_preference: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity_needed: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    max_price_per_unit: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    delivery_location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    delivery_district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    needed_by: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    buyer: Mapped["User"] = relationship("User", foreign_keys=[buyer_id], lazy="selectin")
    commodity: Mapped["Commodity"] = relationship("Commodity", lazy="selectin")
