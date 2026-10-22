"""Farmer endpoints."""

from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.farmer_profile import FarmerProfile, VerificationStatus
from app.models.listing import Listing, ListingStatus
from app.models.offer import Offer, OfferStatus
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.schemas.farmer import FarmerProfileUpdate, VerificationSubmission
from app.middleware.auth import get_current_user, require_roles

router = APIRouter()


@router.get("/profile")
async def get_farmer_profile(
    current_user: User = Depends(require_roles(UserRole.FARMER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve farmer profile and verification status."""
    stmt = select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        profile = FarmerProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "farm_name": profile.farm_name,
        "farm_location": profile.farm_location,
        "district": profile.district.value if profile.district else None,
        "taluk": profile.taluk,
        "village": profile.village,
        "farm_size_acres": float(profile.farm_size_acres) if profile.farm_size_acres else None,
        "primary_crops": profile.primary_crops,
        "description": profile.description,
        "verification_status": profile.verification_status.value,
        "bank_account_verified": profile.bank_account_verified,
        "is_verified": current_user.is_verified,
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }


@router.put("/profile")
async def update_farmer_profile(
    data: FarmerProfileUpdate,
    current_user: User = Depends(require_roles(UserRole.FARMER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Update farm location, acreage, and crop details."""
    stmt = select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        profile = FarmerProfile(user_id=current_user.id)
        db.add(profile)

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, val)

    await db.flush()
    return {"message": "Farmer profile updated successfully"}


@router.post("/verification")
async def submit_verification(
    data: VerificationSubmission,
    current_user: User = Depends(require_roles(UserRole.FARMER)),
    db: AsyncSession = Depends(get_db),
):
    """Submit identity or land documentation for admin verification."""
    stmt = select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        profile = FarmerProfile(user_id=current_user.id)
        db.add(profile)

    profile.verification_document_path = data.verification_document_path
    profile.verification_status = VerificationStatus.SUBMITTED
    await db.flush()
    return {
        "status": profile.verification_status.value,
        "message": "Verification documents submitted successfully for administrative review.",
    }


@router.get("/dashboard-stats")
async def get_farmer_stats(
    current_user: User = Depends(require_roles(UserRole.FARMER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Calculate real-time operational statistics for farmer dashboard."""
    # Active listings
    l_stmt = select(func.count(Listing.id)).where(
        Listing.farmer_id == current_user.id,
        Listing.status.in_([ListingStatus.ACTIVE, ListingStatus.PARTIALLY_RESERVED]),
    )
    active_listings = (await db.execute(l_stmt)).scalar() or 0

    # Pending incoming offers
    o_stmt = select(func.count(Offer.id)).where(
        Offer.seller_id == current_user.id,
        Offer.status == OfferStatus.PENDING,
    )
    pending_offers = (await db.execute(o_stmt)).scalar() or 0

    # Active orders
    ord_stmt = select(func.count(Order.id)).where(
        Order.seller_id == current_user.id,
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

    # Total completed revenue
    rev_stmt = select(func.sum(Order.total_price)).where(
        Order.seller_id == current_user.id,
        Order.status == OrderStatus.COMPLETED,
    )
    total_revenue = (await db.execute(rev_stmt)).scalar() or Decimal("0.00")

    return {
        "active_listings_count": active_listings,
        "pending_offers_count": pending_offers,
        "active_orders_count": active_orders,
        "completed_revenue": float(total_revenue),
    }
