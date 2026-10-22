"""Pydantic schemas for Reference Price."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.commodity import CommodityUnit
from app.models.reference_price import PriceClassification
from app.schemas.commodity import CommodityRead


class ReferencePriceBase(BaseModel):
    commodity_id: int
    variety: Optional[str] = Field(None, max_length=100)
    market: Optional[str] = Field(None, max_length=200)
    locality: Optional[str] = Field(None, max_length=200)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    unit: CommodityUnit
    observation_date: date
    source: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=500)
    classification: PriceClassification = PriceClassification.DEMO_DATA
    quality_grade: Optional[str] = Field(None, max_length=20)


class ReferencePriceCreate(ReferencePriceBase):
    pass


class ReferencePriceUpdate(BaseModel):
    variety: Optional[str] = None
    market: Optional[str] = None
    locality: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    unit: Optional[CommodityUnit] = None
    observation_date: Optional[date] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    classification: Optional[PriceClassification] = None
    quality_grade: Optional[str] = None


class ReferencePriceRead(ReferencePriceBase):
    id: int
    created_at: datetime
    commodity: Optional[CommodityRead] = None

    model_config = {"from_attributes": True}
