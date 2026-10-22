"""API v1 Router aggregating all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    farmers,
    buyers,
    commodities,
    listings,
    requirements,
    reference_prices,
    matching,
    offers,
    orders,
    payments,
    deliveries,
    disputes,
    reviews,
    admin,
    health,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(farmers.router, prefix="/farmers", tags=["Farmers"])
api_router.include_router(buyers.router, prefix="/buyers", tags=["Buyers"])
api_router.include_router(commodities.router, prefix="/commodities", tags=["Commodities"])
api_router.include_router(listings.router, prefix="/listings", tags=["Listings"])
api_router.include_router(requirements.router, prefix="/requirements", tags=["Buyer Requirements"])
api_router.include_router(reference_prices.router, prefix="/reference-prices", tags=["Reference Prices"])
api_router.include_router(matching.router, prefix="/matching", tags=["Matching Engine"])
api_router.include_router(offers.router, prefix="/offers", tags=["Offers & Negotiation"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders & Fulfillment"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(deliveries.router, prefix="/deliveries", tags=["Logistics & Deliveries"])
api_router.include_router(disputes.router, prefix="/disputes", tags=["Disputes"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews & Ratings"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])
