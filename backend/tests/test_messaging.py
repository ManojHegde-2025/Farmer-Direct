"""Automated Security and Functional Tests for Buyer-Farmer Private Messaging."""

import pytest
from httpx import AsyncClient
from decimal import Decimal
from sqlalchemy import select

from app.models.commodity import Commodity, CommodityUnit
from app.models.listing import Listing, ListingStatus
from app.models.farmer_profile import FarmerProfile, VerificationStatus
from app.models.order import Order, OrderStatus
from app.models.conversation import Conversation, Message
from app.models.user import User


async def setup_test_marketplace(client: AsyncClient, db_session):
    """Helper to set up a commodity, verified farmer, buyer, listing, offer, and accepted order."""
    # 1. Commodity
    c = Commodity(name="Arecanut (Mangalore Supari)", unit=CommodityUnit.KG, is_active=True)
    db_session.add(c)
    await db_session.commit()

    # 2. Farmer
    await client.post(
        "/api/v1/auth/register",
        json={"email": "farmer_msg@test.com", "full_name": "Ramesh Rai", "password": "Password123!", "role": "FARMER"},
    )
    f_login = await client.post("/api/v1/auth/login", json={"email": "farmer_msg@test.com", "password": "Password123!"})
    f_token = f_login.json()["access_token"]

    f_res = await db_session.execute(select(User).where(User.email == "farmer_msg@test.com"))
    farmer_user = f_res.scalar_one()
    farmer_user.is_verified = True
    prof_res = await db_session.execute(select(FarmerProfile).where(FarmerProfile.user_id == farmer_user.id))
    prof = prof_res.scalar_one()
    prof.verification_status = VerificationStatus.APPROVED
    prof.farm_name = "Rai Betel Farms"
    await db_session.commit()

    # 3. Listing
    l_res = await client.post(
        "/api/v1/listings/",
        headers={"Authorization": f"Bearer {f_token}"},
        json={
            "commodity_id": c.id,
            "title": "Grade A Arecanut Mangalore",
            "quantity": 500.0,
            "unit": "KG",
            "price_per_unit": 420.0,
        },
    )
    listing_id = l_res.json()["id"]

    # 4. Buyer 1
    await client.post(
        "/api/v1/auth/register",
        json={"email": "buyer_msg@test.com", "full_name": "Aditi Traders", "password": "Password123!", "role": "BUYER"},
    )
    b_login = await client.post("/api/v1/auth/login", json={"email": "buyer_msg@test.com", "password": "Password123!"})
    b_token = b_login.json()["access_token"]

    # 5. Buyer 2 (Unauthorized third party)
    await client.post(
        "/api/v1/auth/register",
        json={"email": "unauthorized_buyer@test.com", "full_name": "Snoop Corp", "password": "Password123!", "role": "BUYER"},
    )
    u_login = await client.post("/api/v1/auth/login", json={"email": "unauthorized_buyer@test.com", "password": "Password123!"})
    u_token = u_login.json()["access_token"]

    # 6. Buyer 1 makes offer for 100 kg
    offer_res = await client.post(
        "/api/v1/offers/",
        headers={"Authorization": f"Bearer {b_token}"},
        json={
            "listing_id": listing_id,
            "quantity": 100.0,
            "price_per_unit": 415.0,
            "delivery_method": "BUYER_PICKUP",
            "message": "Can we arrange warehouse pickup next Tuesday?",
        },
    )
    offer_id = offer_res.json()["id"]

    # 7. Farmer accepts offer -> Creates order & conversation automatically
    accept_res = await client.post(
        f"/api/v1/offers/{offer_id}/accept",
        headers={"Authorization": f"Bearer {f_token}"},
    )
    assert accept_res.status_code == 200
    order_id = accept_res.json()["order_id"]

    return {
        "farmer_token": f_token,
        "buyer_token": b_token,
        "unauthorized_token": u_token,
        "order_id": order_id,
    }


@pytest.mark.asyncio
async def test_offer_acceptance_automatically_creates_conversation(client: AsyncClient, db_session):
    """Verify that accepting an offer automatically establishes the transaction conversation."""
    data = await setup_test_marketplace(client, db_session)
    order_id = data["order_id"]

    # Verify conversation exists in DB
    conv_stmt = select(Conversation).where(Conversation.order_id == order_id)
    conv_res = await db_session.execute(conv_stmt)
    conv = conv_res.scalar_one_or_none()
    assert conv is not None
    assert conv.order_id == order_id

    # Verify both buyer and farmer see this conversation in list
    b_res = await client.get("/api/v1/conversations/", headers={"Authorization": f"Bearer {data['buyer_token']}"})
    assert b_res.status_code == 200
    b_convs = b_res.json()
    assert len(b_convs) == 1
    assert b_convs[0]["order_id"] == order_id
    assert b_convs[0]["farmer"]["full_name"] == "Ramesh Rai"

    f_res = await client.get("/api/v1/conversations/", headers={"Authorization": f"Bearer {data['farmer_token']}"})
    assert f_res.status_code == 200
    f_convs = f_res.json()
    assert len(f_convs) == 1
    assert f_convs[0]["buyer"]["full_name"] == "Aditi Traders"


@pytest.mark.asyncio
async def test_bidirectional_messaging_and_read_tracking(client: AsyncClient, db_session):
    """Verify buyer and farmer can exchange messages, track unread counts, and mark as read."""
    data = await setup_test_marketplace(client, db_session)
    order_id = data["order_id"]

    # Fetch conversation ID
    b_res = await client.get("/api/v1/conversations/", headers={"Authorization": f"Bearer {data['buyer_token']}"})
    conv_id = b_res.json()[0]["id"]

    # 1. Buyer sends a message
    msg_res = await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['buyer_token']}"},
        json={"content": "Namaskara! We will send our vehicle on Wednesday morning."},
    )
    assert msg_res.status_code == 201
    sent_msg = msg_res.json()
    assert sent_msg["content"] == "Namaskara! We will send our vehicle on Wednesday morning."
    assert sent_msg["sender_name"] == "Aditi Traders"
    assert sent_msg["is_mine"] is True

    # 2. Farmer checks conversation list: unread_count should be 1
    f_res = await client.get("/api/v1/conversations/", headers={"Authorization": f"Bearer {data['farmer_token']}"})
    assert f_res.json()[0]["unread_count"] == 1
    assert f_res.json()[0]["last_message"] == "Namaskara! We will send our vehicle on Wednesday morning."

    # 3. Farmer marks messages as read
    read_res = await client.post(
        f"/api/v1/conversations/{conv_id}/read",
        headers={"Authorization": f"Bearer {data['farmer_token']}"},
    )
    assert read_res.status_code == 200
    assert read_res.json()["marked_read_count"] == 1

    # Farmer verifies unread_count is now 0
    f_res2 = await client.get("/api/v1/conversations/", headers={"Authorization": f"Bearer {data['farmer_token']}"})
    assert f_res2.json()[0]["unread_count"] == 0

    # 4. Farmer replies
    reply_res = await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['farmer_token']}"},
        json={"content": "Understood. The produce is packed in clean gunny bags ready at the farm."},
    )
    assert reply_res.status_code == 201
    assert reply_res.json()["sender_name"] == "Ramesh Rai"

    # 5. Fetch message history
    history_res = await client.get(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['buyer_token']}"},
    )
    assert history_res.status_code == 200
    messages = history_res.json()
    assert len(messages) == 2
    assert messages[0]["content"] == "Namaskara! We will send our vehicle on Wednesday morning."
    assert messages[1]["content"] == "Understood. The produce is packed in clean gunny bags ready at the farm."


@pytest.mark.asyncio
async def test_unauthorized_access_and_tampering_blocked(client: AsyncClient, db_session):
    """Verify that unauthorized users cannot read or send messages in other people's conversations (IDOR)."""
    data = await setup_test_marketplace(client, db_session)
    order_id = data["order_id"]

    # Fetch conversation ID
    b_res = await client.get("/api/v1/conversations/", headers={"Authorization": f"Bearer {data['buyer_token']}"})
    conv_id = b_res.json()[0]["id"]

    # Unauthorized user tries to list conversations -> gets empty list
    u_list = await client.get("/api/v1/conversations/", headers={"Authorization": f"Bearer {data['unauthorized_token']}"})
    assert u_list.status_code == 200
    assert len(u_list.json()) == 0

    # Unauthorized user tries to fetch specific conversation details -> 403 Forbidden
    u_detail = await client.get(f"/api/v1/conversations/{conv_id}", headers={"Authorization": f"Bearer {data['unauthorized_token']}"})
    assert u_detail.status_code == 403

    # Unauthorized user tries to read messages -> 403 Forbidden
    u_msgs = await client.get(f"/api/v1/conversations/{conv_id}/messages", headers={"Authorization": f"Bearer {data['unauthorized_token']}"})
    assert u_msgs.status_code == 403

    # Unauthorized user tries to post a message -> 403 Forbidden
    u_post = await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['unauthorized_token']}"},
        json={"content": "Malicious intrusion attempt"},
    )
    assert u_post.status_code == 403

    # Unauthorized user tries to create conversation for order -> 403 Forbidden
    u_order_conv = await client.post(
        f"/api/v1/conversations/order/{order_id}",
        headers={"Authorization": f"Bearer {data['unauthorized_token']}"},
    )
    assert u_order_conv.status_code == 403


@pytest.mark.asyncio
async def test_message_input_validation(client: AsyncClient, db_session):
    """Verify rejection of empty, whitespace-only, and excessively large messages."""
    data = await setup_test_marketplace(client, db_session)
    b_res = await client.get("/api/v1/conversations/", headers={"Authorization": f"Bearer {data['buyer_token']}"})
    conv_id = b_res.json()[0]["id"]

    # Empty string
    res_empty = await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['buyer_token']}"},
        json={"content": ""},
    )
    assert res_empty.status_code == 422

    # Whitespace only
    res_space = await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['buyer_token']}"},
        json={"content": "     \n\t   "},
    )
    assert res_space.status_code == 422

    # Exceeding 2000 characters
    res_huge = await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['buyer_token']}"},
        json={"content": "A" * 2001},
    )
    assert res_huge.status_code == 422


@pytest.mark.asyncio
async def test_duplicate_conversation_prevention_is_idempotent(client: AsyncClient, db_session):
    """Verify that repeated calls to create conversation for the same order return the existing conversation."""
    data = await setup_test_marketplace(client, db_session)
    order_id = data["order_id"]

    call1 = await client.post(
        f"/api/v1/conversations/order/{order_id}",
        headers={"Authorization": f"Bearer {data['buyer_token']}"},
    )
    assert call1.status_code == 200
    conv_id1 = call1.json()["id"]

    call2 = await client.post(
        f"/api/v1/conversations/order/{order_id}",
        headers={"Authorization": f"Bearer {data['farmer_token']}"},
    )
    assert call2.status_code == 200
    conv_id2 = call2.json()["id"]

    assert conv_id1 == conv_id2


@pytest.mark.asyncio
async def test_order_status_messaging_policy(client: AsyncClient, db_session):
    """Verify that completed or cancelled orders close messaging while preserving history,
    and disputed orders retain messaging."""
    data = await setup_test_marketplace(client, db_session)
    order_id = data["order_id"]

    b_res = await client.get("/api/v1/conversations/", headers={"Authorization": f"Bearer {data['buyer_token']}"})
    conv_id = b_res.json()[0]["id"]

    # 1. Post a message while active
    await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['buyer_token']}"},
        json={"content": "Active stage message"},
    )

    # 2. Transition order directly to CANCELLED in DB
    order_stmt = select(Order).where(Order.id == order_id)
    res = await db_session.execute(order_stmt)
    order = res.scalar_one()
    order.status = OrderStatus.CANCELLED
    await db_session.commit()

    # 3. Attempt to post new message on CANCELLED order -> 400 Bad Request
    cancel_post = await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['buyer_token']}"},
        json={"content": "Trying to message on cancelled order"},
    )
    assert cancel_post.status_code == 400
    assert "Messaging is closed" in cancel_post.json()["detail"]

    # But message history is still completely readable!
    history_res = await client.get(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['buyer_token']}"},
    )
    assert history_res.status_code == 200
    assert len(history_res.json()) == 1

    # 4. Now transition order to DISPUTED -> Messaging should be re-enabled for resolution
    order.status = OrderStatus.DISPUTED
    await db_session.commit()

    dispute_post = await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['buyer_token']}"},
        json={"content": "Here is clarification regarding the quality dispute"},
    )
    assert dispute_post.status_code == 201


@pytest.mark.asyncio
async def test_commercial_state_separation(client: AsyncClient, db_session):
    """Verify that sending messages cannot alter order status, price, or inventory."""
    data = await setup_test_marketplace(client, db_session)
    order_id = data["order_id"]

    b_res = await client.get("/api/v1/conversations/", headers={"Authorization": f"Bearer {data['buyer_token']}"})
    conv_id = b_res.json()[0]["id"]

    # Send a message claiming payment and delivery occurred
    msg_res = await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {data['buyer_token']}"},
        json={"content": "I have transferred the full amount of ₹41,500 via IMPS and confirmed receipt of produce."},
    )
    assert msg_res.status_code == 201

    # Verify Order state in DB remains strictly CONFIRMED, total_price is untouched
    order_stmt = select(Order).where(Order.id == order_id)
    res = await db_session.execute(order_stmt)
    order = res.scalar_one()

    assert order.status == OrderStatus.CONFIRMED
    assert float(order.total_price) == 41500.0
    assert float(order.reserved_quantity) == 100.0
    assert float(order.delivered_quantity) == 0.0
