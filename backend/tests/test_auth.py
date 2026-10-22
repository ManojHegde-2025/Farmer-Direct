"""Tests for Authentication and Role Permissions."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_farmer(client: AsyncClient):
    """Test farmer registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "farmer.test@example.com",
            "full_name": "Test Farmer",
            "phone": "+919876543210",
            "password": "Password123!",
            "role": "FARMER",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "farmer.test@example.com"
    assert data["role"] == "FARMER"
    assert "password" not in data


@pytest.mark.asyncio
async def test_cannot_self_register_as_admin(client: AsyncClient):
    """PHASE 5 rule: Users must not be able to assign themselves the ADMIN role."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "hacker@example.com",
            "full_name": "Hacker",
            "password": "Password123!",
            "role": "ADMIN",
        },
    )
    assert response.status_code == 403
    assert "administrator" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_and_me_flow(client: AsyncClient):
    """Test login with JWT retrieval and authenticated /me endpoint."""
    # Register buyer
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "buyer.test@example.com",
            "full_name": "Test Buyer",
            "password": "Password123!",
            "role": "BUYER",
        },
    )

    # Login
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "buyer.test@example.com", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

    # Get /me
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "buyer.test@example.com"
    assert me_data["role"] == "BUYER"
