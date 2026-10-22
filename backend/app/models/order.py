"""Order model."""

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Enum, DateTime, ForeignKey, Numeric, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrderStatus(str, enum.Enum):
    CREATED = "CREATED"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    DISPATCHED = "DISPATCHED"
    DELIVERED = "DELIVERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"


# Valid status transitions
ORDER_STATUS_TRANSITIONS = {
    OrderStatus.CREATED: [OrderStatus.AWAITING_CONFIRMATION, OrderStatus.CANCELLED],
    OrderStatus.AWAITING_CONFIRMATION: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.PAYMENT_PENDING, OrderStatus.CANCELLED],
    OrderStatus.PAYMENT_PENDING: [OrderStatus.PAYMENT_CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.PAYMENT_CONFIRMED: [OrderStatus.READY_FOR_PICKUP, OrderStatus.DISPATCHED, OrderStatus.CANCELLED, OrderStatus.DISPUTED],
    OrderStatus.READY_FOR_PICKUP: [OrderStatus.DISPATCHED, OrderStatus.DELIVERED, OrderStatus.CANCELLED, OrderStatus.DISPUTED],
    OrderStatus.DISPATCHED: [OrderStatus.DELIVERED, OrderStatus.DISPUTED],
    OrderStatus.DELIVERED: [OrderStatus.COMPLETED, OrderStatus.DISPUTED],
    OrderStatus.COMPLETED: [OrderStatus.DISPUTED],
    OrderStatus.CANCELLED: [],
    OrderStatus.DISPUTED: [OrderStatus.COMPLETED, OrderStatus.CANCELLED],
}


class FulfilmentMethod(str, enum.Enum):
    BUYER_PICKUP = "BUYER_PICKUP"
    SELLER_DELIVERY = "SELLER_DELIVERY"
    THIRD_PARTY = "THIRD_PARTY"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    offer_id: Mapped[int | None] = mapped_column(
        ForeignKey("offers.id"), nullable=True, index=True
    )
    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id"), nullable=False, index=True
    )
    commodity_id: Mapped[int] = mapped_column(
        ForeignKey("commodities.id"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reserved_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    dispatched_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    delivered_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    price_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.CREATED, nullable=False, index=True
    )
    fulfilment_method: Mapped[FulfilmentMethod | None] = mapped_column(
        Enum(FulfilmentMethod), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    offer: Mapped["Offer | None"] = relationship("Offer", lazy="selectin")
    buyer: Mapped["User"] = relationship("User", foreign_keys=[buyer_id], lazy="selectin")
    seller: Mapped["User"] = relationship("User", foreign_keys=[seller_id], lazy="selectin")
    listing: Mapped["Listing"] = relationship("Listing", lazy="selectin")
    commodity: Mapped["Commodity"] = relationship("Commodity", lazy="selectin")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="order", lazy="selectin")
    delivery: Mapped["Delivery | None"] = relationship("Delivery", back_populates="order", uselist=False, lazy="selectin")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", lazy="selectin")

    __table_args__ = (
        Index("ix_orders_buyer_status", "buyer_id", "status"),
        Index("ix_orders_seller_status", "seller_id", "status"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    listing: Mapped["Listing"] = relationship("Listing", lazy="selectin")
