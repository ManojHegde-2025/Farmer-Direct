"""Buyer endpoints."""

from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.buyer_profile import BuyerProfile
from app.models.farmer_profile import VerificationStatus
from app.models.buyer_requirement import BuyerRequirement
from app.models.offer import Offer, OfferStatus
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.schemas.buyer import BuyerProfileUpdate
from app.schemas.farmer import VerificationSubmission
from app.middleware.auth import get_current_user, require_roles

router = APIRouter()


@router.get("/profile")
async def get_buyer_profile(
    current_user: User = Depends(require_roles(UserRole.BUYER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve buyer profile and verification status."""
    stmt = select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        profile = BuyerProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "business_name": profile.business_name,
        "business_type": profile.business_type.value if profile.business_type else None,
        "district": profile.district,
        "taluk": profile.taluk,
        "description": profile.description,
        "verification_status": profile.verification_status.value,
        "gst_number": profile.gst_number,
        "is_verified": current_user.is_verified,
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }


@router.put("/profile")
async def update_buyer_profile(
    data: BuyerProfileUpdate,
    current_user: User = Depends(require_roles(UserRole.BUYER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Update commercial buyer information."""
    stmt = select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        profile = BuyerProfile(user_id=current_user.id)
        db.add(profile)

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, val)

    await db.flush()
    return {"message": "Buyer profile updated successfully"}


@router.post("/verification")
async def submit_buyer_verification(
    data: VerificationSubmission,
    current_user: User = Depends(require_roles(UserRole.BUYER)),
    db: AsyncSession = Depends(get_db),
):
    """Submit business registration or GST documentation for review."""
    stmt = select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        profile = BuyerProfile(user_id=current_user.id)
        db.add(profile)

    profile.verification_status = VerificationStatus.SUBMITTED
    await db.flush()
    return {"status": profile.verification_status.value, "message": "Verification submitted"}


@router.get("/dashboard-stats")
async def get_buyer_stats(
    current_user: User = Depends(require_roles(UserRole.BUYER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Calculate buyer dashboard procurement statistics."""
    # Active requirements
    req_stmt = select(func.count(BuyerRequirement.id)).where(
        BuyerRequirement.buyer_id == current_user.id,
        BuyerRequirement.is_active == True,
    )
    active_reqs = (await db.execute(req_stmt)).scalar() or 0

    # Active pending offers sent
    off_stmt = select(func.count(Offer.id)).where(
        Offer.buyer_id == current_user.id,
        Offer.status == OfferStatus.PENDING,
    )
    pending_offers = (await db.execute(off_stmt)).scalar() or 0

    # Active orders
    ord_stmt = select(func.count(Order.id)).where(
        Order.buyer_id == current_user.id,
        Order.status.in_([
            OrderStatus.CONFIRMED,
            OrderStatus.PAYMENT_PENDING,
            OrderStatus.PAYMENT_CONFIRMED,
            OrderStatus.READY_FOR_PICKUP,
            OrderStatus.DISPATCHED,
            OrderStatus.DELIVERED,
        ]),
    )
    active_orders = (await db.execute(ord_stmt)).scalar() or 0

    # Total procurement spend
    spend_stmt = select(func.sum(Order.total_price)).where(
        Order.buyer_id == current_user.id,
        Order.status == OrderStatus.COMPLETED,
    )
    total_spend = (await db.execute(spend_stmt)).scalar() or Decimal("0.00")

    return {
        "active_requirements_count": active_reqs,
        "pending_offers_count": pending_offers,
        "active_orders_count": active_orders,
        "total_spend": float(total_spend),
    }
