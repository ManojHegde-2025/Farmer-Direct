"""Pydantic schemas for Offer."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.offer import OfferStatus
from app.schemas.listing import ListingBrief
from app.schemas.user import UserBrief


class OfferBase(BaseModel):
    listing_id: int
    quantity: Decimal = Field(..., gt=0, decimal_places=2)
    price_per_unit: Decimal = Field(..., gt=0, decimal_places=2)
    delivery_method: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[str] = Field(None, max_length=200)
    message: Optional[str] = None


class OfferCreate(OfferBase):
    pass


class CounterOfferCreate(BaseModel):
    quantity: Decimal = Field(..., gt=0, decimal_places=2)
    price_per_unit: Decimal = Field(..., gt=0, decimal_places=2)
    delivery_method: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[str] = Field(None, max_length=200)
    message: Optional[str] = None


class OfferRead(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    seller_id: int
    quantity: Decimal
    price_per_unit: Decimal
    total_price: Decimal
    delivery_method: Optional[str] = None
    payment_terms: Optional[str] = None
    message: Optional[str] = None
    status: OfferStatus
    expires_at: Optional[datetime] = None
    parent_offer_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    listing: Optional[ListingBrief] = None
    buyer: Optional[UserBrief] = None
    seller: Optional[UserBrief] = None

    model_config = {"from_attributes": True}
