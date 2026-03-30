"""Tests for campaign endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client, ClientStatus
from app.models.user import User


async def _create_client(db: AsyncSession, user: User) -> Client:
    client = Client(
        user_id=user.id,
        company_name="Test Brand Co.",
        status=ClientStatus.ACTIVE,
        currency="USD",
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@pytest.mark.asyncio
async def test_create_campaign(client: AsyncClient, manager_headers: dict, db_session: AsyncSession, manager_user: User):
    brand_client = await _create_client(db_session, manager_user)

    response = await client.post("/api/v1/campaigns", json={
        "name": "Summer Launch 2026",
        "campaign_type": "product_launch",
        "client_id": brand_client.id,
        "total_budget": 50000.00,
        "currency": "USD",
    }, headers=manager_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Summer Launch 2026"
    assert data["status"] == "draft"
    assert data["campaign_type"] == "product_launch"


@pytest.mark.asyncio
async def test_list_campaigns(client: AsyncClient, manager_headers: dict, db_session: AsyncSession, manager_user: User):
    response = await client.get("/api/v1/campaigns", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_campaign_unauthorized(client: AsyncClient):
    response = await client.post("/api/v1/campaigns", json={
        "name": "Test",
        "campaign_type": "sales",
        "client_id": 1,
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_campaign_not_found(client: AsyncClient, manager_headers: dict):
    response = await client.get("/api/v1/campaigns/99999", headers=manager_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_campaign_status(client: AsyncClient, manager_headers: dict, db_session: AsyncSession, manager_user: User):
    brand_client = await _create_client(db_session, manager_user)

    create_resp = await client.post("/api/v1/campaigns", json={
        "name": "Campaign to Update",
        "campaign_type": "brand_awareness",
        "client_id": brand_client.id,
    }, headers=manager_headers)
    campaign_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/campaigns/{campaign_id}",
        json={"status": "active"},
        headers=manager_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "active"
