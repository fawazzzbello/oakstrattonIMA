import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.campaign import Campaign
from app.models.client import Client, Brand
from app.models.influencer import Influencer
from app.models.social_account import SocialAccount
from app.models.user import User
from app.services.ai.client import ai_client

MATCHING_SYSTEM_PROMPT = """You are an expert influencer marketing strategist. Given a campaign brief and a list of available influencers, rank and score the best matches.

Return a JSON array of matches, each with these fields:
- influencer_id (int): The influencer's ID
- name (str): The influencer's full name
- match_score (float): 0.0 to 1.0 overall match score
- reasoning (str): 2-3 sentence explanation of why this influencer is a good match
- strengths (list[str]): Key strengths for this campaign
- concerns (list[str]): Potential concerns or risks

Scoring rubric (weight each equally):
1. Niche alignment — Does the influencer's content niche match the campaign's target niches?
2. Audience fit — Does the influencer's audience demographics align with the campaign's target audience?
3. Engagement quality — Does the influencer have strong engagement rates on relevant platforms?
4. Brand safety — Is the influencer's content appropriate for this brand?
5. Price/value — Is the influencer's rate reasonable relative to their reach and the campaign budget?

Return ONLY the JSON array, no other text."""


async def match_influencers(db: AsyncSession, campaign_id: int, max_results: int = 10) -> dict:
    """Match influencers to a campaign using AI analysis."""
    # Fetch campaign with brand info
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise ValueError(f"Campaign with id {campaign_id} not found")

    # Fetch brand if available
    brand_info = ""
    if campaign.brand_id:
        brand_result = await db.execute(
            select(Brand).where(Brand.id == campaign.brand_id)
        )
        brand = brand_result.scalar_one_or_none()
        if brand:
            brand_info = f"\nBrand: {brand.name}\nDescription: {brand.description or 'N/A'}\nIndustry: {brand.industry or 'N/A'}\nTarget Audience: {brand.target_audience or 'N/A'}"

    # Fetch client info
    client_result = await db.execute(
        select(Client).where(Client.id == campaign.client_id)
    )
    client = client_result.scalar_one_or_none()

    # Fetch all active influencers with social accounts
    inf_result = await db.execute(
        select(Influencer)
        .options(selectinload(Influencer.social_accounts), selectinload(Influencer.user))
        .where(Influencer.status == "active")
    )
    influencers = inf_result.scalars().all()

    if not influencers:
        return {"matches": [], "model_used": "none", "input_tokens": 0, "output_tokens": 0}

    # Build campaign context
    campaign_context = f"""Campaign: {campaign.name}
Type: {campaign.campaign_type.value if campaign.campaign_type else 'N/A'}
Description: {campaign.description or 'N/A'}
Target Niches: {json.dumps(campaign.target_niches or [])}
Target Platforms: {json.dumps(campaign.target_platforms or [])}
Budget: {campaign.total_budget or 'N/A'} {campaign.currency}
Target Countries: {json.dumps(campaign.target_countries or [])}
Min Followers: {campaign.min_follower_count or 'N/A'}
Max Followers: {campaign.max_follower_count or 'N/A'}
Client: {client.company_name if client else 'N/A'}{brand_info}"""

    # Build influencer list
    influencer_data = []
    for inf in influencers:
        social_summary = []
        for sa in inf.social_accounts:
            social_summary.append({
                "platform": sa.platform.value if hasattr(sa.platform, 'value') else str(sa.platform),
                "username": sa.username,
                "followers": sa.follower_count,
                "engagement_rate": float(sa.engagement_rate) if sa.engagement_rate else None,
                "avg_likes": float(sa.avg_likes) if sa.avg_likes else None,
            })
        influencer_data.append({
            "influencer_id": inf.id,
            "name": inf.user.full_name if inf.user else f"Influencer #{inf.id}",
            "niches": inf.niches or [],
            "location": inf.location,
            "country": inf.country_code,
            "bio": inf.bio,
            "rate_per_post": float(inf.rate_per_post) if inf.rate_per_post else None,
            "rate_per_reel": float(inf.rate_per_reel) if inf.rate_per_reel else None,
            "rate_per_video": float(inf.rate_per_video) if inf.rate_per_video else None,
            "trust_score": float(inf.trust_score) if inf.trust_score else None,
            "social_accounts": social_summary,
        })

    user_message = f"""Campaign Details:
{campaign_context}

Available Influencers ({len(influencer_data)} total):
{json.dumps(influencer_data, indent=2)}

Return the top {max_results} matches as a JSON array."""

    ai_result = await ai_client.generate_json(MATCHING_SYSTEM_PROMPT, user_message)

    matches = ai_result.get("parsed", [])
    if isinstance(matches, dict) and "matches" in matches:
        matches = matches["matches"]
    if not isinstance(matches, list):
        matches = []

    # Ensure we only return max_results
    matches = matches[:max_results]

    return {
        "matches": matches,
        "model_used": ai_result.get("model", "unknown"),
        "input_tokens": ai_result.get("input_tokens", 0),
        "output_tokens": ai_result.get("output_tokens", 0),
    }
