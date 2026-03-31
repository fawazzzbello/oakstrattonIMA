from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign, CampaignStatus, CampaignInfluencer, CampaignMetrics
from app.models.influencer import Influencer
from app.models.client import Client
from app.models.payment import Invoice, InvoiceStatus
from app.models.user import User
from app.models.ai_result import AIInsightReport
from app.services.ai.client import ai_client
from app.core.config import settings

INSIGHTS_SYSTEM_PROMPT = """You are a senior analytics strategist at a top influencer marketing agency. Given platform metrics and data, write a comprehensive insights report in markdown format.

Structure the report as follows:
1. **Executive Summary** — 2-3 sentence overview of key findings
2. **Campaign Performance** — analysis of active and recently completed campaigns
3. **Influencer Roster Health** — active influencers, new additions, engagement trends
4. **Financial Overview** — revenue, outstanding invoices, payout trends
5. **Key Wins** — highlight top-performing campaigns or influencers
6. **Areas of Concern** — any red flags or declining metrics
7. **Recommendations** — 3-5 actionable recommendations for the next period

Also return a JSON block at the very end with:
```json
{
  "key_metrics": {
    "total_active_campaigns": <int>,
    "avg_engagement_rate": <float>,
    "total_revenue_period": <float>,
    "top_performing_campaign": "<string>",
    "influencer_utilization_rate": <float>
  },
  "recommendations": [
    {"priority": "high|medium|low", "title": "<string>", "description": "<string>"}
  ]
}
```
"""


async def generate_insights_report(db: AsyncSession, report_type: str, user_id: int) -> dict:
    """Generate an AI-powered insights report from platform data."""
    now = datetime.now(timezone.utc)

    if report_type == "weekly":
        period_start = now - timedelta(days=7)
    else:
        period_start = now - timedelta(days=30)

    # Aggregate platform data
    # Campaign counts by status
    campaign_counts = {}
    for status in CampaignStatus:
        result = await db.execute(
            select(sa_func.count(Campaign.id)).where(Campaign.status == status)
        )
        campaign_counts[status.value] = result.scalar() or 0

    # Active influencer count
    result = await db.execute(
        select(sa_func.count(Influencer.id)).where(Influencer.status == "active")
    )
    active_influencers = result.scalar() or 0

    # Total influencer count
    result = await db.execute(select(sa_func.count(Influencer.id)))
    total_influencers = result.scalar() or 0

    # Client count
    result = await db.execute(select(sa_func.count(Client.id)))
    total_clients = result.scalar() or 0

    # Revenue from paid invoices in the period
    result = await db.execute(
        select(sa_func.sum(Invoice.total_amount)).where(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.paid_at >= period_start,
        )
    )
    period_revenue = float(result.scalar() or 0)

    # Total outstanding invoices
    result = await db.execute(
        select(sa_func.sum(Invoice.total_amount)).where(
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.VIEWED, InvoiceStatus.OVERDUE])
        )
    )
    outstanding_invoices = float(result.scalar() or 0)

    # Campaign metrics averages for active campaigns
    result = await db.execute(
        select(
            sa_func.avg(CampaignMetrics.avg_engagement_rate),
            sa_func.sum(CampaignMetrics.total_reach),
            sa_func.sum(CampaignMetrics.total_impressions),
        ).join(Campaign, Campaign.id == CampaignMetrics.campaign_id).where(
            Campaign.status == CampaignStatus.ACTIVE
        )
    )
    metrics_row = result.one_or_none()
    avg_engagement = float(metrics_row[0]) if metrics_row and metrics_row[0] else 0.0
    total_reach = int(metrics_row[1]) if metrics_row and metrics_row[1] else 0
    total_impressions = int(metrics_row[2]) if metrics_row and metrics_row[2] else 0

    # Number of influencers currently assigned to campaigns
    result = await db.execute(
        select(sa_func.count(sa_func.distinct(CampaignInfluencer.influencer_id))).join(
            Campaign, Campaign.id == CampaignInfluencer.campaign_id
        ).where(Campaign.status == CampaignStatus.ACTIVE)
    )
    assigned_influencers = result.scalar() or 0

    # Build the data summary for the AI
    data_summary = f"""Platform Data Summary ({report_type.capitalize()} Report)
Period: {period_start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}

Campaign Counts by Status:
{chr(10).join(f'  - {k}: {v}' for k, v in campaign_counts.items())}

Influencer Stats:
  - Total influencers: {total_influencers}
  - Active influencers: {active_influencers}
  - Currently assigned to active campaigns: {assigned_influencers}

Client Stats:
  - Total clients: {total_clients}

Financial Summary:
  - Revenue this period (paid invoices): ${period_revenue:,.2f}
  - Outstanding invoices: ${outstanding_invoices:,.2f}

Performance Metrics (Active Campaigns):
  - Average engagement rate: {avg_engagement:.4f}
  - Total reach: {total_reach:,}
  - Total impressions: {total_impressions:,}
"""

    ai_result = await ai_client.generate(INSIGHTS_SYSTEM_PROMPT, data_summary)

    content = ai_result["content"]

    # Try to extract JSON block
    import json
    key_metrics = {}
    recommendations = []

    json_start = content.rfind("```json")
    if json_start != -1:
        json_text = content[json_start + 7:]
        json_end = json_text.find("```")
        if json_end != -1:
            json_text = json_text[:json_end].strip()
        try:
            parsed = json.loads(json_text)
            key_metrics = parsed.get("key_metrics", {})
            recommendations = parsed.get("recommendations", [])
        except json.JSONDecodeError:
            pass
        report_markdown = content[:json_start].strip()
    else:
        report_markdown = content

    # Save the report to the database
    report = AIInsightReport(
        report_type=report_type,
        period_start=period_start,
        period_end=now,
        generated_by="manual",
        requested_by_id=user_id,
        model_used=ai_result.get("model", settings.AI_MODEL),
        report_markdown=report_markdown,
        key_metrics=key_metrics,
        recommendations=recommendations,
        status="completed",
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    return {
        "id": report.id,
        "report_type": report.report_type,
        "period_start": report.period_start,
        "period_end": report.period_end,
        "generated_by": report.generated_by,
        "requested_by_id": report.requested_by_id,
        "model_used": report.model_used,
        "report_markdown": report.report_markdown,
        "key_metrics": report.key_metrics,
        "recommendations": report.recommendations,
        "status": report.status,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
    }
