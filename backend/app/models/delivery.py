"""Delivery model."""

import enum
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import String, Enum, DateTime, ForeignKey, Numeric, Text, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DeliveryMethod(str, enum.Enum):
    BUYER_PICKUP = "BUYER_PICKUP"
    SELLER_DELIVERY = "SELLER_DELIVERY"
    THIRD_PARTY = "THIRD_PARTY"


class DeliveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    DISPATCHED = "DISPATCHED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class CostBorneBy(str, enum.Enum):
    BUYER = "BUYER"
    SELLER = "SELLER"
    SHARED = "SHARED"


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    method: Mapped[DeliveryMethod] = mapped_column(Enum(DeliveryMethod), nullable=False)
    pickup_location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    delivery_location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expected_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    transport_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    cost_borne_by: Mapped[CostBorneBy | None] = mapped_column(Enum(CostBorneBy), nullable=True)
    dispatch_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="delivery")
