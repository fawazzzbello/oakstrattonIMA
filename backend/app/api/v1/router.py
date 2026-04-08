from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, influencers, campaigns, clients, analytics, payments, contracts, notifications,
    admin, ai, directory, sales,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(influencers.router)
api_router.include_router(campaigns.router)
api_router.include_router(clients.router)
api_router.include_router(analytics.router)
api_router.include_router(payments.router)
api_router.include_router(contracts.router)
api_router.include_router(notifications.router)
api_router.include_router(admin.router)
api_router.include_router(ai.router)
api_router.include_router(directory.router)
api_router.include_router(sales.router)
