"""Offer negotiation service with atomic order creation and inventory locking.

PHASE 11 & PHASE 12 specifications:
- PENDING, COUNTERED, ACCEPTED, REJECTED, WITHDRAWN, EXPIRED.
- Offer acceptance atomically creates Order and reserves stock in a DB transaction.
- Prevents duplicate acceptance and conflicting orders.
- Validates ownership and permissions.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer import Offer, OfferStatus
from app.models.listing import Listing, ListingStatus
from app.models.order import Order, OrderStatus, FulfilmentMethod
from app.models.user import User
from app.services.inventory_service import reserve_stock


async def get_offer_by_id(db: AsyncSession, offer_id: int) -> Offer:
    result = await db.execute(select(Offer).where(Offer.id == offer_id))
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer #{offer_id} not found",
        )
    return offer


async def create_offer(
    db: AsyncSession,
    buyer: User,
    listing_id: int,
    quantity: Decimal,
    price_per_unit: Decimal,
    delivery_method: Optional[str] = None,
    payment_terms: Optional[str] = None,
    message: Optional[str] = None,
    expires_at: Optional[datetime] = None,
) -> Offer:
    """Create a new offer for a listing."""
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    # Buyer cannot make offer on their own listing
    if listing.farmer_id == buyer.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farmers cannot submit offers on their own listings",
        )

    if listing.status not in [ListingStatus.ACTIVE, ListingStatus.PARTIALLY_RESERVED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Listing is not currently accepting offers (status: {listing.status.value})",
        )

    if quantity <= Decimal("0"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offer quantity must be strictly greater than zero",
        )

    if quantity > listing.available_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested quantity ({quantity}) exceeds available stock ({listing.available_quantity})",
        )

    if listing.min_order_quantity and quantity < listing.min_order_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested quantity is below minimum order requirement of {listing.min_order_quantity}",
        )

    if price_per_unit <= Decimal("0"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price per unit must be greater than zero",
        )

    total_price = quantity * price_per_unit

    offer = Offer(
        listing_id=listing.id,
        buyer_id=buyer.id,
        seller_id=listing.farmer_id,
        quantity=quantity,
        price_per_unit=price_per_unit,
        total_price=total_price,
        delivery_method=delivery_method,
        payment_terms=payment_terms,
        message=message,
        status=OfferStatus.PENDING,
        expires_at=expires_at,
    )
    db.add(offer)
    await db.flush()
    return offer


async def counter_offer(
    db: AsyncSession,
    user: User,
    original_offer_id: int,
    quantity: Decimal,
    price_per_unit: Decimal,
    delivery_method: Optional[str] = None,
    payment_terms: Optional[str] = None,
    message: Optional[str] = None,
    expires_at: Optional[datetime] = None,
) -> Offer:
    """Submit a counteroffer responding to an existing pending offer."""
    original_offer = await get_offer_by_id(db, original_offer_id)

    if original_offer.status != OfferStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot counter offer with status {original_offer.status.value}",
        )

    # Check expiration
    if original_offer.expires_at and original_offer.expires_at < datetime.now(timezone.utc):
        original_offer.status = OfferStatus.EXPIRED
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The original offer has expired and can no longer be countered",
        )

    # Verify user is one of the parties
    if user.id not in [original_offer.buyer_id, original_offer.seller_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to negotiate on this offer",
        )

    # Mark original offer as COUNTERED
    original_offer.status = OfferStatus.COUNTERED

    total_price = quantity * price_per_unit

    # Create new counter-offer pointing back to parent
    counter = Offer(
        listing_id=original_offer.listing_id,
        buyer_id=original_offer.buyer_id,
        seller_id=original_offer.seller_id,
        quantity=quantity,
        price_per_unit=price_per_unit,
        total_price=total_price,
        delivery_method=delivery_method or original_offer.delivery_method,
        payment_terms=payment_terms or original_offer.payment_terms,
        message=message,
        status=OfferStatus.PENDING,
        expires_at=expires_at,
        parent_offer_id=original_offer.id,
    )
    db.add(counter)
    await db.flush()
    return counter


async def accept_offer(
    db: AsyncSession,
    user: User,
    offer_id: int,
) -> Order:
    """Accept an offer atomically: updates offer, reserves stock, creates confirmed order."""
    offer = await get_offer_by_id(db, offer_id)

    if offer.status != OfferStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Offer cannot be accepted because its status is {offer.status.value}",
        )

    # Verify expiration
    if offer.expires_at and offer.expires_at < datetime.now(timezone.utc):
        offer.status = OfferStatus.EXPIRED
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This offer has expired and cannot be accepted",
        )

    # Both parties can accept depending on who sent the last counter, but let's allow either authorized participant
    if user.id not in [offer.buyer_id, offer.seller_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this negotiation",
        )

    # 1. Atomically reserve inventory with row-level lock
    listing = await reserve_stock(db, offer.listing_id, offer.quantity)

    # 2. Mark offer accepted
    offer.status = OfferStatus.ACCEPTED

    # 3. Determine fulfillment method
    method = None
    if offer.delivery_method:
        normalized = offer.delivery_method.upper()
        if "PICKUP" in normalized:
            method = FulfilmentMethod.BUYER_PICKUP
        elif "THIRD" in normalized:
            method = FulfilmentMethod.THIRD_PARTY
        else:
            method = FulfilmentMethod.SELLER_DELIVERY

    # 4. Create Order
    order = Order(
        offer_id=offer.id,
        buyer_id=offer.buyer_id,
        seller_id=offer.seller_id,
        listing_id=listing.id,
        commodity_id=listing.commodity_id,
        quantity=offer.quantity,
        reserved_quantity=offer.quantity,
        dispatched_quantity=Decimal("0.00"),
        delivered_quantity=Decimal("0.00"),
        price_per_unit=offer.price_per_unit,
        total_price=offer.total_price,
        status=OrderStatus.CONFIRMED,
        fulfilment_method=method,
    )
    db.add(order)
    await db.flush()
    return order


async def reject_offer(
    db: AsyncSession,
    user: User,
    offer_id: int,
) -> Offer:
    """Reject an offer."""
    offer = await get_offer_by_id(db, offer_id)

    if offer.status != OfferStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject offer with status {offer.status.value}",
        )

    if user.id not in [offer.buyer_id, offer.seller_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to reject this offer",
        )

    offer.status = OfferStatus.REJECTED
    await db.flush()
    return offer


async def withdraw_offer(
    db: AsyncSession,
    user: User,
    offer_id: int,
) -> Offer:
    """Withdraw an offer (can be done by the originator before acceptance)."""
    offer = await get_offer_by_id(db, offer_id)

    if offer.status != OfferStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot withdraw offer with status {offer.status.value}",
        )

    if user.id not in [offer.buyer_id, offer.seller_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to withdraw this offer",
        )

    offer.status = OfferStatus.WITHDRAWN
    await db.flush()
    return offer
