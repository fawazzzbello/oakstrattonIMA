"""
AI Influencer Profile Generator
Generates a complete, realistic influencer/model profile using Claude,
including physical attributes, social stats, portfolio image concepts,
and a stable appearance prompt for consistent image generation.
"""
import hashlib
from app.services.ai.client import ai_client


SYSTEM_PROMPT = """\
You are a world-class talent agency creative director. Your job is to generate
a fully-realized, realistic influencer / model profile for a marketing agency's
roster.  The profile must feel authentic and production-ready.

Reply with ONLY valid JSON — no markdown fences, no commentary.

Required JSON schema:
{
  "first_name": "<string>",
  "last_name": "<string>",
  "age": <int 18-45>,
  "gender": "<male|female|non-binary>",
  "location": "<City, State/Country>",
  "country_code": "<ISO 3166-1 alpha-2>",
  "bio": "<2-3 sentence influencer bio>",
  "niches": ["<niche>", ...],          // 2-4 niches from: fashion, beauty, fitness, food, travel, tech, gaming, lifestyle, business, education, entertainment, health, sports
  "tags": ["<tag>", ...],              // 4-8 descriptive tags
  "language": "<ISO 639-1>",

  "physical_attributes": {
    "height_cm": <int>,
    "hair_color": "<string>",
    "hair_style": "<string>",
    "eye_color": "<string>",
    "skin_tone": "<string>",
    "body_type": "<slim|athletic|curvy|average|muscular>",
    "ethnicity": "<string>",
    "distinguishing_features": "<string or empty>"
  },

  "appearance_prompt": "<A single, detailed paragraph (60-100 words) describing this person's face and appearance with enough specificity to generate consistent images. Include face shape, bone structure, expression style, skin texture, hair details, and any unique features. This must read like a casting director's description.>",

  "social_accounts": [
    {
      "platform": "<instagram|tiktok|youtube|twitter>",
      "username": "<realistic handle>",
      "follower_count": <int>,
      "following_count": <int>,
      "post_count": <int>,
      "engagement_rate": <float 0.01-0.12>,
      "is_verified": <bool>,
      "is_primary": <bool — exactly one true>
    }
  ],

  "rates": {
    "rate_per_post": <int dollars>,
    "rate_per_story": <int dollars>,
    "rate_per_reel": <int dollars>,
    "rate_per_video": <int dollars>
  },

  "audience_demographics": {
    "age_18_24": <float 0-1>,
    "age_25_34": <float 0-1>,
    "age_35_44": <float 0-1>,
    "age_45_plus": <float 0-1>,
    "gender_female": <float 0-1>,
    "gender_male": <float 0-1>,
    "top_countries": ["<code>", ...]
  },

  "portfolio_images": [
    {
      "caption": "<short descriptive caption>",
      "image_type": "<headshot|editorial|lifestyle|fitness|fashion|beauty|outdoor|studio|candid|commercial|portrait|action>",
      "setting": "<brief scene/background description>",
      "mood": "<one-word mood>"
    }
  ]
}

RULES:
- Generate exactly 12 portfolio image concepts with diverse types and settings.
- Generate 2-4 social accounts across different platforms.
- All monetary values in whole USD.
- Follower counts should be realistic for a mid-to-senior tier influencer (50K-2M).
- The appearance_prompt MUST be specific enough that every portfolio image could
  depict the same recognizable person.
- Make the profile feel lived-in and authentic — real-sounding handles, realistic
  engagement rates, a bio that sounds human.
"""


def _build_user_message(
    gender: str | None,
    age_range: str | None,
    niche: str | None,
    ethnicity: str | None,
    extra_instructions: str | None,
) -> str:
    """Build the user-facing generation prompt from optional preferences."""
    parts = ["Generate a complete influencer/model profile"]
    constraints = []
    if gender:
        constraints.append(f"Gender: {gender}")
    if age_range:
        constraints.append(f"Age range: {age_range}")
    if niche:
        constraints.append(f"Primary niche: {niche}")
    if ethnicity:
        constraints.append(f"Ethnicity: {ethnicity}")
    if extra_instructions:
        constraints.append(f"Additional direction: {extra_instructions}")

    if constraints:
        parts.append("with these preferences:\n- " + "\n- ".join(constraints))
    else:
        parts.append("with no specific constraints — surprise me.")

    return " ".join(parts)


def _seed_avatar_url(name: str, idx: int = 0) -> str:
    """Generate a deterministic placeholder portrait URL from a name + index."""
    seed = hashlib.md5(f"{name}-{idx}".encode()).hexdigest()[:10]
    # Use picsum with a face-like seed; the frontend shows these as model shots
    return f"https://picsum.photos/seed/{seed}/600/800"


async def generate_influencer_profile(
    gender: str | None = None,
    age_range: str | None = None,
    niche: str | None = None,
    ethnicity: str | None = None,
    extra_instructions: str | None = None,
) -> dict:
    """
    Calls Claude to generate a full influencer profile, then enriches
    portfolio images with deterministic placeholder URLs.

    Returns the parsed profile dict ready for DB insertion.
    """
    user_message = _build_user_message(gender, age_range, niche, ethnicity, extra_instructions)

    result = await ai_client.generate_json(SYSTEM_PROMPT, user_message, max_tokens=4096)
    profile = result["parsed"]

    # Stamp placeholder image URLs onto each portfolio concept
    full_name = f"{profile.get('first_name', 'Model')} {profile.get('last_name', 'X')}"
    for i, img in enumerate(profile.get("portfolio_images", [])):
        img["url"] = _seed_avatar_url(full_name, i)

    # Attach AI cost metadata
    profile["_ai_meta"] = {
        "model": result.get("model"),
        "input_tokens": result.get("input_tokens"),
        "output_tokens": result.get("output_tokens"),
    }

    return profile
