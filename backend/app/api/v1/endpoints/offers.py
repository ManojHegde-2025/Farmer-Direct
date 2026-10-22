"""Offers and Negotiation endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.offer import Offer, OfferStatus
from app.models.listing import Listing
from app.models.user import User, UserRole
from app.schemas.offer import OfferCreate, CounterOfferCreate
from app.middleware.auth import get_current_user
from app.services import offer_service

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def make_offer(
    data: OfferCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit an initial purchase offer on a produce listing."""
    offer = await offer_service.create_offer(
        db=db,
        buyer=current_user,
        listing_id=data.listing_id,
        quantity=data.quantity,
        price_per_unit=data.price_per_unit,
        delivery_method=data.delivery_method,
        payment_terms=data.payment_terms,
        message=data.message,
    )
    return {
        "id": offer.id,
        "status": offer.status.value,
        "quantity": float(offer.quantity),
        "price_per_unit": float(offer.price_per_unit),
        "total_price": float(offer.total_price),
        "message": "Offer submitted successfully",
    }


@router.post("/{offer_id}/counter", status_code=status.HTTP_201_CREATED)
async def counter_offer(
    offer_id: int,
    data: CounterOfferCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a counteroffer responding to an existing pending offer."""
    counter = await offer_service.counter_offer(
        db=db,
        user=current_user,
        original_offer_id=offer_id,
        quantity=data.quantity,
        price_per_unit=data.price_per_unit,
        delivery_method=data.delivery_method,
        payment_terms=data.payment_terms,
        message=data.message,
    )
    return {
        "id": counter.id,
        "parent_offer_id": counter.parent_offer_id,
        "status": counter.status.value,
        "quantity": float(counter.quantity),
        "price_per_unit": float(counter.price_per_unit),
        "total_price": float(counter.total_price),
        "message": "Counteroffer submitted successfully",
    }


@router.post("/{offer_id}/accept")
async def accept_offer(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accept an offer. Atomically creates a confirmed Order and reserves produce inventory."""
    order = await offer_service.accept_offer(
        db=db,
        user=current_user,
        offer_id=offer_id,
    )
    return {
        "order_id": order.id,
        "status": order.status.value,
        "reserved_quantity": float(order.reserved_quantity),
        "total_price": float(order.total_price),
        "message": "Offer accepted! Confirmed order created and stock reserved successfully.",
    }


@router.post("/{offer_id}/reject")
async def reject_offer(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject an offer."""
    offer = await offer_service.reject_offer(db=db, user=current_user, offer_id=offer_id)
    return {"id": offer.id, "status": offer.status.value, "message": "Offer rejected"}


@router.post("/{offer_id}/withdraw")
async def withdraw_offer(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Withdraw an offer."""
    offer = await offer_service.withdraw_offer(db=db, user=current_user, offer_id=offer_id)
    return {"id": offer.id, "status": offer.status.value, "message": "Offer withdrawn"}


@router.get("/")
async def list_my_offers(
    role_view: Optional[str] = Query("all", pattern="^(buyer|seller|all)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all offers where current user is the buyer or seller."""
    stmt = (
        select(Offer)
        .options(
            selectinload(Offer.listing).selectinload(Listing.commodity),
            selectinload(Offer.buyer),
            selectinload(Offer.seller),
        )
    )

    if role_view == "buyer":
        stmt = stmt.where(Offer.buyer_id == current_user.id)
    elif role_view == "seller":
        stmt = stmt.where(Offer.seller_id == current_user.id)
    else:
        stmt = stmt.where(
            or_(Offer.buyer_id == current_user.id, Offer.seller_id == current_user.id)
        )

    stmt = stmt.order_by(Offer.created_at.desc())
    result = await db.execute(stmt)
    offers = result.scalars().all()

    return [
        {
            "id": o.id,
            "listing_id": o.listing_id,
            "listing_title": o.listing.title if o.listing else None,
            "commodity_name": o.listing.commodity.name if o.listing and o.listing.commodity else None,
            "unit": o.listing.unit.value if o.listing and hasattr(o.listing.unit, "value") else "KG",
            "buyer_id": o.buyer_id,
            "buyer_name": o.buyer.full_name if o.buyer else "Buyer",
            "seller_id": o.seller_id,
            "seller_name": o.seller.full_name if o.seller else "Farmer",
            "quantity": float(o.quantity),
            "price_per_unit": float(o.price_per_unit),
            "total_price": float(o.total_price),
            "delivery_method": o.delivery_method,
            "payment_terms": o.payment_terms,
            "message": o.message,
            "status": o.status.value,
            "parent_offer_id": o.parent_offer_id,
            "is_incoming": o.seller_id == current_user.id,
            "created_at": o.created_at.isoformat(),
        }
        for o in offers
    ]


@router.get("/{offer_id}/history")
async def get_negotiation_history(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the full chronological chain of counteroffers and negotiation."""
    # Find root offer
    curr = await offer_service.get_offer_by_id(db, offer_id)

    # Permission check
    if current_user.id not in [curr.buyer_id, curr.seller_id] and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Traverse to root
    root_id = curr.id
    visited = set()
    while curr.parent_offer_id and curr.parent_offer_id not in visited:
        visited.add(curr.id)
        parent_result = await db.execute(select(Offer).where(Offer.id == curr.parent_offer_id))
        curr = parent_result.scalar_one_or_none()
        if not curr:
            break
        root_id = curr.id

    # Fetch all offers for this listing and buyer/seller
    stmt = (
        select(Offer)
        .options(selectinload(Offer.buyer), selectinload(Offer.seller))
        .where(
            Offer.listing_id == curr.listing_id,
            Offer.buyer_id == curr.buyer_id,
            Offer.seller_id == curr.seller_id,
        )
        .order_by(Offer.created_at.asc())
    )
    result = await db.execute(stmt)
    history = result.scalars().all()

    return [
        {
            "id": h.id,
            "parent_offer_id": h.parent_offer_id,
            "quantity": float(h.quantity),
            "price_per_unit": float(h.price_per_unit),
            "total_price": float(h.total_price),
            "delivery_method": h.delivery_method,
            "message": h.message,
            "status": h.status.value,
            "sender_name": h.buyer.full_name if h.buyer_id == current_user.id else h.seller.full_name,
            "created_at": h.created_at.isoformat(),
        }
        for h in history
    ]
