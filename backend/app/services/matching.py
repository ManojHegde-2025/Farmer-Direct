"""Matching engine for buyer requirements and produce listings.

Deterministic rules-based scoring with explainable recommendations.
PHASE 10 specification:
- Commodity and variety: 25%
- Quantity: 20%
- Price: 20%
- Location: 15%
- Timing: 10%
- Quality: 10%
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing, ListingStatus, QualityGrade
from app.models.buyer_requirement import BuyerRequirement
from app.models.farmer_profile import FarmerProfile, VerificationStatus
from app.models.user import User


class MatchScore:
    def __init__(
        self,
        listing: Listing,
        total_score: float,
        breakdown: Dict[str, float],
        reasons: List[str],
        fulfillable_quantity: Decimal,
    ):
        self.listing = listing
        self.total_score = round(total_score, 1)
        self.breakdown = breakdown
        self.reasons = reasons
        self.fulfillable_quantity = fulfillable_quantity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "listing_id": self.listing.id,
            "listing": {
                "id": self.listing.id,
                "title": self.listing.title,
                "commodity_id": self.listing.commodity_id,
                "variety": self.listing.variety,
                "quality_grade": self.listing.quality_grade.value,
                "price_per_unit": float(self.listing.price_per_unit),
                "available_quantity": float(self.listing.available_quantity),
                "unit": self.listing.unit,
                "pickup_location": self.listing.pickup_location,
                "delivery_available": self.listing.delivery_available,
                "status": self.listing.status.value,
                "farmer": {
                    "id": self.listing.farmer.id if self.listing.farmer else None,
                    "name": self.listing.farmer.full_name if self.listing.farmer else "Unknown",
                    "district": (
                        self.listing.farmer.farmer_profile.district.value
                        if self.listing.farmer and self.listing.farmer.farmer_profile and self.listing.farmer.farmer_profile.district
                        else None
                    ),
                    "taluk": (
                        self.listing.farmer.farmer_profile.taluk
                        if self.listing.farmer and self.listing.farmer.farmer_profile
                        else None
                    ),
                    "is_verified": self.listing.farmer.is_verified if self.listing.farmer else False,
                }
            },
            "match_score": self.total_score,
            "score_breakdown": self.breakdown,
            "match_reasons": self.reasons,
            "explanation": " • ".join(self.reasons) if self.reasons else "Compatible match",
            "fulfillable_quantity": float(self.fulfillable_quantity),
        }


async def find_matches_for_requirement(
    db: AsyncSession,
    requirement: BuyerRequirement,
    min_score: float = 30.0,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Find and rank matching listings for a buyer requirement using deterministic rules."""
    # 1. Fetch Candidate Listings with eager loads
    stmt = (
        select(Listing)
        .options(
            selectinload(Listing.farmer).selectinload(User.farmer_profile),
            selectinload(Listing.commodity),
        )
        .where(
            and_(
                Listing.commodity_id == requirement.commodity_id,
                Listing.status == ListingStatus.ACTIVE,
                Listing.available_quantity > 0,
            )
        )
    )
    result = await db.execute(stmt)
    candidates = result.scalars().all()

    matches: List[MatchScore] = []

    for listing in candidates:
        farmer = listing.farmer
        profile: Optional[FarmerProfile] = farmer.farmer_profile if farmer else None

        # Hard Constraint: Farmer Verification / Eligibility
        # Unapproved or suspended farmers should not match active procurement requirements
        if profile and profile.verification_status != VerificationStatus.APPROVED and not farmer.is_verified:
            continue

        # Hard Constraint: Available quantity must be positive
        if listing.available_quantity <= Decimal("0"):
            continue

        # Hard Constraint: Expiration date
        today = date.today()
        if listing.available_until and listing.available_until < today:
            continue

        # Evaluate Component Scores
        breakdown: Dict[str, float] = {}
        reasons: List[str] = []

        # 1. Commodity & Variety (Weight: 25%)
        # Commodity matches by query. Variety check:
        variety_score = 15.0  # Base for matching commodity
        if requirement.variety_preference:
            if listing.variety and requirement.variety_preference.lower() in listing.variety.lower():
                variety_score = 25.0
                reasons.append(f"Exact variety match: {listing.variety}")
            else:
                variety_score = 12.0
                reasons.append(f"Produce matches commodity, variety differs ({listing.variety or 'Standard'})")
        else:
            variety_score = 25.0
            reasons.append("Produce commodity matches requested requirement")
        breakdown["commodity_variety"] = variety_score

        # 2. Quantity (Weight: 20%)
        req_qty = requirement.quantity_needed
        avail_qty = listing.available_quantity
        fulfillable_qty = min(req_qty, avail_qty)

        if avail_qty >= req_qty:
            quantity_score = 20.0
            reasons.append(f"Can fulfill 100% of requested quantity ({req_qty} {listing.unit})")
        else:
            pct = float(avail_qty / req_qty)
            quantity_score = max(5.0, round(pct * 20.0, 1))
            reasons.append(f"Partial fulfillment: {avail_qty} of {req_qty} {listing.unit} ({int(pct*100)}%)")
        breakdown["quantity"] = quantity_score

        # 3. Price (Weight: 20%)
        if requirement.max_price_per_unit is not None and requirement.max_price_per_unit > 0:
            max_p = requirement.max_price_per_unit
            list_p = listing.price_per_unit
            if list_p <= max_p:
                price_ratio = float((max_p - list_p) / max_p)
                price_score = min(20.0, 15.0 + (price_ratio * 10.0))  # Better price yields higher score
                price_score = round(price_score, 1)
                savings = max_p - list_p
                if savings > 0:
                    reasons.append(f"Asking price ₹{list_p} is below your budget of ₹{max_p} (Save ₹{savings}/unit)")
                else:
                    reasons.append(f"Asking price ₹{list_p} meets your maximum budget")
            elif list_p <= max_p * Decimal("1.10"):
                price_score = 8.0
                reasons.append(f"Price ₹{list_p} is within 10% of budget (Negotiation recommended)")
            else:
                price_score = 0.0
                reasons.append(f"Price ₹{list_p} exceeds budget of ₹{max_p}")
        else:
            price_score = 15.0  # Neutral if buyer didn't specify maximum price
            reasons.append(f"Asking price: ₹{listing.price_per_unit}/{listing.unit}")
        breakdown["price"] = price_score

        # 4. Location (Weight: 15%)
        location_score = 5.0
        buyer_district = (
            requirement.delivery_district.value
            if hasattr(requirement.delivery_district, "value")
            else str(requirement.delivery_district) if requirement.delivery_district else None
        )
        farmer_district = (
            profile.district.value
            if profile and hasattr(profile.district, "value")
            else str(profile.district) if profile and profile.district else None
        )

        if buyer_district and farmer_district:
            if buyer_district.upper() == farmer_district.upper():
                location_score = 15.0
                reasons.append(f"Local producer in {farmer_district} district (Low transport distance)")
            else:
                location_score = 8.0
                reasons.append(f"Producer in adjacent coastal district ({farmer_district})")
        else:
            location_score = 10.0
        breakdown["location"] = location_score

        # 5. Timing (Weight: 10%)
        timing_score = 10.0
        if requirement.needed_by:
            if listing.available_from and listing.available_from > requirement.needed_by:
                timing_score = 2.0
                reasons.append(f"Available after needed date ({listing.available_from})")
            elif listing.available_until and listing.available_until < requirement.needed_by:
                timing_score = 6.0
                reasons.append(f"Harvest available until {listing.available_until}")
            else:
                timing_score = 10.0
                reasons.append("Available within required procurement timeframe")
        else:
            timing_score = 10.0
        breakdown["timing"] = timing_score

        # 6. Quality (Weight: 10%)
        quality_score = 7.0
        if requirement.quality_preference:
            pref = requirement.quality_preference.upper()
            grade = listing.quality_grade.value.upper()
            if pref == grade:
                quality_score = 10.0
                reasons.append(f"Matches desired quality grade {grade}")
            elif pref in ["B", "C"] and grade == "A":
                quality_score = 10.0
                reasons.append(f"Exceeds requested quality (Grade A produce)")
            else:
                quality_score = 5.0
                reasons.append(f"Grade {grade} produce available")
        else:
            quality_score = 8.0
            reasons.append(f"Grade {listing.quality_grade.value} certified")
        breakdown["quality"] = quality_score

        total_score = sum(breakdown.values())

        if total_score >= min_score:
            matches.append(
                MatchScore(
                    listing=listing,
                    total_score=total_score,
                    breakdown=breakdown,
                    reasons=reasons,
                    fulfillable_quantity=fulfillable_qty,
                )
            )

    # Sort descending by match score
    matches.sort(key=lambda m: m.total_score, reverse=True)
    return [m.to_dict() for m in matches[:limit]]
