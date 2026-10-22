"""Order management endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.order import Order, OrderStatus
from app.models.listing import Listing
from app.models.user import User, UserRole
from app.schemas.order import OrderStatusUpdate
from app.middleware.auth import get_current_user
from app.services import order_service
from app.services.net_proceeds import calculate_estimated_net_proceeds

router = APIRouter()


@router.get("/")
async def list_orders(
    role_view: Optional[str] = Query("all", pattern="^(buyer|seller|all)$"),
    status_filter: Optional[OrderStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List orders for the authenticated user."""
    stmt = (
        select(Order)
        .options(
            selectinload(Order.commodity),
            selectinload(Order.listing),
            selectinload(Order.buyer),
            selectinload(Order.seller),
        )
    )

    if current_user.role == UserRole.ADMIN:
        pass  # Admin can see all
    elif role_view == "buyer":
        stmt = stmt.where(Order.buyer_id == current_user.id)
    elif role_view == "seller":
        stmt = stmt.where(Order.seller_id == current_user.id)
    else:
        stmt = stmt.where(
            or_(Order.buyer_id == current_user.id, Order.seller_id == current_user.id)
        )

    if status_filter:
        stmt = stmt.where(Order.status == status_filter)

    stmt = stmt.order_by(Order.created_at.desc())
    result = await db.execute(stmt)
    orders = result.scalars().all()

    return [
        {
            "id": o.id,
            "commodity_name": o.commodity.name if o.commodity else "Commodity",
            "listing_title": o.listing.title if o.listing else None,
            "unit": o.listing.unit.value if o.listing and hasattr(o.listing.unit, "value") else "KG",
            "quantity": float(o.quantity),
            "reserved_quantity": float(o.reserved_quantity),
            "dispatched_quantity": float(o.dispatched_quantity),
            "delivered_quantity": float(o.delivered_quantity),
            "price_per_unit": float(o.price_per_unit),
            "total_price": float(o.total_price),
            "status": o.status.value,
            "fulfilment_method": o.fulfilment_method.value if o.fulfilment_method else None,
            "buyer_name": o.buyer.full_name if o.buyer else "Buyer",
            "seller_name": o.seller.full_name if o.seller else "Farmer",
            "is_buyer": o.buyer_id == current_user.id,
            "is_seller": o.seller_id == current_user.id,
            "created_at": o.created_at.isoformat(),
            "updated_at": o.updated_at.isoformat(),
        }
        for o in orders
    ]


@router.get("/{order_id}")
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full details of an order."""
    order = await order_service.get_order_by_id(db, order_id)

    # Permission check
    is_admin = current_user.role == UserRole.ADMIN
    if not (is_admin or current_user.id in [order.buyer_id, order.seller_id]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this order",
        )

    return {
        "id": order.id,
        "offer_id": order.offer_id,
        "listing_id": order.listing_id,
        "listing_title": order.listing.title if order.listing else None,
        "commodity_id": order.commodity_id,
        "commodity_name": order.commodity.name if order.commodity else None,
        "unit": order.listing.unit.value if order.listing and hasattr(order.listing.unit, "value") else "KG",
        "buyer_id": order.buyer_id,
        "buyer_name": order.buyer.full_name if order.buyer else "Buyer",
        "seller_id": order.seller_id,
        "seller_name": order.seller.full_name if order.seller else "Farmer",
        "quantity": float(order.quantity),
        "reserved_quantity": float(order.reserved_quantity),
        "dispatched_quantity": float(order.dispatched_quantity),
        "delivered_quantity": float(order.delivered_quantity),
        "price_per_unit": float(order.price_per_unit),
        "total_price": float(order.total_price),
        "status": order.status.value,
        "fulfilment_method": order.fulfilment_method.value if order.fulfilment_method else None,
        "payments": [
            {
                "id": p.id,
                "amount": float(p.amount),
                "status": p.status.value,
                "method": p.method.value if hasattr(p.method, "value") else str(p.method),
                "is_simulated": p.is_simulated,
                "paid_at": p.paid_at.isoformat() if p.paid_at else None,
            }
            for p in order.payments
        ],
        "delivery": {
            "id": order.delivery.id,
            "method": order.delivery.method.value if hasattr(order.delivery.method, "value") else str(order.delivery.method),
            "status": order.delivery.status.value if hasattr(order.delivery.status, "value") else str(order.delivery.status),
            "pickup_location": order.delivery.pickup_location,
            "delivery_location": order.delivery.delivery_location,
            "expected_date": order.delivery.expected_date.isoformat() if order.delivery.expected_date else None,
            "transport_cost": float(order.delivery.transport_cost) if order.delivery.transport_cost else None,
            "cost_borne_by": order.delivery.cost_borne_by.value if order.delivery.cost_borne_by else None,
        } if order.delivery else None,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
    }


@router.patch("/{order_id}/status")
async def update_status(
    order_id: int,
    data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transition order status. Follows validated state machine."""
    order = await order_service.update_order_status(
        db=db,
        user=current_user,
        order_id=order_id,
        new_status=data.status,
    )
    return {
        "id": order.id,
        "status": order.status.value,
        "reserved_quantity": float(order.reserved_quantity),
        "delivered_quantity": float(order.delivered_quantity),
        "message": f"Order status updated to {order.status.value}",
    }


@router.get("/{order_id}/breakdown")
async def get_order_financial_breakdown(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the transparent cost breakdown and estimated net proceeds for an order."""
    order = await order_service.get_order_by_id(db, order_id)

    # Permission check: seller, buyer, or admin
    if current_user.role != UserRole.ADMIN and current_user.id not in [order.seller_id, order.buyer_id]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    delivery = order.delivery
    breakdown = calculate_estimated_net_proceeds(order, delivery=delivery)
    return breakdown
