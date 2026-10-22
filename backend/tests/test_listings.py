"""Tests for Listings, Ownership Permissions, and Verification Rules."""

import pytest
from httpx import AsyncClient
from app.models.commodity import Commodity, CommodityUnit
from app.models.farmer_profile import District


@pytest.mark.asyncio
async def test_unapproved_farmer_cannot_publish_active_listing(client: AsyncClient, db_session):
    """PHASE 6 & PHASE 18 rule: Unapproved farmer listing is saved as PENDING_REVIEW."""
    # Seed commodity
    c = Commodity(name="Arecanut", unit=CommodityUnit.KG, is_active=True)
    db_session.add(c)
    await db_session.commit()

    # Register new farmer (unverified)
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new.farmer@example.com",
            "full_name": "New Farmer",
            "password": "Password123!",
            "role": "FARMER",
        },
    )
    assert reg.status_code == 201

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "new.farmer@example.com", "password": "Password123!"},
    )
    token = login.json()["access_token"]

    # Create listing
    res = await client.post(
        "/api/v1/listings/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "commodity_id": c.id,
            "title": "Unverified 100 kg Arecanut",
            "quantity": 100.0,
            "unit": "KG",
            "price_per_unit": 450.0,
        },
    )
    assert res.status_code == 201
    assert res.json()["status"] == "PENDING_REVIEW"


@pytest.mark.asyncio
async def test_buyer_cannot_edit_farmer_listing(client: AsyncClient, db_session):
    """PHASE 18 rule 1: A buyer cannot edit a farmer's listing."""
    # Seed commodity
    c = Commodity(name="Coconut", unit=CommodityUnit.COUNT, is_active=True)
    db_session.add(c)
    await db_session.commit()

    # Register farmer
    await client.post(
        "/api/v1/auth/register",
        json={"email": "f@test.com", "full_name": "Farmer", "password": "Password123!", "role": "FARMER"},
    )
    f_login = await client.post("/api/v1/auth/login", json={"email": "f@test.com", "password": "Password123!"})
    f_token = f_login.json()["access_token"]

    # Farmer creates listing
    listing_res = await client.post(
        "/api/v1/listings/",
        headers={"Authorization": f"Bearer {f_token}"},
        json={"commodity_id": c.id, "title": "Farmer Coconut", "quantity": 100.0, "unit": "COUNT", "price_per_unit": 25.0},
    )
    listing_id = listing_res.json()["id"]

    # Register buyer
    await client.post(
        "/api/v1/auth/register",
        json={"email": "b@test.com", "full_name": "Buyer", "password": "Password123!", "role": "BUYER"},
    )
    b_login = await client.post("/api/v1/auth/login", json={"email": "b@test.com", "password": "Password123!"})
    b_token = b_login.json()["access_token"]

    # Buyer attempts to edit farmer's listing
    edit_res = await client.put(
        f"/api/v1/listings/{listing_id}",
        headers={"Authorization": f"Bearer {b_token}"},
        json={"title": "Hacked Title"},
    )
    assert edit_res.status_code == 403
    assert "not own" in edit_res.json()["detail"].lower()
