"""Logistics and Delivery tracking endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.delivery import Delivery, DeliveryStatus
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_delivery(
    data: DeliveryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create fulfillment logistics record for an order."""
    result = await db.execute(select(Order).where(Order.id == data.order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if current_user.id not in [order.buyer_id, order.seller_id] and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    delivery = Delivery(
        order_id=data.order_id,
        method=data.method,
        pickup_location=data.pickup_location,
        delivery_location=data.delivery_location,
        expected_date=data.expected_date,
        transport_cost=data.transport_cost,
        cost_borne_by=data.cost_borne_by,
        status=DeliveryStatus.PENDING,
        notes=data.notes,
    )
    db.add(delivery)
    await db.flush()
    return {"id": delivery.id, "message": "Logistics record created successfully"}


@router.patch("/{delivery_id}")
async def update_delivery(
    delivery_id: int,
    data: DeliveryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update dispatch or delivery status."""
    result = await db.execute(select(Delivery).where(Delivery.id == delivery_id))
    deliv = result.scalar_one_or_none()
    if not deliv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery record not found")

    o_res = await db.execute(select(Order).where(Order.id == deliv.order_id))
    order = o_res.scalar_one_or_none()
    if current_user.id not in [order.buyer_id, order.seller_id] and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(deliv, field, val)

    # Sync with order status if dispatched or delivered
    if data.status == DeliveryStatus.DISPATCHED and order.status in [OrderStatus.CONFIRMED, OrderStatus.PAYMENT_CONFIRMED, OrderStatus.READY_FOR_PICKUP]:
        order.status = OrderStatus.DISPATCHED
        order.dispatched_quantity = order.quantity
    elif data.status == DeliveryStatus.DELIVERED and order.status != OrderStatus.COMPLETED:
        order.status = OrderStatus.DELIVERED
        order.delivered_quantity = order.quantity

    await db.flush()
    return {"id": deliv.id, "status": deliv.status.value, "message": "Delivery updated"}
