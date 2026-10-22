"""Pydantic schemas for Order."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.order import OrderStatus, FulfilmentMethod
from app.schemas.user import UserBrief


class OrderCreate(BaseModel):
    offer_id: Optional[int] = None
    listing_id: int
    quantity: Decimal = Field(..., gt=0, decimal_places=2)
    price_per_unit: Decimal = Field(..., gt=0, decimal_places=2)
    fulfilment_method: Optional[FulfilmentMethod] = None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemRead(BaseModel):
    id: int
    order_id: int
    listing_id: int
    quantity: Decimal
    price_per_unit: Decimal

    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    id: int
    offer_id: Optional[int] = None
    buyer_id: int
    seller_id: int
    listing_id: int
    commodity_id: int
    quantity: Decimal
    reserved_quantity: Decimal
    dispatched_quantity: Decimal
    delivered_quantity: Decimal
    price_per_unit: Decimal
    total_price: Decimal
    status: OrderStatus
    fulfilment_method: Optional[FulfilmentMethod] = None
    created_at: datetime
    updated_at: datetime
    buyer: Optional[UserBrief] = None
    seller: Optional[UserBrief] = None
    items: Optional[List[OrderItemRead]] = None

    model_config = {"from_attributes": True}
