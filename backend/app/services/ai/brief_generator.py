from app.schemas.ai import CampaignBriefRequest
from app.services.ai.client import ai_client

BRIEF_SYSTEM_PROMPT = """You are an expert influencer marketing strategist at a top-tier agency. Given product details and campaign parameters, generate a comprehensive campaign brief in markdown format.

The brief should include:
1. **Campaign Overview** — name suggestion, objective, key message
2. **Target Audience** — demographics, psychographics, online behavior
3. **Platform Strategy** — which platforms to prioritize and why
4. **Content Pillars** — 3-5 content themes/angles
5. **Influencer Criteria** — ideal influencer profile, tier mix (nano/micro/macro/mega)
6. **Content Guidelines** — dos and don'ts, tone of voice, required elements
7. **Timeline** — suggested phases (teaser, launch, sustain)
8. **Budget Allocation** — suggested split across influencer tiers, platforms, and content types
9. **KPIs & Success Metrics** — what to measure and target benchmarks
10. **FTC/Legal Notes** — disclosure requirements

Also return a JSON block at the very end of your response with this exact structure (after the markdown):
```json
{
  "suggested_influencer_count": <int>,
  "suggested_budget_split": {
    "nano_influencers": <percentage as float>,
    "micro_influencers": <percentage as float>,
    "macro_influencers": <percentage as float>,
    "mega_influencers": <percentage as float>,
    "production_costs": <percentage as float>,
    "paid_amplification": <percentage as float>
  }
}
```
"""


async def generate_brief(request: CampaignBriefRequest) -> dict:
    """Generate a comprehensive campaign brief using AI."""
    user_message = f"""Please generate a detailed influencer marketing campaign brief for the following:

Product/Brand: {request.product_name}
Description: {request.product_description}
Target Audience: {request.target_audience}
Budget Range: {request.budget_range}
Campaign Type: {request.campaign_type}
Platforms: {', '.join(request.platforms)}
Duration: {request.duration_weeks} weeks
"""

    result = await ai_client.generate(BRIEF_SYSTEM_PROMPT, user_message)

    content = result["content"]

    # Try to extract the JSON block from the end of the response
    import json
    suggested_influencer_count = 10
    suggested_budget_split = {}

    json_start = content.rfind("```json")
    if json_start != -1:
        json_text = content[json_start + 7:]
        json_end = json_text.find("```")
        if json_end != -1:
            json_text = json_text[:json_end].strip()
        try:
            parsed = json.loads(json_text)
            suggested_influencer_count = parsed.get("suggested_influencer_count", 10)
            suggested_budget_split = parsed.get("suggested_budget_split", {})
        except json.JSONDecodeError:
            pass
        # Remove the JSON block from markdown
        brief_markdown = content[:json_start].strip()
    else:
        brief_markdown = content

    return {
        "brief_markdown": brief_markdown,
        "suggested_influencer_count": suggested_influencer_count,
        "suggested_budget_split": suggested_budget_split,
        "model_used": result.get("model", "unknown"),
        "input_tokens": result.get("input_tokens", 0),
        "output_tokens": result.get("output_tokens", 0),
    }
