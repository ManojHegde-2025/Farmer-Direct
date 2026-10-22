"""Inventory service with row-level locking to prevent overselling.

Enforces ACID transactional stock reservations and releases.
"""

from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing, ListingStatus


async def get_listing_with_lock(db: AsyncSession, listing_id: int) -> Listing:
    """Fetch a listing with pessimistic row-level write lock (SELECT FOR UPDATE)."""
    stmt = (
        select(Listing)
        .where(Listing.id == listing_id)
        .with_for_update()
    )
    result = await db.execute(stmt)
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produce listing #{listing_id} not found",
        )
    return listing


async def reserve_stock(
    db: AsyncSession,
    listing_id: int,
    quantity_to_reserve: Decimal,
) -> Listing:
    """Reserve stock atomically with row-level locking.

    Raises 400 Bad Request if requested quantity exceeds available stock.
    Updates listing status to PARTIALLY_RESERVED or SOLD_OUT.
    """
    if quantity_to_reserve <= Decimal("0"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation quantity must be strictly greater than zero",
        )

    listing = await get_listing_with_lock(db, listing_id)

    # Check listing status allows purchase
    if listing.status not in [ListingStatus.ACTIVE, ListingStatus.PARTIALLY_RESERVED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Listing is not available for purchase (status: {listing.status.value})",
        )

    if listing.available_quantity < quantity_to_reserve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Insufficient stock available. Requested: {quantity_to_reserve} {listing.unit}, "
                f"Available: {listing.available_quantity} {listing.unit}"
            ),
        )

    # Deduct available quantity
    listing.available_quantity -= quantity_to_reserve

    if listing.available_quantity == Decimal("0"):
        listing.status = ListingStatus.SOLD_OUT
    else:
        listing.status = ListingStatus.PARTIALLY_RESERVED

    await db.flush()
    return listing


async def release_stock(
    db: AsyncSession,
    listing_id: int,
    quantity_to_release: Decimal,
) -> Listing:
    """Release previously reserved stock back to the listing.

    Used when an order is cancelled or an offer is voided.
    """
    if quantity_to_release <= Decimal("0"):
        return await get_listing_with_lock(db, listing_id)

    listing = await get_listing_with_lock(db, listing_id)

    listing.available_quantity += quantity_to_release
    # Cap available_quantity at total listing quantity
    if listing.available_quantity > listing.quantity:
        listing.available_quantity = listing.quantity

    if listing.available_quantity == listing.quantity:
        listing.status = ListingStatus.ACTIVE
    elif listing.available_quantity > Decimal("0"):
        listing.status = ListingStatus.PARTIALLY_RESERVED

    await db.flush()
    return listing
