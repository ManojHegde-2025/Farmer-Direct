"""Order management service.

PHASE 12 specification:
- Lifecycle: CREATED -> AWAITING_CONFIRMATION -> CONFIRMED -> PAYMENT_PENDING ->
  PAYMENT_CONFIRMED -> READY_FOR_PICKUP -> DISPATCHED -> DELIVERED -> COMPLETED -> CANCELLED -> DISPUTED.
- Enforces valid state transitions.
- Safely releases inventory reservation on CANCELLED.
- Tracks dispatched & delivered quantities.
"""

from decimal import Decimal
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus, ORDER_STATUS_TRANSITIONS
from app.models.user import User, UserRole
from app.services.inventory_service import release_stock


async def get_order_by_id(db: AsyncSession, order_id: int) -> Order:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.buyer),
            selectinload(Order.seller),
            selectinload(Order.listing),
            selectinload(Order.commodity),
            selectinload(Order.payments),
            selectinload(Order.delivery),
        )
        .where(Order.id == order_id)
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order #{order_id} not found",
        )
    return order


async def update_order_status(
    db: AsyncSession,
    user: User,
    order_id: int,
    new_status: OrderStatus,
    reason: Optional[str] = None,
) -> Order:
    """Validate and transition an order to a new status."""
    order = await get_order_by_id(db, order_id)

    # Permission check: must be buyer, seller, or admin
    is_admin = user.role == UserRole.ADMIN
    is_buyer = user.id == order.buyer_id
    is_seller = user.id == order.seller_id

    if not (is_admin or is_buyer or is_seller):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify this order",
        )

    # Check allowed transitions
    allowed_next_states = ORDER_STATUS_TRANSITIONS.get(order.status, [])
    if new_status not in allowed_next_states and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid order transition from {order.status.value} to {new_status.value}",
        )

    # If cancelling, release the reserved stock back to the listing
    if new_status == OrderStatus.CANCELLED and order.status != OrderStatus.CANCELLED:
        remaining_reservation = order.reserved_quantity - order.delivered_quantity
        if remaining_reservation > Decimal("0"):
            await release_stock(db, order.listing_id, remaining_reservation)
            order.reserved_quantity = Decimal("0.00")

    # If completing or delivering, update delivered quantity
    if new_status == OrderStatus.DELIVERED:
        order.delivered_quantity = order.quantity
    elif new_status == OrderStatus.DISPATCHED:
        order.dispatched_quantity = order.quantity

    order.status = new_status
    await db.flush()
    return order
