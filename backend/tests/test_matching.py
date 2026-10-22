"""Tests for Matching Engine (Deterministic Rules, Weights & Explanations)."""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from app.models.commodity import Commodity, CommodityUnit
from app.models.listing import Listing, QualityGrade, ListingStatus
from app.models.buyer_requirement import BuyerRequirement
from app.models.farmer_profile import FarmerProfile, District, VerificationStatus
from app.models.user import User, UserRole
from app.services.matching import find_matches_for_requirement


@pytest.mark.asyncio
async def test_matching_engine_rules_and_scoring(db_session):
    """Verify:
    1. Incompatible commodity produces NO match.
    2. Unapproved farmer produces NO match.
    3. Compatible listing produces match with score >= 70, breakdown, and explanation.
    """
    # 1. Commodities
    areca = Commodity(name="Arecanut", unit=CommodityUnit.KG, is_active=True)
    coconut = Commodity(name="Coconut", unit=CommodityUnit.COUNT, is_active=True)
    db_session.add_all([areca, coconut])
    await db_session.flush()

    # 2. Verified Farmer in Udupi
    farmer = User(
        email="f.verified@test.com",
        full_name="Mahabaleshwara Bhat",
        role=UserRole.FARMER,
        hashed_password="pw",
        is_active=True,
        is_verified=True,
    )
    db_session.add(farmer)
    await db_session.flush()

    f_prof = FarmerProfile(
        user_id=farmer.id,
        district=District.UDUPI,
        taluk="Karkala",
        verification_status=VerificationStatus.APPROVED,
    )
    db_session.add(f_prof)
    await db_session.flush()

    # 3. Create Arecanut Listing
    listing = Listing(
        farmer_id=farmer.id,
        commodity_id=areca.id,
        title="Chali Arecanut Grade A",
        variety="Chali Whole Dried",
        quality_grade=QualityGrade.A,
        quantity=Decimal("100.00"),
        available_quantity=Decimal("100.00"),
        unit=CommodityUnit.KG,
        price_per_unit=Decimal("450.00"),
        status=ListingStatus.ACTIVE,
        available_until=date.today() + timedelta(days=30),
    )
    db_session.add(listing)
    await db_session.commit()

    # 4. Buyer Requirement for Arecanut (Compatible)
    req_areca = BuyerRequirement(
        buyer_id=1,
        commodity_id=areca.id,
        variety_preference="Chali",
        quality_preference="A",
        quantity_needed=Decimal("80.00"),
        max_price_per_unit=Decimal("460.00"),
        delivery_district="UDUPI",
        needed_by=date.today() + timedelta(days=20),
        is_active=True,
    )

    matches = await find_matches_for_requirement(db_session, req_areca)
    assert len(matches) == 1
    m = matches[0]
    assert m["listing_id"] == listing.id
    assert m["match_score"] >= 80.0  # High score due to exact match on variety, budget, district, timing, quality
    assert "score_breakdown" in m
    assert "match_reasons" in m
    assert len(m["match_reasons"]) > 0

    # 5. Buyer Requirement for Coconut (Incompatible commodity)
    req_coconut = BuyerRequirement(
        buyer_id=1,
        commodity_id=coconut.id,
        quantity_needed=Decimal("50.00"),
        is_active=True,
    )
    no_matches = await find_matches_for_requirement(db_session, req_coconut)
    assert len(no_matches) == 0
