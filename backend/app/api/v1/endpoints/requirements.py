"""Buyer Requirements endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.buyer_requirement import BuyerRequirement
from app.models.commodity import Commodity
from app.models.user import User, UserRole
from app.schemas.requirement import RequirementCreate, RequirementUpdate
from app.middleware.auth import get_current_user, require_roles

router = APIRouter()


@router.get("/")
async def list_requirements(
    my_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List buyer requirements."""
    stmt = (
        select(BuyerRequirement)
        .options(
            selectinload(BuyerRequirement.commodity),
            selectinload(BuyerRequirement.buyer),
        )
    )
    if my_only or current_user.role == UserRole.BUYER:
        stmt = stmt.where(BuyerRequirement.buyer_id == current_user.id)
    else:
        stmt = stmt.where(BuyerRequirement.is_active == True)

    stmt = stmt.order_by(BuyerRequirement.created_at.desc())
    result = await db.execute(stmt)
    reqs = result.scalars().all()

    return [
        {
            "id": r.id,
            "buyer_id": r.buyer_id,
            "commodity_id": r.commodity_id,
            "commodity_name": r.commodity.name if r.commodity else None,
            "commodity_name_kn": r.commodity.name_kn if r.commodity else None,
            "unit": r.commodity.unit.value if r.commodity else "KG",
            "variety_preference": r.variety_preference,
            "quality_preference": r.quality_preference,
            "quantity_needed": float(r.quantity_needed),
            "max_price_per_unit": float(r.max_price_per_unit) if r.max_price_per_unit else None,
            "delivery_location": r.delivery_location,
            "delivery_district": r.delivery_district,
            "needed_by": r.needed_by.isoformat() if r.needed_by else None,
            "is_active": r.is_active,
            "created_at": r.created_at.isoformat(),
        }
        for r in reqs
    ]


@router.get("/{requirement_id}")
async def get_requirement(
    requirement_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get single buyer requirement."""
    stmt = (
        select(BuyerRequirement)
        .options(
            selectinload(BuyerRequirement.commodity),
            selectinload(BuyerRequirement.buyer),
        )
        .where(BuyerRequirement.id == requirement_id)
    )
    result = await db.execute(stmt)
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found",
        )
    return {
        "id": r.id,
        "buyer_id": r.buyer_id,
        "commodity_id": r.commodity_id,
        "commodity_name": r.commodity.name if r.commodity else None,
        "variety_preference": r.variety_preference,
        "quality_preference": r.quality_preference,
        "quantity_needed": float(r.quantity_needed),
        "max_price_per_unit": float(r.max_price_per_unit) if r.max_price_per_unit else None,
        "delivery_location": r.delivery_location,
        "delivery_district": r.delivery_district,
        "needed_by": r.needed_by.isoformat() if r.needed_by else None,
        "is_active": r.is_active,
        "created_at": r.created_at.isoformat(),
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_requirement(
    data: RequirementCreate,
    current_user: User = Depends(require_roles(UserRole.BUYER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Publish a buyer procurement requirement."""
    comm = await db.execute(select(Commodity).where(Commodity.id == data.commodity_id))
    if not comm.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commodity #{data.commodity_id} not found",
        )

    req = BuyerRequirement(
        buyer_id=current_user.id,
        commodity_id=data.commodity_id,
        variety_preference=data.variety_preference,
        quality_preference=data.quality_preference,
        quantity_needed=data.quantity_needed,
        max_price_per_unit=data.max_price_per_unit,
        delivery_location=data.delivery_location,
        delivery_district=data.delivery_district,
        needed_by=data.needed_by,
        is_active=True,
    )
    db.add(req)
    await db.flush()
    return {"id": req.id, "message": "Procurement requirement published successfully"}


@router.put("/{requirement_id}")
async def update_requirement(
    requirement_id: int,
    data: RequirementUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update requirement (Buyer only)."""
    result = await db.execute(select(BuyerRequirement).where(BuyerRequirement.id == requirement_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

    if req.buyer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(req, field, val)

    await db.flush()
    return {"message": "Requirement updated successfully", "id": req.id}


@router.delete("/{requirement_id}")
async def delete_requirement(
    requirement_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate requirement."""
    result = await db.execute(select(BuyerRequirement).where(BuyerRequirement.id == requirement_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

    if req.buyer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    req.is_active = False
    await db.flush()
    return {"message": "Requirement deactivated"}
