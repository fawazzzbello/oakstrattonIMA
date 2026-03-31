import json
import anthropic
from app.core.config import settings


class AIClient:
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            self._client = None
        else:
            self._client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    @property
    def is_available(self) -> bool:
        return self._client is not None

    async def generate(self, system_prompt: str, user_message: str, max_tokens: int = None) -> dict:
        if not self.is_available:
            raise ValueError("AI service not configured. Set ANTHROPIC_API_KEY.")
        response = await self._client.messages.create(
            model=settings.AI_MODEL,
            max_tokens=max_tokens or settings.AI_MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return {
            "content": response.content[0].text,
            "model": response.model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

    async def generate_json(self, system_prompt: str, user_message: str, max_tokens: int = None) -> dict:
        """Generate and parse JSON response."""
        result = await self.generate(system_prompt, user_message, max_tokens)
        try:
            parsed = json.loads(result["content"])
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            text = result["content"]
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                parsed = json.loads(text[start:end])
            else:
                start = text.find("[")
                end = text.rfind("]") + 1
                if start != -1 and end > start:
                    parsed = json.loads(text[start:end])
                else:
                    parsed = {"raw_response": text}
        result["parsed"] = parsed
        return result


ai_client = AIClient()
