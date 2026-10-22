"""Reference Price API endpoints.

PHASE 9 specification:
- Classifications: LIVE_EXTERNAL_SOURCE, OFFICIAL_PUBLISHED_DATA, HISTORICAL_REFERENCE, DEMO_DATA, USER_REPORTED.
- Clearly displays observation date and data source.
- When no reliable price exists, returns clear unavailable status.
- Admin management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.reference_price import ReferencePrice, PriceClassification
from app.models.commodity import Commodity
from app.models.user import UserRole
from app.schemas.reference_price import ReferencePriceCreate, ReferencePriceRead
from app.middleware.auth import require_roles

router = APIRouter()


@router.get("/")
async def list_reference_prices(
    commodity_id: Optional[int] = None,
    classification: Optional[PriceClassification] = None,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve market reference price records with full transparency on source & classification."""
    stmt = (
        select(ReferencePrice)
        .options(selectinload(ReferencePrice.commodity))
    )
    if commodity_id:
        stmt = stmt.where(ReferencePrice.commodity_id == commodity_id)
    if classification:
        stmt = stmt.where(ReferencePrice.classification == classification)

    stmt = stmt.order_by(ReferencePrice.observation_date.desc())
    result = await db.execute(stmt)
    records = result.scalars().all()

    return [
        {
            "id": r.id,
            "commodity_id": r.commodity_id,
            "commodity_name": r.commodity.name if r.commodity else None,
            "variety": r.variety,
            "market": r.market,
            "locality": r.locality,
            "price": float(r.price),
            "unit": r.unit.value if hasattr(r.unit, "value") else str(r.unit),
            "observation_date": r.observation_date.isoformat(),
            "source": r.source,
            "source_url": r.source_url,
            "classification": r.classification.value,
            "quality_grade": r.quality_grade,
            "is_demonstration": r.classification == PriceClassification.DEMO_DATA,
        }
        for r in records
    ]


@router.get("/commodity/{commodity_id}")
async def get_commodity_reference_price(commodity_id: int, db: AsyncSession = Depends(get_db)):
    """Get the latest indicative reference price benchmark for a specific commodity."""
    stmt = (
        select(ReferencePrice)
        .options(selectinload(ReferencePrice.commodity))
        .where(ReferencePrice.commodity_id == commodity_id)
        .order_by(ReferencePrice.observation_date.desc())
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    if not records:
        return {
            "commodity_id": commodity_id,
            "available": False,
            "message": "Indicative reference price benchmark currently unavailable for this commodity.",
            "records": [],
        }

    latest = records[0]
    return {
        "commodity_id": commodity_id,
        "available": True,
        "latest_price": float(latest.price),
        "unit": latest.unit.value if hasattr(latest.unit, "value") else str(latest.unit),
        "market": latest.market,
        "observation_date": latest.observation_date.isoformat(),
        "source": latest.source,
        "classification": latest.classification.value,
        "is_demonstration": latest.classification == PriceClassification.DEMO_DATA,
        "all_records": [
            {
                "id": r.id,
                "variety": r.variety,
                "market": r.market,
                "price": float(r.price),
                "unit": r.unit.value if hasattr(r.unit, "value") else str(r.unit),
                "observation_date": r.observation_date.isoformat(),
                "source": r.source,
                "classification": r.classification.value,
            }
            for r in records
        ],
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_reference_price(
    data: ReferencePriceCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_roles(UserRole.ADMIN)),
):
    """Publish a new reference price benchmark (Admin only)."""
    comm = await db.execute(select(Commodity).where(Commodity.id == data.commodity_id))
    if not comm.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commodity #{data.commodity_id} not found",
        )

    ref = ReferencePrice(**data.model_dump())
    db.add(ref)
    await db.flush()
    return {"id": ref.id, "message": "Reference price record added successfully"}
