#!/usr/bin/env python3
"""
OakstrattonIMA — Database Seeder
Creates demo data for development and testing.

Usage:
    cd backend && python ../scripts/seed.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.session import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.influencer import Influencer, InfluencerStatus, ContentNiche
from app.models.social_account import SocialAccount, SocialPlatform
from app.models.client import Client, Brand, ClientStatus
from app.models.campaign import Campaign, CampaignStatus, CampaignType
from datetime import date, timedelta


async def seed():
    async with AsyncSessionLocal() as db:
        print("Seeding database...")

        # Admin user
        admin = User(
            email="admin@oakstrattonima.com",
            hashed_password=get_password_hash("admin123!"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )
        db.add(admin)

        # Manager
        manager = User(
            email="manager@oakstrattonima.com",
            hashed_password=get_password_hash("manager123!"),
            full_name="Jane Manager",
            role=UserRole.MANAGER,
            is_active=True,
            is_verified=True,
        )
        db.add(manager)

        # Client user
        client_user = User(
            email="client@brandco.com",
            hashed_password=get_password_hash("client123!"),
            full_name="Bob Brand",
            role=UserRole.CLIENT,
            is_active=True,
            is_verified=True,
        )
        db.add(client_user)

        # Influencer users
        inf_users = []
        for i, (name, email) in enumerate([
            ("Sofia Martinez", "sofia@influencer.com"),
            ("Jake Chen", "jake@influencer.com"),
            ("Priya Sharma", "priya@influencer.com"),
        ]):
            u = User(
                email=email,
                hashed_password=get_password_hash("influencer123!"),
                full_name=name,
                role=UserRole.INFLUENCER,
                is_active=True,
                is_verified=True,
            )
            db.add(u)
            inf_users.append(u)

        await db.flush()

        # Client profile
        client = Client(
            user_id=client_user.id,
            company_name="BrandCo Inc.",
            company_website="https://brandco.example.com",
            industry="Consumer Goods",
            status=ClientStatus.ACTIVE,
            monthly_budget=50000,
            billing_email="billing@brandco.com",
            account_manager_id=manager.id,
        )
        db.add(client)
        await db.flush()

        # Brand
        brand = Brand(
            client_id=client.id,
            name="BrandCo Beauty",
            description="Premium beauty products",
            website="https://beauty.brandco.example.com",
            industry="Beauty",
            is_active=True,
        )
        db.add(brand)

        # Influencer profiles
        influencers = []
        profiles = [
            {
                "niches": ["beauty", "lifestyle"],
                "location": "Los Angeles, CA",
                "rate_per_post": 2500,
                "rate_per_reel": 3500,
                "username_ig": "sofiabeauty",
                "followers_ig": 285000,
                "eng_rate": 0.0412,
            },
            {
                "niches": ["tech", "gaming"],
                "location": "New York, NY",
                "rate_per_post": 1800,
                "rate_per_video": 4500,
                "username_ig": "jakestech",
                "followers_ig": 156000,
                "eng_rate": 0.0287,
            },
            {
                "niches": ["fitness", "health"],
                "location": "Austin, TX",
                "rate_per_post": 1200,
                "rate_per_reel": 2000,
                "username_ig": "priyafitness",
                "followers_ig": 98000,
                "eng_rate": 0.0538,
            },
        ]

        for u, p in zip(inf_users, profiles):
            inf = Influencer(
                user_id=u.id,
                status=InfluencerStatus.ACTIVE,
                niches=p["niches"],
                location=p["location"],
                country_code="US",
                rate_per_post=p.get("rate_per_post"),
                rate_per_reel=p.get("rate_per_reel"),
                rate_per_video=p.get("rate_per_video"),
                currency="USD",
                trust_score=8.5,
            )
            db.add(inf)
            influencers.append(inf)
        await db.flush()

        for inf, u, p in zip(influencers, inf_users, profiles):
            sa = SocialAccount(
                influencer_id=inf.id,
                platform=SocialPlatform.INSTAGRAM,
                username=p["username_ig"],
                profile_url=f"https://instagram.com/{p['username_ig']}",
                follower_count=p["followers_ig"],
                engagement_rate=p["eng_rate"],
                is_verified=True,
                is_primary=True,
            )
            db.add(sa)

        # Campaign
        today = date.today()
        campaign = Campaign(
            client_id=client.id,
            brand_id=brand.id,
            manager_id=manager.id,
            name="Summer Beauty Launch 2025",
            description="Launch campaign for our new summer beauty line targeting Gen Z & Millennials.",
            campaign_type=CampaignType.PRODUCT_LAUNCH,
            status=CampaignStatus.ACTIVE,
            start_date=today,
            end_date=today + timedelta(days=30),
            content_deadline=today + timedelta(days=20),
            total_budget=15000,
            influencer_budget=12000,
            agency_fee=3000,
            currency="USD",
            target_reach=500000,
            target_impressions=1500000,
            target_engagement_rate=0.04,
            tracking_hashtags=["#OakstrattonSummer", "#BrandCoBeauty"],
            ftc_disclosure_required=True,
            brief_text="Create authentic content showcasing BrandCo's summer beauty collection. Focus on everyday application, natural lighting, and honest reviews. FTC disclosure required on all posts.",
        )
        db.add(campaign)

        await db.commit()
        print("✓ Seeded successfully!")
        print()
        print("Demo credentials:")
        print("  Admin:    admin@oakstrattonima.com / admin123!")
        print("  Manager:  manager@oakstrattonima.com / manager123!")
        print("  Client:   client@brandco.com / client123!")
        print("  Influencer: sofia@influencer.com / influencer123!")


if __name__ == "__main__":
    asyncio.run(seed())
