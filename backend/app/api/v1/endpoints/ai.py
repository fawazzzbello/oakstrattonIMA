import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.deps import get_db, require_manager, require_admin
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.influencer import Influencer, InfluencerStatus
from app.models.social_account import SocialAccount
from app.models.ai_result import AIAnalysis, AIInsightReport, AIChatSession, AIChatMessage
from app.services.audit import log_action
from app.schemas.ai import (
    GenerateInfluencerRequest,
    GenerateInfluencerResponse,
    PortfolioImage,
    InfluencerMatchRequest,
    InfluencerMatchResponse,
    InfluencerMatchResult,
    CampaignBriefRequest,
    CampaignBriefResponse,
    ContentAnalysisRequest,
    ContentAnalysisResponse,
    AIInsightReportResponse,
    InsightReportGenerateRequest,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
)
from app.schemas.common import PaginatedResponse
from app.services.ai.client import ai_client

router = APIRouter(prefix="/ai", tags=["ai"])


def _check_ai_configured():
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="AI service not configured")


# ---- Influencer Matching ----

@router.post("/match-influencers", response_model=InfluencerMatchResponse)
async def match_influencers(
    data: InfluencerMatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    _check_ai_configured()
    from app.services.ai.matching import match_influencers as do_match

    try:
        result = await do_match(db, data.campaign_id, data.max_results)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Log the analysis
    analysis = AIAnalysis(
        analysis_type="matching",
        requested_by_id=current_user.id,
        subject_type="campaign",
        subject_id=data.campaign_id,
        model_used=result.get("model_used", settings.AI_MODEL),
        prompt_tokens=result.get("input_tokens"),
        completion_tokens=result.get("output_tokens"),
        result_json={"matches": result["matches"]},
    )
    db.add(analysis)
    await db.commit()

    matches = [
        InfluencerMatchResult(
            influencer_id=m.get("influencer_id", 0),
            name=m.get("name", "Unknown"),
            match_score=float(m.get("match_score", 0)),
            reasoning=m.get("reasoning", ""),
            strengths=m.get("strengths", []),
            concerns=m.get("concerns", []),
        )
        for m in result["matches"]
    ]

    return InfluencerMatchResponse(
        matches=matches,
        model_used=result.get("model_used", "unknown"),
    )


# ---- Campaign Brief Generation ----

@router.post("/generate-brief", response_model=CampaignBriefResponse)
async def generate_brief(
    data: CampaignBriefRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    _check_ai_configured()
    from app.services.ai.brief_generator import generate_brief as do_generate

    result = await do_generate(data)

    # Log the analysis
    analysis = AIAnalysis(
        analysis_type="brief",
        requested_by_id=current_user.id,
        model_used=result.get("model_used", settings.AI_MODEL),
        prompt_tokens=result.get("input_tokens"),
        completion_tokens=result.get("output_tokens"),
        result_json={
            "suggested_influencer_count": result["suggested_influencer_count"],
            "suggested_budget_split": result["suggested_budget_split"],
        },
    )
    db.add(analysis)
    await db.commit()

    return CampaignBriefResponse(
        brief_markdown=result["brief_markdown"],
        suggested_influencer_count=result["suggested_influencer_count"],
        suggested_budget_split=result["suggested_budget_split"],
        model_used=result.get("model_used", "unknown"),
    )


# ---- Content Analysis ----

@router.post("/analyze-content", response_model=ContentAnalysisResponse)
async def analyze_content(
    data: ContentAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    _check_ai_configured()
    from app.services.ai.content_analyzer import analyze_content as do_analyze

    result = await do_analyze(data)

    # Log the analysis
    analysis = AIAnalysis(
        analysis_type="content",
        requested_by_id=current_user.id,
        model_used=result.get("model_used", settings.AI_MODEL),
        prompt_tokens=result.get("input_tokens"),
        completion_tokens=result.get("output_tokens"),
        result_json={
            "brand_safety_score": result["brand_safety_score"],
            "quality_score": result["quality_score"],
            "engagement_prediction": result["engagement_prediction"],
        },
    )
    db.add(analysis)
    await db.commit()

    return ContentAnalysisResponse(
        brand_safety_score=result["brand_safety_score"],
        quality_score=result["quality_score"],
        engagement_prediction=result["engagement_prediction"],
        issues=result["issues"],
        suggestions=result["suggestions"],
        model_used=result.get("model_used", "unknown"),
    )


# ---- Insight Reports ----

@router.get("/insights", response_model=PaginatedResponse[AIInsightReportResponse])
async def list_insights(
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    count_result = await db.execute(select(func.count(AIInsightReport.id)))
    total = count_result.scalar() or 0

    result = await db.execute(
        select(AIInsightReport)
        .order_by(AIInsightReport.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    reports = result.scalars().all()

    return PaginatedResponse(items=reports, total=total, skip=skip, limit=limit)


@router.get("/insights/{report_id}", response_model=AIInsightReportResponse)
async def get_insight(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    result = await db.execute(
        select(AIInsightReport).where(AIInsightReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/insights/generate", response_model=AIInsightReportResponse)
async def generate_insight(
    data: InsightReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    _check_ai_configured()
    from app.services.ai.insights import generate_insights_report

    result = await generate_insights_report(db, data.report_type, current_user.id)
    await db.commit()
    return result


# ---- Chat Sessions ----

@router.get("/chat/sessions", response_model=list[ChatSessionResponse])
async def list_chat_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    result = await db.execute(
        select(AIChatSession)
        .where(AIChatSession.user_id == current_user.id, AIChatSession.is_active == True)  # noqa: E712
        .order_by(AIChatSession.created_at.desc())
    )
    return result.scalars().all()


@router.post("/chat/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_chat_session(
    data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    session = AIChatSession(
        user_id=current_user.id,
        session_name=data.session_name or "New Chat",
        context_type=data.context_type,
        context_id=data.context_id,
        is_active=True,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    await db.commit()
    return session


@router.get("/chat/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_chat_messages(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    # Verify session belongs to user
    result = await db.execute(
        select(AIChatSession).where(
            AIChatSession.id == session_id,
            AIChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    result = await db.execute(
        select(AIChatMessage)
        .where(AIChatMessage.session_id == session_id)
        .order_by(AIChatMessage.created_at.asc())
    )
    messages = result.scalars().all()
    return [
        ChatMessageResponse(role=m.role, content=m.content, session_id=m.session_id)
        for m in messages
    ]


@router.post("/chat/sessions/{session_id}/message", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: int,
    data: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    _check_ai_configured()

    # Verify session belongs to user
    result = await db.execute(
        select(AIChatSession).where(
            AIChatSession.id == session_id,
            AIChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Save user message
    user_msg = AIChatMessage(
        session_id=session_id,
        role="user",
        content=data.content,
    )
    db.add(user_msg)
    await db.flush()

    # Fetch conversation history for context
    result = await db.execute(
        select(AIChatMessage)
        .where(AIChatMessage.session_id == session_id)
        .order_by(AIChatMessage.created_at.asc())
    )
    history = result.scalars().all()

    # Build messages list for the AI
    messages = [{"role": m.role, "content": m.content} for m in history]

    system_prompt = (
        "You are an expert AI assistant for an influencer marketing agency called OakstrattonIMA. "
        "You help agency managers with campaign strategy, influencer selection, content ideas, "
        "analytics interpretation, and general marketing questions. "
        "Be concise, actionable, and data-driven in your responses."
    )

    if session.context_type:
        system_prompt += f"\n\nContext: This conversation is about a {session.context_type}."
        if session.context_id:
            system_prompt += f" (ID: {session.context_id})"

    # Call AI
    try:
        response = await ai_client._client.messages.create(
            model=settings.AI_MODEL,
            max_tokens=settings.AI_MAX_TOKENS,
            system=system_prompt,
            messages=messages,
        )
        ai_content = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    # Save assistant message
    assistant_msg = AIChatMessage(
        session_id=session_id,
        role="assistant",
        content=ai_content,
        prompt_tokens=input_tokens,
        completion_tokens=output_tokens,
    )
    db.add(assistant_msg)
    await db.commit()

    return ChatMessageResponse(
        role="assistant",
        content=ai_content,
        session_id=session_id,
    )


@router.delete("/chat/sessions/{session_id}", status_code=204)
async def archive_chat_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    result = await db.execute(
        select(AIChatSession).where(
            AIChatSession.id == session_id,
            AIChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    session.is_active = False
    await db.commit()


# ---- AI Influencer Generation ----

@router.post("/generate-influencer", response_model=GenerateInfluencerResponse, status_code=201)
async def generate_influencer(
    data: GenerateInfluencerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    _check_ai_configured()
    from app.services.ai.profile_generator import generate_influencer_profile

    # 1. Generate profile via Claude
    profile = await generate_influencer_profile(
        gender=data.gender,
        age_range=data.age_range,
        niche=data.niche,
        ethnicity=data.ethnicity,
        extra_instructions=data.extra_instructions,
    )

    ai_meta = profile.pop("_ai_meta", {})

    # 2. Create synthetic user account
    first_name = profile.get("first_name", "AI")
    last_name = profile.get("last_name", "Model")
    unique_id = uuid.uuid4().hex[:12]
    email = f"ai.generated.{unique_id}@oakstrattonima.internal"

    user = User(
        email=email,
        full_name=f"{first_name} {last_name}",
        hashed_password=get_password_hash(uuid.uuid4().hex),
        role=UserRole.INFLUENCER,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    # 3. Create influencer record
    rates = profile.get("rates", {})
    demographics = profile.get("audience_demographics", {})

    influencer = Influencer(
        user_id=user.id,
        status=InfluencerStatus.ACTIVE,
        bio=profile.get("bio"),
        location=profile.get("location"),
        country_code=profile.get("country_code"),
        language=profile.get("language", "en"),
        niches=profile.get("niches", []),
        tags=profile.get("tags", []),
        ai_generated=True,
        physical_attributes=profile.get("physical_attributes"),
        portfolio_images=profile.get("portfolio_images", []),
        appearance_prompt=profile.get("appearance_prompt"),
        rate_per_post=rates.get("rate_per_post"),
        rate_per_story=rates.get("rate_per_story"),
        rate_per_reel=rates.get("rate_per_reel"),
        rate_per_video=rates.get("rate_per_video"),
        audience_age_18_24=demographics.get("age_18_24"),
        audience_age_25_34=demographics.get("age_25_34"),
        audience_age_35_44=demographics.get("age_35_44"),
        audience_age_45_plus=demographics.get("age_45_plus"),
        audience_gender_female=demographics.get("gender_female"),
        audience_gender_male=demographics.get("gender_male"),
        audience_top_countries=demographics.get("top_countries", []),
    )
    db.add(influencer)
    await db.flush()

    # 4. Create social accounts
    social_count = 0
    for acct in profile.get("social_accounts", []):
        sa = SocialAccount(
            influencer_id=influencer.id,
            platform=acct.get("platform", "instagram"),
            username=acct.get("username", ""),
            follower_count=acct.get("follower_count", 0),
            following_count=acct.get("following_count", 0),
            post_count=acct.get("post_count", 0),
            engagement_rate=acct.get("engagement_rate", 0.0),
            is_verified=acct.get("is_verified", False),
            is_primary=acct.get("is_primary", False),
        )
        db.add(sa)
        social_count += 1

    # 5. Log the AI analysis
    analysis = AIAnalysis(
        analysis_type="influencer_generation",
        requested_by_id=current_user.id,
        subject_type="influencer",
        subject_id=influencer.id,
        model_used=ai_meta.get("model", settings.AI_MODEL),
        prompt_tokens=ai_meta.get("input_tokens"),
        completion_tokens=ai_meta.get("output_tokens"),
        result_json={"influencer_id": influencer.id, "user_id": user.id},
    )
    db.add(analysis)

    await log_action(db, current_user.id, "generate_ai_influencer", "influencer", influencer.id, {
        "full_name": f"{first_name} {last_name}",
        "niches": profile.get("niches", []),
    })

    await db.commit()

    portfolio_images = [
        PortfolioImage(
            url=img.get("url", ""),
            caption=img.get("caption", ""),
            image_type=img.get("image_type", "portrait"),
            setting=img.get("setting"),
            mood=img.get("mood"),
        )
        for img in profile.get("portfolio_images", [])
    ]

    return GenerateInfluencerResponse(
        influencer_id=influencer.id,
        user_id=user.id,
        full_name=f"{first_name} {last_name}",
        bio=profile.get("bio"),
        location=profile.get("location"),
        niches=profile.get("niches", []),
        physical_attributes=profile.get("physical_attributes"),
        appearance_prompt=profile.get("appearance_prompt"),
        portfolio_images=portfolio_images,
        social_accounts_created=social_count,
        model_used=ai_meta.get("model", "unknown"),
    )
