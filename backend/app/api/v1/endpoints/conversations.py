"""Conversation and Messaging API Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User
from app.middleware.auth import get_current_user
from app.schemas.conversation import (
    ConversationResponse,
    MessageResponse,
    MessageCreate,
)
from app.services import messaging_service

router = APIRouter()


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the authenticated user, sorted by last activity."""
    return await messaging_service.list_user_conversations(db, current_user)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get single conversation metadata, verifying participant authorization."""
    conv = await messaging_service.get_conversation_with_auth(db, conversation_id, current_user)
    # List helper builds the response format with unread count and participants
    convs = await messaging_service.list_user_conversations(db, current_user)
    for c in convs:
        if c.id == conv.id:
            return c
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")


@router.post("/order/{order_id}", response_model=ConversationResponse, status_code=status.HTTP_200_OK)
async def get_or_create_order_conversation(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get or establish the unique private conversation associated with an order."""
    conv = await messaging_service.get_or_create_conversation_for_order(db, order_id, current_user)
    convs = await messaging_service.list_user_conversations(db, current_user)
    for c in convs:
        if c.id == conv.id:
            return c
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation could not be loaded")


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve chronological message history for a conversation."""
    return await messaging_service.get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
        user=current_user,
        limit=limit,
        offset=offset,
    )


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a text message in an authorized conversation."""
    return await messaging_service.send_message_in_conversation(
        db=db,
        conversation_id=conversation_id,
        user=current_user,
        content=data.content,
    )


@router.post("/{conversation_id}/read", status_code=status.HTTP_200_OK)
async def mark_messages_read(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all incoming unread messages in the conversation as read."""
    count = await messaging_service.mark_conversation_messages_as_read(
        db=db,
        conversation_id=conversation_id,
        user=current_user,
    )
    return {"message": "Messages marked as read", "marked_read_count": count}
