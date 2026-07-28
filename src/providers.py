"""
Multi-provider adapter with safe fallback to offline mock mode.
"""

from __future__ import annotations

import os
import sys

import requests
from dotenv import load_dotenv

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()


def _has_real_api_key(value: str | None) -> bool:
    if not value:
        return False
    normalized = value.strip().lower()
    return normalized not in {
        "",
        "your_gemini_api_key_here",
        "your_openai_api_key_here",
        "your_anthropic_api_key_here",
        "your_openrouter_api_key_here",
    }


class BaseLLMProvider:
    """Base interface for all providers."""

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not _has_real_api_key(self.api_key):
            return "[Gemini Error]: Chua cau hinh GEMINI_API_KEY trong file .env."
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents,
            )
            return response.text
        except Exception as exc:
            return f"[Gemini Exception]: {exc}"


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not _has_real_api_key(self.api_key):
            return "[OpenAI Error]: Chua cau hinh OPENAI_API_KEY trong file .env."
        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as exc:
            return f"[OpenAI Exception]: {exc}"


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not _has_real_api_key(self.api_key):
            return "[Anthropic Error]: Chua cau hinh ANTHROPIC_API_KEY trong file .env."
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                kwargs["system"] = system_prompt
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as exc:
            return f"[Anthropic Exception]: {exc}"


class OpenRouterProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not _has_real_api_key(self.api_key):
            return "[OpenRouter Error]: Chua cau hinh OPENROUTER_API_KEY trong file .env."
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            payload = {
                "model": self.model_name,
                "messages": messages,
            }
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            if response.status_code != 200:
                return f"[OpenRouter API Error {response.status_code}]: {response.text}"
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            return f"[OpenRouter Exception]: {exc}"


class MockProvider(BaseLLMProvider):
    """Offline provider for local demo and lab fallback."""

    model_name = "mock-offline"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        text = prompt.lower()
        if any(keyword in text for keyword in ["dau bung", "đau bụng", "da day", "dạ dày"]):
            return (
                "Ban co the can kham chuyen khoa Tieu hoa dua tren mo ta hien tai. "
                "Toi chua the tu kiem tra lich bac si neu khong dung cong cu."
            )
        if any(keyword in text for keyword in ["kho tho", "khó thở", "dau nguc", "đau ngực"]):
            return (
                "Trieu chung co dau hieu nguy hiem. Ban nen den cap cuu ngay "
                "thay vi cho lich kham thong thuong."
            )
        return "Mock response: toi chi dang mo phong baseline chatbot offline."


def get_llm_provider(provider_name: str | None = None) -> BaseLLMProvider:
    """Select a provider from env and fall back to mock mode if needed."""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()

    if name == "gemini":
        provider = GeminiProvider()
        return provider if _has_real_api_key(provider.api_key) else MockProvider()
    if name == "openai":
        provider = OpenAIProvider()
        return provider if _has_real_api_key(provider.api_key) else MockProvider()
    if name == "anthropic":
        provider = AnthropicProvider()
        return provider if _has_real_api_key(provider.api_key) else MockProvider()
    if name == "openrouter":
        provider = OpenRouterProvider()
        return provider if _has_real_api_key(provider.api_key) else MockProvider()
    return MockProvider()


if __name__ == "__main__":
    provider = get_llm_provider()
    print(f"Provider: {provider.__class__.__name__}")
    print(provider.generate("Toi bi dau bung va muon dat lich kham ngay mai."))
