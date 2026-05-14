"""Per-model API clients with a unified interface.

Every advisor implements `ask(system, user) -> str`. Missing API keys
make the advisor `available = False`; the orchestrator skips it.

Supported providers:
  - Anthropic Claude
  - OpenAI GPT
  - Google Gemini (via OpenAI-compatible endpoint)
  - xAI Grok (OpenAI-compatible)
  - DeepSeek (OpenAI-compatible)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

import anthropic
from openai import OpenAI


class Advisor(Protocol):
    name: str
    model_id: str
    available: bool

    def ask(self, system: str, user: str, *, max_tokens: int = 2000) -> str: ...


@dataclass
class AnthropicAdvisor:
    name: str = "Claude"
    model_id: str = os.environ.get("COUNCIL_CLAUDE_MODEL", "claude-opus-4-7")

    @property
    def available(self) -> bool:
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    def ask(self, system: str, user: str, *, max_tokens: int = 2000) -> str:
        client = anthropic.Anthropic()
        chunks: list[str] = []
        with client.messages.stream(
            model=self.model_id,
            max_tokens=max_tokens,
            thinking={"type": "adaptive"},
            system=system,
            messages=[{"role": "user", "content": user}],
        ) as stream:
            for event in stream:
                if (
                    event.type == "content_block_delta"
                    and event.delta.type == "text_delta"
                ):
                    chunks.append(event.delta.text)
            stream.get_final_message()
        return "".join(chunks).strip()


@dataclass
class OpenAICompatibleAdvisor:
    """Catch-all for OpenAI-compatible providers."""

    name: str
    model_id: str
    api_key_env: str
    base_url: str | None = None

    @property
    def available(self) -> bool:
        return bool(os.environ.get(self.api_key_env))

    def _client(self) -> OpenAI:
        return OpenAI(
            api_key=os.environ[self.api_key_env],
            base_url=self.base_url,
        )

    def ask(self, system: str, user: str, *, max_tokens: int = 2000) -> str:
        resp = self._client().chat.completions.create(
            model=self.model_id,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        text = resp.choices[0].message.content or ""
        return text.strip()


def default_panel() -> list[Advisor]:
    """Return the standard 5-advisor panel, filtered to those whose API keys are set."""
    panel: list[Advisor] = [
        AnthropicAdvisor(),
        OpenAICompatibleAdvisor(
            name="GPT",
            model_id=os.environ.get("COUNCIL_OPENAI_MODEL", "gpt-5"),
            api_key_env="OPENAI_API_KEY",
        ),
        OpenAICompatibleAdvisor(
            name="Gemini",
            model_id=os.environ.get("COUNCIL_GEMINI_MODEL", "gemini-2.5-pro"),
            api_key_env="GOOGLE_API_KEY",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        ),
        OpenAICompatibleAdvisor(
            name="Grok",
            model_id=os.environ.get("COUNCIL_XAI_MODEL", "grok-4"),
            api_key_env="XAI_API_KEY",
            base_url="https://api.x.ai/v1",
        ),
        OpenAICompatibleAdvisor(
            name="DeepSeek",
            model_id=os.environ.get("COUNCIL_DEEPSEEK_MODEL", "deepseek-chat"),
            api_key_env="DEEPSEEK_API_KEY",
            base_url="https://api.deepseek.com/v1",
        ),
    ]
    return [a for a in panel if a.available]


def solo_claude_panel() -> list[Advisor]:
    """Fallback: 5 Claude instances, one per persona — used when only ANTHROPIC_API_KEY is set."""
    return [
        AnthropicAdvisor(name=f"Claude-{i + 1}") for i in range(5)
    ]
