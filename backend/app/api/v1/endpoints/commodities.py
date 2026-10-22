"""Commodity management endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.commodity import Commodity
from app.models.user import UserRole
from app.schemas.commodity import CommodityCreate, CommodityRead, CommodityUpdate
from app.middleware.auth import require_roles

router = APIRouter()


@router.get("/", response_model=List[CommodityRead])
async def list_commodities(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List agricultural commodities supported by the marketplace."""
    stmt = select(Commodity)
    if active_only:
        stmt = stmt.where(Commodity.is_active == True)
    stmt = stmt.order_by(Commodity.name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{commodity_id}", response_model=CommodityRead)
async def get_commodity(commodity_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a single commodity."""
    result = await db.execute(select(Commodity).where(Commodity.id == commodity_id))
    commodity = result.scalar_one_or_none()
    if not commodity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commodity #{commodity_id} not found",
        )
    return commodity


@router.post("/", response_model=CommodityRead, status_code=status.HTTP_201_CREATED)
async def create_commodity(
    data: CommodityCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_roles(UserRole.ADMIN)),
):
    """Create a new commodity (Admin only)."""
    existing = await db.execute(select(Commodity).where(Commodity.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Commodity '{data.name}' already exists",
        )
    commodity = Commodity(**data.model_dump())
    db.add(commodity)
    await db.flush()
    return commodity


@router.put("/{commodity_id}", response_model=CommodityRead)
async def update_commodity(
    commodity_id: int,
    data: CommodityUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_roles(UserRole.ADMIN)),
):
    """Update a commodity (Admin only)."""
    result = await db.execute(select(Commodity).where(Commodity.id == commodity_id))
    commodity = result.scalar_one_or_none()
    if not commodity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commodity #{commodity_id} not found",
        )
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(commodity, field, val)
    await db.flush()
    return commodity
