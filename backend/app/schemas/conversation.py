"""Schemas for conversation and messaging."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="Message text content")

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Message cannot be empty or contain only whitespace")
        return trimmed


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    sender_id: int
    sender_name: str
    sender_role: str
    content: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    is_mine: bool = False


class ConversationParticipant(BaseModel):
    id: int
    full_name: str
    role: str
    district: Optional[str] = None
    business_or_farm_name: Optional[str] = None


class ConversationOrderSummary(BaseModel):
    id: int
    status: str
    commodity_name: str
    quantity: float
    unit: str
    price_per_unit: float
    total_price: float


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    buyer: ConversationParticipant
    farmer: ConversationParticipant
    order_summary: ConversationOrderSummary
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0
    is_messaging_closed: bool = False
    created_at: datetime
    updated_at: datetime


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse] = []
