"""Matching API endpoint."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.buyer_requirement import BuyerRequirement
from app.models.listing import Listing
from app.models.user import User
from app.middleware.auth import get_current_user
from app.services.matching import find_matches_for_requirement

router = APIRouter()


@router.get("/requirement/{requirement_id}")
async def get_matches_for_requirement(
    requirement_id: int,
    min_score: float = Query(20.0, ge=0.0, le=100.0),
    sort_by: str = Query("score", pattern="^(score|price|quantity)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Find and rank compatible produce listings for a buyer requirement with full scoring breakdown."""
    stmt = (
        select(BuyerRequirement)
        .options(selectinload(BuyerRequirement.commodity))
        .where(BuyerRequirement.id == requirement_id)
    )
    result = await db.execute(stmt)
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement #{requirement_id} not found",
        )

    matches = await find_matches_for_requirement(db, req, min_score=min_score)

    # Sort results
    if sort_by == "price":
        matches.sort(key=lambda m: m["listing"]["price_per_unit"])
    elif sort_by == "quantity":
        matches.sort(key=lambda m: m["fulfillable_quantity"], reverse=True)
    else:
        matches.sort(key=lambda m: m["match_score"], reverse=True)

    return {
        "requirement_id": req.id,
        "commodity": req.commodity.name if req.commodity else "Commodity",
        "quantity_needed": float(req.quantity_needed),
        "total_matches_found": len(matches),
        "matches": matches,
    }


@router.get("/listing/{listing_id}/buyers")
async def get_matching_buyers_for_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Find active procurement requirements that can be fulfilled by this farmer's listing."""
    stmt = select(Listing).where(Listing.id == listing_id)
    result = await db.execute(stmt)
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    # Find active requirements for same commodity
    r_stmt = (
        select(BuyerRequirement)
        .options(selectinload(BuyerRequirement.buyer), selectinload(BuyerRequirement.commodity))
        .where(
            BuyerRequirement.commodity_id == listing.commodity_id,
            BuyerRequirement.is_active == True,
        )
    )
    r_result = await db.execute(r_stmt)
    requirements = r_result.scalars().all()

    compatible = []
    for req in requirements:
        matches = await find_matches_for_requirement(db, req, min_score=25.0)
        # Check if our listing is in the matches
        for m in matches:
            if m["listing_id"] == listing.id:
                compatible.append({
                    "requirement_id": req.id,
                    "buyer_name": req.buyer.full_name if req.buyer else "Buyer",
                    "quantity_needed": float(req.quantity_needed),
                    "max_price_per_unit": float(req.max_price_per_unit) if req.max_price_per_unit else None,
                    "delivery_location": req.delivery_location,
                    "delivery_district": req.delivery_district,
                    "needed_by": req.needed_by.isoformat() if req.needed_by else None,
                    "match_score": m["match_score"],
                    "match_reasons": m["match_reasons"],
                })

    compatible.sort(key=lambda x: x["match_score"], reverse=True)
    return {
        "listing_id": listing.id,
        "compatible_requirements_count": len(compatible),
        "requirements": compatible,
    }
