"""Google Gemini LLM client."""
import json
import logging
from typing import Any, Dict, List

import google.generativeai as genai

from app.config import settings
from app.external.llm.base_client import BaseLLMClient, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)

# Cost per 1M tokens (USD) for gemini-2.0-flash
COST_PER_1M_INPUT = 0.075
COST_PER_1M_OUTPUT = 0.30


class GeminiClient(BaseLLMClient):
    """Google Gemini LLM client."""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL

    def _build_gemini_messages(self, messages: List[LLMMessage]) -> tuple[str, list]:
        """Extract system prompt and convert messages to Gemini format."""
        system_prompt = ""
        history = []
        user_message = ""

        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            elif msg.role == "user":
                user_message = msg.content
                if history:
                    history.append({"role": "user", "parts": [msg.content]})
            elif msg.role == "assistant":
                history.append({"role": "model", "parts": [msg.content]})

        return system_prompt, history, user_message

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        json_mode: bool = False,
    ) -> LLMResponse:
        try:
            system_prompt, history, user_message = self._build_gemini_messages(messages)

            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json" if json_mode else "text/plain",
            )

            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt if system_prompt else None,
                generation_config=generation_config,
            )

            chat = model.start_chat(history=history)
            response = await chat.send_message_async(user_message)

            # Calculate tokens and cost
            prompt_tokens = response.usage_metadata.prompt_token_count or 0
            completion_tokens = response.usage_metadata.candidates_token_count or 0
            total_tokens = prompt_tokens + completion_tokens
            cost = (prompt_tokens / 1_000_000 * COST_PER_1M_INPUT) + (
                completion_tokens / 1_000_000 * COST_PER_1M_OUTPUT
            )

            return LLMResponse(
                content=response.text,
                model=self.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost,
                raw_response=response,
            )

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def generate_structured(
        self,
        messages: List[LLMMessage],
        response_schema: Dict[str, Any],
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        # Add JSON instruction to last user message
        json_instruction = f"\n\nRespond with valid JSON matching this schema: {json.dumps(response_schema)}"
        new_messages = messages.copy()
        if new_messages and new_messages[-1].role == "user":
            new_messages[-1] = LLMMessage(
                role="user",
                content=new_messages[-1].content + json_instruction,
            )

        response = await self.generate(new_messages, temperature=temperature, json_mode=True)
        try:
            # Strip markdown code blocks if present
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini: {e}\nContent: {response.content}")
            return {"error": "Failed to parse structured response", "raw": response.content}


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for development when no API key is available."""

    async def generate(self, messages, temperature=0.7, max_tokens=2048, json_mode=False):
        return LLMResponse(
            content="This is a mock LLM response for development. Configure GEMINI_API_KEY to enable real AI.",
            model="mock",
            prompt_tokens=50,
            completion_tokens=20,
            total_tokens=70,
            cost_usd=0.0,
        )

    async def generate_structured(self, messages, response_schema, temperature=0.3):
        return {
            "selected_question": {
                "id": "mock-q-1",
                "content": "Design a URL shortener (mock question)",
                "difficulty": "medium",
            },
            "technical_accuracy": 75,
            "completeness": 70,
            "communication_quality": 80,
            "problem_solving_approach": 72,
            "confidence_level": 75,
            "overall_score": 74,
            "feedback_summary": "Mock evaluation - configure GEMINI_API_KEY for real feedback.",
            "strengths": ["Good structure"],
            "improvements": ["Add more detail"],
            "gaps_identified": [],
        }


def get_llm_client() -> BaseLLMClient:
    """Factory function returning the appropriate LLM client."""
    if settings.GEMINI_API_KEY:
        return GeminiClient()
    logger.warning("No GEMINI_API_KEY found, using MockLLMClient")
    return MockLLMClient()
