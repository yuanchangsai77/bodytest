import asyncio
import os
import sys
from typing import Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from llmapiconfig.llm_client import chat
from llmapiconfig.settings import settings


class MultiModelAPIClient:
    """Simple wrapper that delegates chat requests to configured LLM provider."""

    def __init__(self, provider: Optional[str] = None) -> None:
        self.provider = provider

    def call_api(self, system_prompt: str, user_instruction: str) -> str:
        """Send messages to the LLM and return the text response.

        Parameters
        ----------
        system_prompt: str
            The system level instruction.
        user_instruction: str
            The user message.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_instruction},
        ]
        response = asyncio.run(chat(messages, provider=self.provider))
        actual_provider = self.provider or settings.default_provider
        if actual_provider in ["openai", "zhipu"]:
            return response["choices"][0]["message"]["content"]
        if actual_provider == "claude":
            return response["content"][0]["text"]
        if actual_provider == "qwen":
            return response["output"]["choices"][0]["message"]["content"]
        if actual_provider == "gemini":
            return response["candidates"][0]["content"]["parts"][0]["text"]
        raise ValueError(f"不支持的提供商: {actual_provider}")
