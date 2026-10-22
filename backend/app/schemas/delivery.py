"""Pydantic schemas for Delivery."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.delivery import DeliveryMethod, DeliveryStatus, CostBorneBy


class DeliveryCreate(BaseModel):
    order_id: int
    method: DeliveryMethod
    pickup_location: Optional[str] = Field(None, max_length=500)
    delivery_location: Optional[str] = Field(None, max_length=500)
    expected_date: Optional[date] = None
    transport_cost: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    cost_borne_by: Optional[CostBorneBy] = None
    notes: Optional[str] = None


class DeliveryUpdate(BaseModel):
    status: Optional[DeliveryStatus] = None
    dispatch_date: Optional[date] = None
    delivery_date: Optional[date] = None
    notes: Optional[str] = None


class DeliveryRead(BaseModel):
    id: int
    order_id: int
    method: DeliveryMethod
    pickup_location: Optional[str] = None
    delivery_location: Optional[str] = None
    expected_date: Optional[date] = None
    transport_cost: Optional[Decimal] = None
    cost_borne_by: Optional[CostBorneBy] = None
    dispatch_date: Optional[date] = None
    delivery_date: Optional[date] = None
    status: DeliveryStatus
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
