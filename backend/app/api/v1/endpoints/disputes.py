"""Dispute resolution endpoints."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.dispute import Dispute, DisputeStatus
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.schemas.dispute import DisputeCreate, DisputeUpdate
from app.middleware.auth import get_current_user, require_roles

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def raise_dispute(
    data: DisputeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Raise a dispute on an active or completed order."""
    result = await db.execute(select(Order).where(Order.id == data.order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if current_user.id not in [order.buyer_id, order.seller_id]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this order")

    against_user_id = order.seller_id if current_user.id == order.buyer_id else order.buyer_id

    dispute = Dispute(
        order_id=data.order_id,
        raised_by=current_user.id,
        against_user=against_user_id,
        category=data.category,
        description=data.description,
        status=DisputeStatus.OPEN,
    )
    db.add(dispute)
    order.status = OrderStatus.DISPUTED
    await db.flush()
    return {"id": dispute.id, "message": "Dispute submitted to admin review queue"}


@router.get("/")
async def list_disputes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List disputes relevant to current user (or all if admin)."""
    stmt = (
        select(Dispute)
        .options(selectinload(Dispute.order), selectinload(Dispute.raiser), selectinload(Dispute.against))
    )
    if current_user.role != UserRole.ADMIN:
        stmt = stmt.where(
            or_(Dispute.raised_by == current_user.id, Dispute.against_user == current_user.id)
        )
    stmt = stmt.order_by(Dispute.created_at.desc())
    result = await db.execute(stmt)
    disputes = result.scalars().all()

    return [
        {
            "id": d.id,
            "order_id": d.order_id,
            "category": d.category.value,
            "description": d.description,
            "status": d.status.value,
            "resolution": d.resolution,
            "raised_by_name": d.raiser.full_name if d.raiser else "User",
            "against_name": d.against.full_name if d.against else "User",
            "created_at": d.created_at.isoformat(),
            "resolved_at": d.resolved_at.isoformat() if d.resolved_at else None,
        }
        for d in disputes
    ]


@router.patch("/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: int,
    data: DisputeUpdate,
    admin: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Resolve an open dispute (Admin only)."""
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    if not dispute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")

    dispute.status = data.status or DisputeStatus.RESOLVED
    dispute.resolution = data.resolution
    dispute.admin_id = admin.id
    dispute.resolved_at = datetime.now(timezone.utc)
    await db.flush()
    return {"id": dispute.id, "status": dispute.status.value, "message": "Dispute updated"}
