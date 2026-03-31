from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_db, require_manager
from app.models.user import User
from app.models.ai_result import AIAnalysis, AIInsightReport, AIChatSession, AIChatMessage
from app.schemas.ai import (
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
