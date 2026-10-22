"""Pydantic schemas for Buyer Profile."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.buyer_profile import BusinessType
from app.models.farmer_profile import VerificationStatus


class BuyerProfileBase(BaseModel):
    business_name: Optional[str] = Field(None, max_length=255)
    business_type: Optional[BusinessType] = None
    district: Optional[str] = Field(None, max_length=100)
    taluk: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    gst_number: Optional[str] = Field(None, max_length=20)


class BuyerProfileCreate(BuyerProfileBase):
    pass


class BuyerProfileUpdate(BuyerProfileBase):
    pass


class BuyerProfileRead(BuyerProfileBase):
    id: int
    user_id: int
    verification_status: VerificationStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
