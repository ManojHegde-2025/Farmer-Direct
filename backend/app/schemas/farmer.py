"""Pydantic schemas for Farmer Profile."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.farmer_profile import District, VerificationStatus


class FarmerProfileBase(BaseModel):
    farm_name: Optional[str] = Field(None, max_length=255)
    farm_location: Optional[str] = Field(None, max_length=500)
    district: Optional[District] = None
    taluk: Optional[str] = Field(None, max_length=100)
    village: Optional[str] = Field(None, max_length=100)
    farm_size_acres: Optional[Decimal] = Field(None, ge=0)
    primary_crops: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None


class FarmerProfileCreate(FarmerProfileBase):
    pass


class FarmerProfileUpdate(FarmerProfileBase):
    pass


class FarmerProfileRead(FarmerProfileBase):
    id: int
    user_id: int
    verification_status: VerificationStatus
    verification_document_path: Optional[str] = None
    bank_account_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VerificationSubmission(BaseModel):
    verification_document_path: str = Field(..., min_length=1)


class VerificationDecision(BaseModel):
    status: VerificationStatus
    reason: Optional[str] = None
