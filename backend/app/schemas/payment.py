"""Pydantic schemas for Payment."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    order_id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    method: Optional[PaymentMethod] = None
    reference_number: Optional[str] = Field(None, max_length=100)


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus
    reference_number: Optional[str] = None


class PaymentRead(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    method: Optional[PaymentMethod] = None
    status: PaymentStatus
    is_simulated: bool
    reference_number: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
