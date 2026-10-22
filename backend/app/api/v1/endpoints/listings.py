"""Listing endpoints for Farmers and Marketplace."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.listing import Listing, ListingStatus, QualityGrade
from app.models.commodity import Commodity
from app.models.farmer_profile import FarmerProfile, District, VerificationStatus
from app.models.user import User, UserRole
from app.schemas.listing import (
    ListingCreate,
    ListingRead,
    ListingUpdate,
    ListingStatusUpdate,
)
from app.middleware.auth import (
    get_current_user,
    get_optional_current_user,
    require_roles,
)

router = APIRouter()


@router.get("/")
async def list_listings(
    q: Optional[str] = Query(None, description="Search query on title or description"),
    commodity_id: Optional[int] = Query(None, description="Filter by commodity ID"),
    district: Optional[District] = Query(None, description="Filter by district"),
    min_price: Optional[Decimal] = Query(None, description="Minimum price per unit"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price per unit"),
    min_quantity: Optional[Decimal] = Query(None, description="Minimum available quantity"),
    status_filter: Optional[ListingStatus] = Query(None, description="Filter by status (default: ACTIVE)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Browse and search listings with multiple agricultural marketplace filters."""
    stmt = (
        select(Listing)
        .options(
            selectinload(Listing.commodity),
            selectinload(Listing.farmer).selectinload(User.farmer_profile),
        )
    )

    conditions = []

    # Default to ACTIVE listings for marketplace browsing unless explicitly requested
    if status_filter:
        conditions.append(Listing.status == status_filter)
    else:
        conditions.append(Listing.status.in_([ListingStatus.ACTIVE, ListingStatus.PARTIALLY_RESERVED]))

    if commodity_id:
        conditions.append(Listing.commodity_id == commodity_id)

    if q:
        search_pattern = f"%{q}%"
        conditions.append(
            or_(
                Listing.title.ilike(search_pattern),
                Listing.variety.ilike(search_pattern),
                Listing.description.ilike(search_pattern),
            )
        )

    if min_price is not None:
        conditions.append(Listing.price_per_unit >= min_price)

    if max_price is not None:
        conditions.append(Listing.price_per_unit <= max_price)

    if min_quantity is not None:
        conditions.append(Listing.available_quantity >= min_quantity)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.order_by(Listing.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    listings = result.scalars().all()

    # Apply district filter in memory or via join if specified
    items = []
    for l in listings:
        f_prof = l.farmer.farmer_profile if l.farmer else None
        if district and f_prof and f_prof.district != district:
            continue

        items.append({
            "id": l.id,
            "title": l.title,
            "commodity_id": l.commodity_id,
            "commodity_name": l.commodity.name if l.commodity else None,
            "commodity_name_kn": l.commodity.name_kn if l.commodity else None,
            "variety": l.variety,
            "quality_grade": l.quality_grade.value,
            "quantity": float(l.quantity),
            "available_quantity": float(l.available_quantity),
            "unit": l.unit.value if hasattr(l.unit, "value") else str(l.unit),
            "price_per_unit": float(l.price_per_unit),
            "min_order_quantity": float(l.min_order_quantity) if l.min_order_quantity else None,
            "images": l.images,
            "status": l.status.value,
            "available_from": l.available_from.isoformat() if l.available_from else None,
            "available_until": l.available_until.isoformat() if l.available_until else None,
            "pickup_location": l.pickup_location,
            "delivery_available": l.delivery_available,
            "farmer": {
                "id": l.farmer.id if l.farmer else None,
                "full_name": l.farmer.full_name if l.farmer else "Farmer",
                "district": f_prof.district.value if f_prof and f_prof.district else None,
                "taluk": f_prof.taluk if f_prof else None,
                "is_verified": l.farmer.is_verified if l.farmer else False,
            },
            "created_at": l.created_at.isoformat(),
        })

    return items


@router.get("/{listing_id}")
async def get_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve full details for a single produce listing."""
    stmt = (
        select(Listing)
        .options(
            selectinload(Listing.commodity),
            selectinload(Listing.farmer).selectinload(User.farmer_profile),
        )
        .where(Listing.id == listing_id)
    )
    result = await db.execute(stmt)
    l = result.scalar_one_or_none()
    if not l:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing #{listing_id} not found",
        )

    f_prof = l.farmer.farmer_profile if l.farmer else None
    return {
        "id": l.id,
        "title": l.title,
        "description": l.description,
        "commodity_id": l.commodity_id,
        "commodity": {
            "id": l.commodity.id,
            "name": l.commodity.name,
            "name_kn": l.commodity.name_kn,
            "category": l.commodity.category,
            "unit": l.commodity.unit.value,
            "icon": l.commodity.icon,
        } if l.commodity else None,
        "variety": l.variety,
        "quality_grade": l.quality_grade.value,
        "quantity": float(l.quantity),
        "available_quantity": float(l.available_quantity),
        "unit": l.unit.value if hasattr(l.unit, "value") else str(l.unit),
        "price_per_unit": float(l.price_per_unit),
        "min_order_quantity": float(l.min_order_quantity) if l.min_order_quantity else None,
        "images": l.images,
        "status": l.status.value,
        "harvest_date": l.harvest_date.isoformat() if l.harvest_date else None,
        "available_from": l.available_from.isoformat() if l.available_from else None,
        "available_until": l.available_until.isoformat() if l.available_until else None,
        "pickup_location": l.pickup_location,
        "delivery_available": l.delivery_available,
        "delivery_radius_km": l.delivery_radius_km,
        "farmer": {
            "id": l.farmer.id if l.farmer else None,
            "full_name": l.farmer.full_name if l.farmer else "Farmer",
            "district": f_prof.district.value if f_prof and f_prof.district else None,
            "taluk": f_prof.taluk if f_prof else None,
            "village": f_prof.village if f_prof else None,
            "farm_name": f_prof.farm_name if f_prof else None,
            "is_verified": l.farmer.is_verified if l.farmer else False,
        },
        "created_at": l.created_at.isoformat(),
        "updated_at": l.updated_at.isoformat(),
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_listing(
    data: ListingCreate,
    current_user: User = Depends(require_roles(UserRole.FARMER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Create a produce listing. Unverified farmers cannot publish directly to ACTIVE."""
    # Check commodity exists
    comm = await db.execute(select(Commodity).where(Commodity.id == data.commodity_id))
    if not comm.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commodity #{data.commodity_id} does not exist",
        )

    # Check farmer verification status
    stmt = select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    # Rule: Do not allow unapproved farmers to publish active listings
    if not current_user.is_verified and (not profile or profile.verification_status != VerificationStatus.APPROVED):
        initial_status = ListingStatus.PENDING_REVIEW
    else:
        initial_status = ListingStatus.ACTIVE

    listing = Listing(
        farmer_id=current_user.id,
        commodity_id=data.commodity_id,
        title=data.title,
        description=data.description,
        variety=data.variety,
        quality_grade=data.quality_grade,
        quantity=data.quantity,
        available_quantity=data.quantity,
        unit=data.unit,
        price_per_unit=data.price_per_unit,
        min_order_quantity=data.min_order_quantity,
        images=data.images,
        status=initial_status,
        harvest_date=data.harvest_date,
        available_from=data.available_from,
        available_until=data.available_until,
        pickup_location=data.pickup_location,
        delivery_available=data.delivery_available,
        delivery_radius_km=data.delivery_radius_km,
    )
    db.add(listing)
    await db.flush()
    return {
        "id": listing.id,
        "title": listing.title,
        "status": listing.status.value,
        "available_quantity": float(listing.available_quantity),
        "price_per_unit": float(listing.price_per_unit),
        "message": (
            "Listing created and is now ACTIVE"
            if initial_status == ListingStatus.ACTIVE
            else "Listing created and is PENDING_REVIEW awaiting administrator verification"
        ),
    }


@router.put("/{listing_id}")
async def update_listing(
    listing_id: int,
    data: ListingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a listing. Enforces farmer ownership."""
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing #{listing_id} not found",
        )

    # Ownership check: buyers cannot edit farmer's listing; only owner or admin can
    if listing.farmer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this listing",
        )

    for field, val in data.model_dump(exclude_unset=True).items():
        if field == "quantity" and val is not None:
            # Adjust available_quantity proportionately if total quantity changed
            diff = val - listing.quantity
            listing.quantity = val
            listing.available_quantity = max(Decimal("0.00"), listing.available_quantity + diff)
        else:
            setattr(listing, field, val)

    await db.flush()
    return {"message": "Listing updated successfully", "id": listing.id}


@router.patch("/{listing_id}/status")
async def update_listing_status(
    listing_id: int,
    status_data: ListingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pause, deactivate, or activate a listing."""
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing #{listing_id} not found",
        )

    if listing.farmer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this listing status",
        )

    listing.status = status_data.status
    await db.flush()
    return {"id": listing.id, "status": listing.status.value}
