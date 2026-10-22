"""Pydantic schemas for matching engine."""

from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.listing import ListingRead


class MatchScore(BaseModel):
    commodity_score: float = 0.0
    quantity_score: float = 0.0
    price_score: float = 0.0
    location_score: float = 0.0
    timing_score: float = 0.0
    quality_score: float = 0.0
    total_score: float = 0.0


class MatchExplanation(BaseModel):
    commodity_match: str = ""
    quantity_match: str = ""
    price_match: str = ""
    location_match: str = ""
    timing_match: str = ""
    quality_match: str = ""


class MatchResult(BaseModel):
    listing: ListingRead
    score: MatchScore
    explanation: MatchExplanation
    overall_percentage: float = 0.0


class MatchResponse(BaseModel):
    requirement_id: int
    matches: List[MatchResult]
    total_matches: int


class NetProceedsRequest(BaseModel):
    quantity: Decimal
    price_per_unit: Decimal
    transport_cost: Optional[Decimal] = Decimal("0")
    commission_rate: Optional[Decimal] = Decimal("0.02")
    packaging_cost: Optional[Decimal] = Decimal("0")


class NetProceedsResponse(BaseModel):
    gross_value: Decimal
    transport_cost: Decimal
    commission: Decimal
    packaging_cost: Decimal
    total_costs: Decimal
    net_proceeds: Decimal
    cost_percentage: Decimal
