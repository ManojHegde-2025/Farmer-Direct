"""Pydantic schemas for Listing."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any

from pydantic import BaseModel, Field

from app.models.commodity import CommodityUnit
from app.models.listing import QualityGrade, ListingStatus
from app.schemas.commodity import CommodityRead
from app.schemas.user import UserBrief


class ListingBase(BaseModel):
    commodity_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    variety: Optional[str] = Field(None, max_length=100)
    quality_grade: QualityGrade = QualityGrade.UNGRADED
    quantity: Decimal = Field(..., gt=0, decimal_places=2)
    unit: CommodityUnit
    price_per_unit: Decimal = Field(..., gt=0, decimal_places=2)
    min_order_quantity: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    images: Optional[Any] = None
    harvest_date: Optional[date] = None
    available_from: Optional[date] = None
    available_until: Optional[date] = None
    pickup_location: Optional[str] = Field(None, max_length=500)
    delivery_available: bool = False
    delivery_radius_km: Optional[int] = None


class ListingCreate(ListingBase):
    pass


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    variety: Optional[str] = Field(None, max_length=100)
    quality_grade: Optional[QualityGrade] = None
    quantity: Optional[Decimal] = Field(None, gt=0)
    price_per_unit: Optional[Decimal] = Field(None, gt=0)
    min_order_quantity: Optional[Decimal] = Field(None, gt=0)
    images: Optional[Any] = None
    harvest_date: Optional[date] = None
    available_from: Optional[date] = None
    available_until: Optional[date] = None
    pickup_location: Optional[str] = None
    delivery_available: Optional[bool] = None
    delivery_radius_km: Optional[int] = None


class ListingStatusUpdate(BaseModel):
    status: ListingStatus


class ListingRead(ListingBase):
    id: int
    farmer_id: int
    available_quantity: Decimal
    status: ListingStatus
    created_at: datetime
    updated_at: datetime
    commodity: Optional[CommodityRead] = None
    farmer: Optional[UserBrief] = None

    model_config = {"from_attributes": True}


class ListingBrief(BaseModel):
    id: int
    title: str
    commodity_id: int
    price_per_unit: Decimal
    available_quantity: Decimal
    unit: CommodityUnit
    status: ListingStatus

    model_config = {"from_attributes": True}
