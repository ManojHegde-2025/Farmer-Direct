"""Payment and Settlement endpoints (Simulated & Manual Tracking)."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.schemas.payment import PaymentCreate, PaymentStatusUpdate
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def record_payment(
    data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a simulated or offline/manual payment.

    Clearly distinguishes demonstration/simulated payment from live financial settlement.
    """
    result = await db.execute(select(Order).where(Order.id == data.order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if current_user.id not in [order.buyer_id, order.seller_id] and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    payment = Payment(
        order_id=data.order_id,
        amount=data.amount,
        method=data.method or PaymentMethod.BANK_TRANSFER,
        status=PaymentStatus.CONFIRMED,
        is_simulated=True,
        reference_number=data.reference_number or f"SIM-TXN-{int(datetime.now().timestamp())}",
        paid_at=datetime.now(timezone.utc),
    )
    db.add(payment)

    # If order is in PAYMENT_PENDING or CONFIRMED, update order to PAYMENT_CONFIRMED
    if order.status in [OrderStatus.PAYMENT_PENDING, OrderStatus.CONFIRMED]:
        order.status = OrderStatus.PAYMENT_CONFIRMED

    await db.flush()
    return {
        "id": payment.id,
        "order_id": payment.order_id,
        "amount": float(payment.amount),
        "status": payment.status.value,
        "is_simulated": payment.is_simulated,
        "reference_number": payment.reference_number,
        "message": "Payment recorded (Simulated for MVP testing)",
    }


@router.get("/order/{order_id}")
async def get_order_payments(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List payment records for an order."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if current_user.id not in [order.buyer_id, order.seller_id] and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    stmt = select(Payment).where(Payment.order_id == order_id).order_by(Payment.created_at.desc())
    p_res = await db.execute(stmt)
    payments = p_res.scalars().all()

    return [
        {
            "id": p.id,
            "order_id": p.order_id,
            "amount": float(p.amount),
            "status": p.status.value,
            "method": p.method.value if hasattr(p.method, "value") else str(p.method),
            "is_simulated": p.is_simulated,
            "reference_number": p.reference_number,
            "paid_at": p.paid_at.isoformat() if p.paid_at else None,
        }
        for p in payments
    ]
