"""Review and Rating endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.review import Review
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.schemas.review import ReviewCreate
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_review(
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a review after order completion. Enforces transaction eligibility."""
    result = await db.execute(select(Order).where(Order.id == data.order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Eligibility: Order must be delivered or completed
    if order.status not in [OrderStatus.DELIVERED, OrderStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviews can only be submitted for delivered or completed orders",
        )

    # Must be a participant
    if current_user.id not in [order.buyer_id, order.seller_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this order",
        )

    # Prevent duplicate review from same user for same order
    existing = await db.execute(
        select(Review).where(
            Review.order_id == data.order_id,
            Review.reviewer_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted a review for this transaction",
        )

    reviewee_id = order.seller_id if current_user.id == order.buyer_id else order.buyer_id

    review = Review(
        order_id=data.order_id,
        reviewer_id=current_user.id,
        reviewee_id=reviewee_id,
        rating=data.rating,
        comment=data.comment,
        is_visible=True,
    )
    db.add(review)
    await db.flush()
    return {"id": review.id, "message": "Review submitted successfully"}


@router.get("/user/{user_id}")
async def get_user_reviews(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get reviews and aggregate rating received by a farmer or buyer."""
    stmt = (
        select(Review)
        .options(selectinload(Review.reviewer))
        .where(Review.reviewee_id == user_id, Review.is_visible == True)
        .order_by(Review.created_at.desc())
    )
    result = await db.execute(stmt)
    reviews = result.scalars().all()

    avg_rating = (
        round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0.0
    )

    return {
        "user_id": user_id,
        "average_rating": avg_rating,
        "total_reviews": len(reviews),
        "reviews": [
            {
                "id": r.id,
                "rating": r.rating,
                "comment": r.comment,
                "reviewer_name": r.reviewer.full_name if r.reviewer else "Verified User",
                "created_at": r.created_at.isoformat(),
            }
            for r in reviews
        ],
    }
