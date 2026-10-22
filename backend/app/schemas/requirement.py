"""Pydantic schemas for Buyer Requirement."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.commodity import CommodityRead
from app.schemas.user import UserBrief


class RequirementBase(BaseModel):
    commodity_id: int
    variety_preference: Optional[str] = Field(None, max_length=100)
    quality_preference: Optional[str] = Field(None, max_length=50)
    quantity_needed: Decimal = Field(..., gt=0, decimal_places=2)
    max_price_per_unit: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    delivery_location: Optional[str] = Field(None, max_length=500)
    delivery_district: Optional[str] = Field(None, max_length=100)
    needed_by: Optional[date] = None


class RequirementCreate(RequirementBase):
    pass


class RequirementUpdate(BaseModel):
    variety_preference: Optional[str] = Field(None, max_length=100)
    quality_preference: Optional[str] = Field(None, max_length=50)
    quantity_needed: Optional[Decimal] = Field(None, gt=0)
    max_price_per_unit: Optional[Decimal] = Field(None, gt=0)
    delivery_location: Optional[str] = None
    delivery_district: Optional[str] = None
    needed_by: Optional[date] = None
    is_active: Optional[bool] = None


class RequirementRead(RequirementBase):
    id: int
    buyer_id: int
    is_active: bool
    created_at: datetime
    commodity: Optional[CommodityRead] = None
    buyer: Optional[UserBrief] = None

    model_config = {"from_attributes": True}
