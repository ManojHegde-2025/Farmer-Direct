"""Pydantic schemas for Review."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserBrief


class ReviewCreate(BaseModel):
    order_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewRead(BaseModel):
    id: int
    order_id: int
    reviewer_id: int
    reviewee_id: int
    rating: int
    comment: Optional[str] = None
    is_visible: bool
    created_at: datetime
    reviewer: Optional[UserBrief] = None
    reviewee: Optional[UserBrief] = None

    model_config = {"from_attributes": True}
