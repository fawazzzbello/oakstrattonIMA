"""
Multi-provider AI client.
Supports Claude (Anthropic), Gemini (Google), and OpenAI (optional).
Active provider + model can be changed at runtime via configure().
"""
import json
from app.core.config import settings

# Catalogue of supported providers and their available models
PROVIDER_CATALOGUE = {
    "claude": {
        "name": "Claude (Anthropic)",
        "models": [
            "claude-opus-4-6",
            "claude-sonnet-4-6",
            "claude-haiku-4-5-20251001",
        ],
        "default_model": "claude-sonnet-4-6",
    },
    "gemini": {
        "name": "Gemini (Google)",
        "models": [
            "gemini-2.5-pro-preview-05-06",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ],
        "default_model": "gemini-2.0-flash",
    },
    "openai": {
        "name": "GPT (OpenAI)",
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
        ],
        "default_model": "gpt-4o",
    },
}


class MultiAIClient:
    def __init__(self):
        # ── Claude ──────────────────────────────────────────────────────
        self._claude = None
        if settings.ANTHROPIC_API_KEY:
            import anthropic
            self._claude = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

        # ── Gemini ──────────────────────────────────────────────────────
        self._gemini_ready = False
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._gemini_ready = True
            except ImportError:
                pass  # package not installed

        # ── OpenAI ──────────────────────────────────────────────────────
        self._openai = None
        if settings.OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                self._openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                pass  # package not installed

        # Active provider/model — may be overridden at runtime
        self._active_provider: str = settings.AI_PROVIDER
        self._active_model: str = settings.AI_MODEL

    # ── Runtime configuration ────────────────────────────────────────────

    def configure(self, provider: str, model: str) -> None:
        """Update active provider and model (called by admin on settings change)."""
        if provider not in PROVIDER_CATALOGUE:
            raise ValueError(f"Unknown provider '{provider}'. Valid: {list(PROVIDER_CATALOGUE)}")
        self._active_provider = provider
        self._active_model = model

    @property
    def active_provider(self) -> str:
        return self._active_provider

    @property
    def active_model(self) -> str:
        return self._active_model

    @property
    def is_available(self) -> bool:
        return self._is_provider_ready(self._active_provider)

    def _is_provider_ready(self, provider: str) -> bool:
        if provider == "claude":
            return self._claude is not None
        if provider == "gemini":
            return self._gemini_ready
        if provider == "openai":
            return self._openai is not None
        return False

    def get_provider_status(self) -> dict:
        """Returns availability and model list for all providers."""
        return {
            pid: {
                "name": info["name"],
                "is_configured": self._is_provider_ready(pid),
                "models": info["models"],
                "default_model": info["default_model"],
            }
            for pid, info in PROVIDER_CATALOGUE.items()
        }

    # ── Generation ───────────────────────────────────────────────────────

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = None,
        provider: str = None,
        model: str = None,
    ) -> dict:
        p = provider or self._active_provider
        m = model or self._active_model

        if p == "claude":
            return await self._gen_claude(system_prompt, user_message, m, max_tokens)
        if p == "gemini":
            return await self._gen_gemini(system_prompt, user_message, m, max_tokens)
        if p == "openai":
            return await self._gen_openai(system_prompt, user_message, m, max_tokens)
        raise ValueError(f"Unknown provider: {p}")

    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = None,
        provider: str = None,
        model: str = None,
    ) -> dict:
        """Generate and auto-parse a JSON response."""
        result = await self.generate(system_prompt, user_message, max_tokens, provider=provider, model=model)
        text = result["content"]
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            # Try to extract the first JSON object or array
            for open_ch, close_ch in [("{", "}"), ("[", "]")]:
                start = text.find(open_ch)
                end = text.rfind(close_ch) + 1
                if start != -1 and end > start:
                    try:
                        parsed = json.loads(text[start:end])
                        break
                    except json.JSONDecodeError:
                        pass
            else:
                parsed = {"raw_response": text}
        result["parsed"] = parsed
        return result

    # ── Provider implementations ─────────────────────────────────────────

    async def _gen_claude(self, system: str, user: str, model: str, max_tokens: int = None) -> dict:
        if not self._claude:
            raise ValueError("Claude not configured. Set ANTHROPIC_API_KEY.")
        response = await self._claude.messages.create(
            model=model,
            max_tokens=max_tokens or settings.AI_MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return {
            "content": response.content[0].text,
            "model": response.model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

    async def _gen_gemini(self, system: str, user: str, model: str, max_tokens: int = None) -> dict:
        if not self._gemini_ready:
            raise ValueError("Gemini not configured. Set GEMINI_API_KEY.")
        import google.generativeai as genai
        from google.generativeai.types import GenerationConfig
        gen_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system,
        )
        config = GenerationConfig(max_output_tokens=max_tokens or settings.AI_MAX_TOKENS)
        response = await gen_model.generate_content_async(user, generation_config=config)
        usage = response.usage_metadata
        return {
            "content": response.text,
            "model": model,
            "input_tokens": getattr(usage, "prompt_token_count", 0),
            "output_tokens": getattr(usage, "candidates_token_count", 0),
        }

    async def _gen_openai(self, system: str, user: str, model: str, max_tokens: int = None) -> dict:
        if not self._openai:
            raise ValueError("OpenAI not configured. Set OPENAI_API_KEY.")
        response = await self._openai.chat.completions.create(
            model=model,
            max_tokens=max_tokens or settings.AI_MAX_TOKENS,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        usage = response.usage
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "input_tokens": usage.prompt_tokens if usage else 0,
            "output_tokens": usage.completion_tokens if usage else 0,
        }


ai_client = MultiAIClient()
