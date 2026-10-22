"""Tests for Offers, Negotiation, Order creation, and Stock Oversell Prevention."""

import pytest
from httpx import AsyncClient
from decimal import Decimal
from sqlalchemy import select
from app.models.commodity import Commodity, CommodityUnit
from app.models.listing import Listing, ListingStatus
from app.models.farmer_profile import FarmerProfile, VerificationStatus
from app.models.user import User


@pytest.mark.asyncio
async def test_offer_acceptance_and_stock_reservation(client: AsyncClient, db_session):
    """End-to-end negotiation:
    1. Farmer lists 100 kg Arecanut.
    2. Buyer offers for 80 kg.
    3. Farmer counters.
    4. Buyer accepts counter.
    5. Order created for 80 kg, remaining stock is exactly 20 kg.
    6. Another buyer tries to buy 30 kg -> rejected (oversell prevented)!
    """
    # 1. Setup Commodity
    c = Commodity(name="Arecanut", unit=CommodityUnit.KG, is_active=True)
    db_session.add(c)
    await db_session.commit()

    # 2. Register Farmer & Buyer
    await client.post(
        "/api/v1/auth/register",
        json={"email": "farmer@test.com", "full_name": "Farmer", "password": "Password123!", "role": "FARMER"},
    )
    f_login = await client.post("/api/v1/auth/login", json={"email": "farmer@test.com", "password": "Password123!"})
    f_token = f_login.json()["access_token"]

    # Mark farmer verified so listing is ACTIVE
    f_res = await db_session.execute(select(User).where(User.email == "farmer@test.com"))
    f_user = f_res.scalar_one()
    f_user.is_verified = True
    prof_res = await db_session.execute(select(FarmerProfile).where(FarmerProfile.user_id == f_user.id))
    prof = prof_res.scalar_one()
    prof.verification_status = VerificationStatus.APPROVED
    await db_session.commit()

    # Create listing of 100 kg
    l_res = await client.post(
        "/api/v1/listings/",
        headers={"Authorization": f"Bearer {f_token}"},
        json={"commodity_id": c.id, "title": "Arecanut 100 kg", "quantity": 100.0, "unit": "KG", "price_per_unit": 450.0},
    )
    assert l_res.status_code == 201
    listing_id = l_res.json()["id"]
    assert l_res.json()["status"] == "ACTIVE"

    # Register Buyer 1
    await client.post(
        "/api/v1/auth/register",
        json={"email": "buyer1@test.com", "full_name": "Buyer 1", "password": "Password123!", "role": "BUYER"},
    )
    b1_login = await client.post("/api/v1/auth/login", json={"email": "buyer1@test.com", "password": "Password123!"})
    b1_token = b1_login.json()["access_token"]

    # Buyer 1 submits offer for 80 kg @ ₹430
    off_res = await client.post(
        "/api/v1/offers/",
        headers={"Authorization": f"Bearer {b1_token}"},
        json={"listing_id": listing_id, "quantity": 80.0, "price_per_unit": 430.0, "delivery_method": "BUYER_PICKUP"},
    )
    assert off_res.status_code == 201
    offer_id = off_res.json()["id"]

    # Farmer counters with ₹440
    counter_res = await client.post(
        f"/api/v1/offers/{offer_id}/counter",
        headers={"Authorization": f"Bearer {f_token}"},
        json={"quantity": 80.0, "price_per_unit": 440.0, "message": "Best rate for 80kg"},
    )
    assert counter_res.status_code == 201
    counter_id = counter_res.json()["id"]

    # Buyer 1 accepts counter-offer
    accept_res = await client.post(
        f"/api/v1/offers/{counter_id}/accept",
        headers={"Authorization": f"Bearer {b1_token}"},
    )
    assert accept_res.status_code == 200
    order_id = accept_res.json()["order_id"]
    assert accept_res.json()["reserved_quantity"] == 80.0

    # Verify listing now has 20 kg available and status PARTIALLY_RESERVED
    list_check = await client.get(f"/api/v1/listings/{listing_id}")
    assert list_check.status_code == 200
    assert list_check.json()["available_quantity"] == 20.0
    assert list_check.json()["status"] == "PARTIALLY_RESERVED"

    # Register Buyer 2
    await client.post(
        "/api/v1/auth/register",
        json={"email": "buyer2@test.com", "full_name": "Buyer 2", "password": "Password123!", "role": "BUYER"},
    )
    b2_login = await client.post("/api/v1/auth/login", json={"email": "buyer2@test.com", "password": "Password123!"})
    b2_token = b2_login.json()["access_token"]

    # Buyer 2 tries to order 30 kg (only 20 kg left) -> MUST BE REJECTED!
    oversell_res = await client.post(
        "/api/v1/offers/",
        headers={"Authorization": f"Bearer {b2_token}"},
        json={"listing_id": listing_id, "quantity": 30.0, "price_per_unit": 450.0},
    )
    assert oversell_res.status_code == 400
    assert "exceeds available stock" in oversell_res.json()["detail"].lower()
