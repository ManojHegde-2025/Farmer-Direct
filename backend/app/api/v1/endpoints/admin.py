"""Administrator dashboard and moderation endpoints."""

from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User, UserRole
from app.models.farmer_profile import FarmerProfile, VerificationStatus
from app.models.buyer_profile import BuyerProfile
from app.models.listing import Listing, ListingStatus
from app.models.order import Order, OrderStatus
from app.models.dispute import Dispute, DisputeStatus
from app.models.audit_log import AuditLog
from app.schemas.farmer import VerificationDecision
from app.schemas.user import UserAdminUpdate
from app.middleware.auth import require_roles

router = APIRouter()


@router.get("/stats")
async def get_admin_platform_stats(
    admin: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve verified platform metrics calculated from actual database records."""
    # User counts
    total_farmers = (await db.execute(select(func.count(User.id)).where(User.role == UserRole.FARMER))).scalar() or 0
    total_buyers = (await db.execute(select(func.count(User.id)).where(User.role == UserRole.BUYER))).scalar() or 0

    # Pending verifications
    pending_farmer_v = (await db.execute(
        select(func.count(FarmerProfile.id)).where(FarmerProfile.verification_status.in_([VerificationStatus.SUBMITTED, VerificationStatus.PENDING]))
    )).scalar() or 0
    pending_buyer_v = (await db.execute(
        select(func.count(BuyerProfile.id)).where(BuyerProfile.verification_status.in_([VerificationStatus.SUBMITTED, VerificationStatus.PENDING]))
    )).scalar() or 0

    # Listings
    active_listings = (await db.execute(
        select(func.count(Listing.id)).where(Listing.status.in_([ListingStatus.ACTIVE, ListingStatus.PARTIALLY_RESERVED]))
    )).scalar() or 0
    pending_listings = (await db.execute(
        select(func.count(Listing.id)).where(Listing.status == ListingStatus.PENDING_REVIEW)
    )).scalar() or 0

    # Orders & Trade volume
    total_orders = (await db.execute(select(func.count(Order.id)))).scalar() or 0
    total_gmv = (await db.execute(
        select(func.sum(Order.total_price)).where(Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.DELIVERED, OrderStatus.COMPLETED]))
    )).scalar() or Decimal("0.00")

    # Disputes
    open_disputes = (await db.execute(
        select(func.count(Dispute.id)).where(Dispute.status == DisputeStatus.OPEN)
    )).scalar() or 0

    return {
        "total_farmers": total_farmers,
        "total_buyers": total_buyers,
        "pending_verifications": pending_farmer_v + pending_buyer_v,
        "active_listings": active_listings,
        "pending_listings_moderation": pending_listings,
        "total_orders": total_orders,
        "total_trade_volume_inr": float(total_gmv),
        "open_disputes_count": open_disputes,
    }


@router.get("/verifications")
async def list_pending_verifications(
    admin: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve queue of users awaiting identity / land credential verification."""
    # Farmer queue
    f_stmt = (
        select(FarmerProfile)
        .options(selectinload(FarmerProfile.user))
        .where(FarmerProfile.verification_status.in_([VerificationStatus.SUBMITTED, VerificationStatus.PENDING]))
    )
    f_res = await db.execute(f_stmt)
    farmers = f_res.scalars().all()

    # Buyer queue
    b_stmt = (
        select(BuyerProfile)
        .options(selectinload(BuyerProfile.user))
        .where(BuyerProfile.verification_status.in_([VerificationStatus.SUBMITTED, VerificationStatus.PENDING]))
    )
    b_res = await db.execute(b_stmt)
    buyers = b_res.scalars().all()

    return {
        "farmers": [
            {
                "profile_id": f.id,
                "user_id": f.user_id,
                "full_name": f.user.full_name if f.user else "Farmer",
                "email": f.user.email if f.user else "",
                "farm_name": f.farm_name,
                "district": f.district.value if f.district else None,
                "taluk": f.taluk,
                "village": f.village,
                "farm_size_acres": float(f.farm_size_acres) if f.farm_size_acres else None,
                "primary_crops": f.primary_crops,
                "verification_status": f.verification_status.value,
                "verification_document_path": f.verification_document_path,
                "created_at": f.created_at.isoformat(),
            }
            for f in farmers
        ],
        "buyers": [
            {
                "profile_id": b.id,
                "user_id": b.user_id,
                "full_name": b.user.full_name if b.user else "Buyer",
                "email": b.user.email if b.user else "",
                "business_name": b.business_name,
                "business_type": b.business_type.value if b.business_type else None,
                "district": b.district,
                "gst_number": b.gst_number,
                "verification_status": b.verification_status.value,
                "created_at": b.created_at.isoformat(),
            }
            for b in buyers
        ],
    }


@router.patch("/verify/farmer/{profile_id}")
async def decide_farmer_verification(
    profile_id: int,
    decision: VerificationDecision,
    admin: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject farmer credential verification."""
    stmt = (
        select(FarmerProfile)
        .options(selectinload(FarmerProfile.user))
        .where(FarmerProfile.id == profile_id)
    )
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    profile.verification_status = decision.status
    if profile.user:
        profile.user.is_verified = (decision.status == VerificationStatus.APPROVED)

    # If approved, auto-activate any pending review listings by this farmer
    if decision.status == VerificationStatus.APPROVED:
        l_stmt = select(Listing).where(
            Listing.farmer_id == profile.user_id,
            Listing.status == ListingStatus.PENDING_REVIEW,
        )
        l_res = await db.execute(l_stmt)
        for listing in l_res.scalars().all():
            listing.status = ListingStatus.ACTIVE

    # Create audit log
    log = AuditLog(
        user_id=admin.id,
        action=f"VERIFICATION_{decision.status.value}",
        entity_type="farmer_profile",
        entity_id=profile.id,
        details={"status": decision.status.value, "reason": decision.reason},
    )
    db.add(log)

    await db.flush()
    return {"message": f"Farmer profile marked {decision.status.value}"}


@router.patch("/verify/buyer/{profile_id}")
async def decide_buyer_verification(
    profile_id: int,
    decision: VerificationDecision,
    admin: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject commercial buyer verification."""
    stmt = (
        select(BuyerProfile)
        .options(selectinload(BuyerProfile.user))
        .where(BuyerProfile.id == profile_id)
    )
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    profile.verification_status = decision.status
    if profile.user:
        profile.user.is_verified = (decision.status == VerificationStatus.APPROVED)

    log = AuditLog(
        user_id=admin.id,
        action=f"VERIFICATION_{decision.status.value}",
        entity_type="buyer_profile",
        entity_id=profile.id,
        details={"status": decision.status.value, "reason": decision.reason},
    )
    db.add(log)

    await db.flush()
    return {"message": f"Buyer profile marked {decision.status.value}"}


@router.get("/users")
async def list_all_users(
    role: Optional[UserRole] = None,
    admin: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """List all platform accounts with status and verification state."""
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    stmt = stmt.order_by(User.created_at.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()

    return [
        {
            "id": u.id,
            "email": u.email,
            "phone": u.phone,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.patch("/users/{user_id}")
async def update_user_status(
    user_id: int,
    data: UserAdminUpdate,
    admin: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Suspend, reactivate, or update user permissions."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(user, field, val)

    await db.flush()
    return {"message": f"User #{user.id} updated"}
