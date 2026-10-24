"""Messaging service for authenticated buyer-farmer private communications."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import select, or_, and_, func, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, Message
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.models.notification import Notification
from app.schemas.conversation import (
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse,
    ConversationParticipant,
    ConversationOrderSummary,
)

# Order statuses where active messaging is permitted
ACTIVE_MESSAGING_ORDER_STATUSES = {
    OrderStatus.CREATED,
    OrderStatus.AWAITING_CONFIRMATION,
    OrderStatus.CONFIRMED,
    OrderStatus.PAYMENT_PENDING,
    OrderStatus.PAYMENT_CONFIRMED,
    OrderStatus.READY_FOR_PICKUP,
    OrderStatus.DISPATCHED,
    OrderStatus.DELIVERED,
    OrderStatus.DISPUTED,
}

# Order statuses where commercial activity has finished and messaging is closed
CLOSED_MESSAGING_ORDER_STATUSES = {
    OrderStatus.COMPLETED,
    OrderStatus.CANCELLED,
}


def build_participant_info(user: User) -> ConversationParticipant:
    district = None
    biz_or_farm = None
    if user.farmer_profile:
        district = user.farmer_profile.district.value if hasattr(user.farmer_profile.district, "value") else str(user.farmer_profile.district) if user.farmer_profile.district else None
        biz_or_farm = user.farmer_profile.farm_name
    elif user.buyer_profile:
        district = user.buyer_profile.district
        biz_or_farm = user.buyer_profile.business_name

    return ConversationParticipant(
        id=user.id,
        full_name=user.full_name,
        role=user.role.value if hasattr(user.role, "value") else str(user.role),
        district=district,
        business_or_farm_name=biz_or_farm,
    )


def build_order_summary(order: Order) -> ConversationOrderSummary:
    commodity_name = order.commodity.name if order.commodity else (order.listing.commodity.name if order.listing and order.listing.commodity else "Produce")
    unit = "KG"
    if order.listing and hasattr(order.listing, "unit"):
        unit = order.listing.unit.value if hasattr(order.listing.unit, "value") else str(order.listing.unit)

    return ConversationOrderSummary(
        id=order.id,
        status=order.status.value if hasattr(order.status, "value") else str(order.status),
        commodity_name=commodity_name,
        quantity=float(order.quantity),
        unit=unit,
        price_per_unit=float(order.price_per_unit),
        total_price=float(order.total_price),
    )


async def get_or_create_conversation_for_order(
    db: AsyncSession,
    order_id: int,
    user: User,
) -> Conversation:
    """Retrieve or atomically create the unique conversation associated with an order.
    
    Verifies that the calling user is either the buyer or the seller of the order (or an ADMIN).
    """
    stmt = (
        select(Order)
        .options(
            selectinload(Order.buyer),
            selectinload(Order.seller),
            selectinload(Order.commodity),
            selectinload(Order.listing),
        )
        .where(Order.id == order_id)
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order #{order_id} not found",
        )

    # Participant authorization
    is_buyer = order.buyer_id == user.id
    is_seller = order.seller_id == user.id
    is_admin = user.role == UserRole.ADMIN

    if not (is_buyer or is_seller or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access messaging for this order",
        )

    # Check if conversation already exists (idempotent lookup)
    conv_stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.buyer),
            selectinload(Conversation.farmer),
            selectinload(Conversation.order).selectinload(Order.commodity),
            selectinload(Conversation.order).selectinload(Order.listing),
        )
        .where(Conversation.order_id == order.id)
    )
    conv_res = await db.execute(conv_stmt)
    conversation = conv_res.scalar_one_or_none()

    if conversation:
        return conversation

    # Create new conversation for this order
    conversation = Conversation(
        order_id=order.id,
        buyer_id=order.buyer_id,
        farmer_id=order.seller_id,
    )
    db.add(conversation)
    await db.flush()

    # Re-fetch with all eager loads
    conv_res = await db.execute(conv_stmt)
    return conv_res.scalar_one()


async def get_conversation_with_auth(
    db: AsyncSession,
    conversation_id: int,
    user: User,
) -> Conversation:
    """Retrieve conversation and verify current user is an authorized participant."""
    stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.buyer).selectinload(User.buyer_profile),
            selectinload(Conversation.buyer).selectinload(User.farmer_profile),
            selectinload(Conversation.farmer).selectinload(User.farmer_profile),
            selectinload(Conversation.farmer).selectinload(User.buyer_profile),
            selectinload(Conversation.order).selectinload(Order.commodity),
            selectinload(Conversation.order).selectinload(Order.listing),
        )
        .where(Conversation.id == conversation_id)
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation #{conversation_id} not found",
        )

    is_participant = user.id in (conversation.buyer_id, conversation.farmer_id)
    is_admin = user.role == UserRole.ADMIN

    if not (is_participant or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this conversation",
        )

    return conversation


async def list_user_conversations(
    db: AsyncSession,
    user: User,
) -> List[ConversationResponse]:
    """List all conversations for the authenticated user, sorted by last updated timestamp."""
    stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.buyer).selectinload(User.buyer_profile),
            selectinload(Conversation.buyer).selectinload(User.farmer_profile),
            selectinload(Conversation.farmer).selectinload(User.farmer_profile),
            selectinload(Conversation.farmer).selectinload(User.buyer_profile),
            selectinload(Conversation.order).selectinload(Order.commodity),
            selectinload(Conversation.order).selectinload(Order.listing),
            selectinload(Conversation.messages),
        )
        .where(
            or_(Conversation.buyer_id == user.id, Conversation.farmer_id == user.id)
            if user.role != UserRole.ADMIN
            else and_()
        )
        .order_by(Conversation.updated_at.desc())
    )
    result = await db.execute(stmt)
    conversations = result.scalars().all()

    response_list: List[ConversationResponse] = []
    for conv in conversations:
        # Compute last message and unread count
        messages = sorted(conv.messages, key=lambda m: m.created_at) if conv.messages else []
        last_msg = messages[-1] if messages else None

        unread_count = sum(
            1 for m in messages if not m.is_read and m.sender_id != user.id
        )

        is_closed = conv.order.status in CLOSED_MESSAGING_ORDER_STATUSES if conv.order else False

        response_list.append(
            ConversationResponse(
                id=conv.id,
                order_id=conv.order_id,
                buyer=build_participant_info(conv.buyer),
                farmer=build_participant_info(conv.farmer),
                order_summary=build_order_summary(conv.order),
                last_message=last_msg.content if last_msg else None,
                last_message_at=last_msg.created_at if last_msg else None,
                unread_count=unread_count,
                is_messaging_closed=is_closed,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
            )
        )

    return response_list


async def get_conversation_messages(
    db: AsyncSession,
    conversation_id: int,
    user: User,
    limit: int = 50,
    offset: int = 0,
) -> List[MessageResponse]:
    """Retrieve paginated message thread for an authorized conversation."""
    conversation = await get_conversation_with_auth(db, conversation_id, user)

    stmt = (
        select(Message)
        .options(selectinload(Message.sender))
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(min(limit, 100))
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            sender_id=m.sender_id,
            sender_name=m.sender.full_name if m.sender else "User",
            sender_role=m.sender.role.value if hasattr(m.sender.role, "value") else str(m.sender.role),
            content=m.content,
            is_read=m.is_read,
            read_at=m.read_at,
            created_at=m.created_at,
            is_mine=(m.sender_id == user.id),
        )
        for m in messages
    ]


async def send_message_in_conversation(
    db: AsyncSession,
    conversation_id: int,
    user: User,
    content: str,
) -> MessageResponse:
    """Send a private text message in the conversation.
    
    Enforces participant authorization, validates order status policy,
    records message with server-derived sender identity, updates conversation timestamp,
    and notifies the recipient.
    """
    conversation = await get_conversation_with_auth(db, conversation_id, user)

    # Status check: If order is completed or cancelled, new messaging is closed
    if conversation.order.status in CLOSED_MESSAGING_ORDER_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Messaging is closed for this order because its status is {conversation.order.status.value}. "
                "Conversation history is preserved for reference."
            ),
        )

    # Sanitize and validate content
    trimmed = content.strip()
    if not trimmed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message content cannot be empty",
        )
    if len(trimmed) > 2000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message content exceeds maximum permitted length of 2000 characters",
        )

    # Server derives sender identity from authenticated user
    now = datetime.now(timezone.utc)
    message = Message(
        conversation_id=conversation.id,
        sender_id=user.id,
        content=trimmed,
        is_read=False,
        created_at=now,
    )
    db.add(message)

    # Update conversation's updated_at
    conversation.updated_at = now

    # Determine recipient
    recipient_id = (
        conversation.farmer_id if user.id == conversation.buyer_id else conversation.buyer_id
    )

    # Create in-app Notification for recipient
    notif = Notification(
        user_id=recipient_id,
        title=f"New message from {user.full_name}",
        message=f"{trimmed[:100]}..." if len(trimmed) > 100 else trimmed,
        type="NEW_MESSAGE",
        link=f"/messages?conversationId={conversation.id}",
        is_read=False,
    )
    db.add(notif)

    await db.commit()
    await db.refresh(message)

    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        sender_name=user.full_name,
        sender_role=user.role.value if hasattr(user.role, "value") else str(user.role),
        content=message.content,
        is_read=message.is_read,
        read_at=message.read_at,
        created_at=message.created_at,
        is_mine=True,
    )


async def mark_conversation_messages_as_read(
    db: AsyncSession,
    conversation_id: int,
    user: User,
) -> int:
    """Mark all incoming unread messages in the conversation as read for the calling user."""
    conversation = await get_conversation_with_auth(db, conversation_id, user)

    now = datetime.now(timezone.utc)
    stmt = (
        update(Message)
        .where(
            Message.conversation_id == conversation.id,
            Message.sender_id != user.id,
            Message.is_read == False,  # noqa: E712
        )
        .values(is_read=True, read_at=now)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount
