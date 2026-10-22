"""Pydantic schemas for Dispute."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.dispute import DisputeCategory, DisputeStatus
from app.schemas.user import UserBrief


class DisputeCreate(BaseModel):
    order_id: int
    category: DisputeCategory
    description: str = Field(..., min_length=10)


class DisputeUpdate(BaseModel):
    status: Optional[DisputeStatus] = None
    resolution: Optional[str] = None


class DisputeRead(BaseModel):
    id: int
    order_id: int
    raised_by: int
    against_user: int
    category: DisputeCategory
    description: str
    status: DisputeStatus
    resolution: Optional[str] = None
    admin_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    raiser: Optional[UserBrief] = None
    against: Optional[UserBrief] = None

    model_config = {"from_attributes": True}
