from app.schemas.ai import ContentAnalysisRequest
from app.services.ai.client import ai_client

CONTENT_ANALYSIS_SYSTEM_PROMPT = """You are an expert content reviewer for an influencer marketing agency. Analyze the provided content (caption, type, and context) and return a JSON object with the following fields:

{
  "brand_safety_score": <float 0.0-1.0, where 1.0 is perfectly brand-safe>,
  "quality_score": <float 0.0-1.0, where 1.0 is exceptional quality>,
  "engagement_prediction": <float 0.0-1.0, predicted engagement rate relative to platform average>,
  "issues": [<list of strings describing any problems found>],
  "suggestions": [<list of strings with actionable improvement suggestions>]
}

Scoring criteria:
- **Brand Safety**: Check for controversial topics, inappropriate language, competitor mentions, off-brand messaging, potential legal issues, FTC compliance
- **Quality**: Evaluate writing quality, creativity, hook strength, call-to-action effectiveness, hashtag strategy, emoji usage
- **Engagement Prediction**: Based on content type, caption length, hook quality, trending elements, audience relevance

Return ONLY the JSON object, no other text."""


async def analyze_content(request: ContentAnalysisRequest) -> dict:
    """Analyze content for brand safety, quality, and engagement prediction."""
    user_message = f"""Please analyze this influencer content:

Content Type: {request.deliverable_type}
Caption: {request.caption}
Content URL: {request.content_url or 'Not provided'}
Brand Context: {request.brand_context or 'Not provided'}
"""

    result = await ai_client.generate_json(CONTENT_ANALYSIS_SYSTEM_PROMPT, user_message)

    parsed = result.get("parsed", {})

    return {
        "brand_safety_score": float(parsed.get("brand_safety_score", 0.5)),
        "quality_score": float(parsed.get("quality_score", 0.5)),
        "engagement_prediction": float(parsed.get("engagement_prediction", 0.5)),
        "issues": parsed.get("issues", []),
        "suggestions": parsed.get("suggestions", []),
        "model_used": result.get("model", "unknown"),
        "input_tokens": result.get("input_tokens", 0),
        "output_tokens": result.get("output_tokens", 0),
    }
