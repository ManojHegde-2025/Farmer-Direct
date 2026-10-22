"""Pydantic schemas for Commodity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.commodity import CommodityUnit


class CommodityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    name_kn: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    unit: CommodityUnit = CommodityUnit.KG
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)


class CommodityCreate(CommodityBase):
    pass


class CommodityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_kn: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    unit: Optional[CommodityUnit] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    icon: Optional[str] = Field(None, max_length=50)


class CommodityRead(CommodityBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
