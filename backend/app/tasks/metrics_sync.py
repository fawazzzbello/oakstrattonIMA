"""Celery tasks for syncing social media metrics."""
import asyncio
from app.tasks.worker import celery_app


@celery_app.task
def sync_all_active_campaign_metrics():
    """Sync metrics for all active campaigns."""
    asyncio.run(_sync_all_active_campaign_metrics())


async def _sync_all_active_campaign_metrics():
    from app.db.session import AsyncSessionLocal
    from app.models.campaign import Campaign, CampaignStatus
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Campaign).where(Campaign.status == CampaignStatus.ACTIVE)
        )
        campaigns = result.scalars().all()

        for campaign in campaigns:
            sync_campaign_metrics.delay(campaign.id)


@celery_app.task(bind=True, max_retries=3)
def sync_campaign_metrics(self, campaign_id: int):
    """Sync metrics for a single campaign by pulling deliverable post metrics."""
    try:
        asyncio.run(_sync_campaign_metrics(campaign_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


async def _sync_campaign_metrics(campaign_id: int):
    from app.db.session import AsyncSessionLocal
    from app.models.campaign import (
        Campaign, CampaignInfluencer, Deliverable, CampaignMetrics,
        DeliverableStatus,
    )
    from app.models.social_account import SocialAccount
    from sqlalchemy import select
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        # Get all published deliverables
        cis_result = await db.execute(
            select(CampaignInfluencer).where(
                CampaignInfluencer.campaign_id == campaign_id
            )
        )
        cis = cis_result.scalars().all()
        ci_ids = [ci.id for ci in cis]

        deliverables_result = await db.execute(
            select(Deliverable).where(
                Deliverable.campaign_influencer_id.in_(ci_ids),
                Deliverable.status == DeliverableStatus.PUBLISHED,
                Deliverable.live_url.isnot(None),
            )
        )
        deliverables = deliverables_result.scalars().all()

        # Aggregate metrics from post_metrics JSON
        total_reach = 0
        total_impressions = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0
        total_saves = 0
        total_views = 0
        total_clicks = 0
        engagement_rates = []

        for d in deliverables:
            if not d.post_metrics:
                continue
            m = d.post_metrics
            total_reach += m.get("reach", 0)
            total_impressions += m.get("impressions", 0)
            total_likes += m.get("likes", 0)
            total_comments += m.get("comments", 0)
            total_shares += m.get("shares", 0)
            total_saves += m.get("saves", 0)
            total_views += m.get("views", 0)
            total_clicks += m.get("clicks", 0)
            if m.get("engagement_rate"):
                engagement_rates.append(m["engagement_rate"])

        avg_eng = sum(engagement_rates) / len(engagement_rates) if engagement_rates else None

        # Upsert campaign metrics
        metrics_result = await db.execute(
            select(CampaignMetrics).where(CampaignMetrics.campaign_id == campaign_id)
        )
        metrics = metrics_result.scalar_one_or_none()

        if not metrics:
            metrics = CampaignMetrics(campaign_id=campaign_id)
            db.add(metrics)

        metrics.total_reach = total_reach or None
        metrics.total_impressions = total_impressions or None
        metrics.total_likes = total_likes or None
        metrics.total_comments = total_comments or None
        metrics.total_shares = total_shares or None
        metrics.total_saves = total_saves or None
        metrics.total_views = total_views or None
        metrics.total_clicks = total_clicks or None
        metrics.avg_engagement_rate = avg_eng
        metrics.influencer_count = len(cis)
        metrics.deliverable_count = len(deliverables)
        metrics.last_synced_at = datetime.now(timezone.utc)

        await db.commit()


@celery_app.task(bind=True, max_retries=3)
def refresh_influencer_social_metrics(self, social_account_id: int):
    """Pull fresh metrics for a single social account from the platform API."""
    try:
        asyncio.run(_refresh_social_metrics(social_account_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=600)


async def _refresh_social_metrics(social_account_id: int):
    from app.db.session import AsyncSessionLocal
    from app.models.social_account import SocialAccount, SocialPlatform
    from sqlalchemy import select
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SocialAccount).where(SocialAccount.id == social_account_id)
        )
        account = result.scalar_one_or_none()
        if not account:
            return

        # Platform-specific metric fetching
        metrics = {}
        if account.platform == SocialPlatform.INSTAGRAM:
            metrics = await _fetch_instagram_metrics(account)
        elif account.platform == SocialPlatform.TIKTOK:
            metrics = await _fetch_tiktok_metrics(account)
        elif account.platform == SocialPlatform.YOUTUBE:
            metrics = await _fetch_youtube_metrics(account)

        if metrics:
            account.follower_count = metrics.get("follower_count")
            account.following_count = metrics.get("following_count")
            account.post_count = metrics.get("post_count")
            account.avg_likes = metrics.get("avg_likes")
            account.avg_comments = metrics.get("avg_comments")
            account.avg_views = metrics.get("avg_views")
            account.engagement_rate = metrics.get("engagement_rate")
            account.metrics_updated_at = datetime.now(timezone.utc)
            await db.commit()


async def _fetch_instagram_metrics(account) -> dict:
    """Fetch Instagram metrics via Graph API."""
    from app.core.config import settings

    if not account.access_token:
        return {}

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://graph.instagram.com/me",
                params={
                    "fields": "followers_count,follows_count,media_count",
                    "access_token": account.access_token,
                },
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "follower_count": data.get("followers_count"),
                    "following_count": data.get("follows_count"),
                    "post_count": data.get("media_count"),
                }
    except Exception as e:
        print(f"Instagram API error: {e}")
    return {}


async def _fetch_tiktok_metrics(account) -> dict:
    """Fetch TikTok metrics via TikTok API."""
    from app.core.config import settings

    if not account.access_token:
        return {}

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://open.tiktokapis.com/v2/user/info/",
                headers={"Authorization": f"Bearer {account.access_token}"},
                params={"fields": "follower_count,following_count,likes_count,video_count"},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json().get("data", {}).get("user", {})
                return {
                    "follower_count": data.get("follower_count"),
                    "following_count": data.get("following_count"),
                    "post_count": data.get("video_count"),
                }
    except Exception as e:
        print(f"TikTok API error: {e}")
    return {}


async def _fetch_youtube_metrics(account) -> dict:
    """Fetch YouTube metrics via Data API v3."""
    from app.core.config import settings

    if not settings.YOUTUBE_API_KEY:
        return {}

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "statistics",
                    "forUsername": account.username,
                    "key": settings.YOUTUBE_API_KEY,
                },
                timeout=10,
            )
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                if items:
                    stats = items[0].get("statistics", {})
                    return {
                        "follower_count": int(stats.get("subscriberCount", 0)),
                        "post_count": int(stats.get("videoCount", 0)),
                    }
    except Exception as e:
        print(f"YouTube API error: {e}")
    return {}
