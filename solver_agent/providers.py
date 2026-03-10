"""LLM provider clients for local and cloud models."""

from __future__ import annotations

import os
from typing import Optional

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_PROVIDER = "ollama"
DEFAULT_MODEL = "gpt-oss:20b"

OPENAI_COMPAT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "perplexity": "https://api.perplexity.ai",
    "deepseek": "https://api.deepseek.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "together": "https://api.together.xyz/v1",
    "fireworks": "https://api.fireworks.ai/inference/v1",
}


def get_api_key_for_provider(provider: str) -> Optional[str]:
    provider_name = provider.lower().strip()
    specific_key = os.getenv(f"{provider_name.upper()}_API_KEY")
    if specific_key:
        return specific_key
    return os.getenv("LLM_API_KEY")


def query_ollama(prompt: str, model: str = DEFAULT_MODEL, base_url: str = OLLAMA_URL) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(base_url, json=payload, timeout=180)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()


def query_openai_compatible(prompt: str, model: str, api_key: str, base_url: str) -> str:
    if not api_key:
        raise ValueError("API key is required for OpenAI-compatible providers")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, headers=headers, timeout=180)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def query_anthropic(prompt: str, model: str, api_key: str, base_url: str = "https://api.anthropic.com") -> str:
    if not api_key:
        raise ValueError("Anthropic API key is required for provider=anthropic")

    payload = {
        "model": model,
        "max_tokens": 2048,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    response = requests.post(f"{base_url.rstrip('/')}/v1/messages", json=payload, headers=headers, timeout=600)
    response.raise_for_status()
    data = response.json()
    content = data.get("content", [])
    text_blocks = [block.get("text", "") for block in content if block.get("type") == "text"]
    return "\n".join(part for part in text_blocks if part).strip()


def query_model(
    prompt: str,
    provider: str = DEFAULT_PROVIDER,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> str:
    provider_name = provider.lower().strip()

    if provider_name == "ollama":
        return query_ollama(prompt, model=model, base_url=base_url or OLLAMA_URL)

    if provider_name == "anthropic":
        return query_anthropic(
            prompt,
            model=model,
            api_key=api_key or get_api_key_for_provider("anthropic") or "",
            base_url=base_url or "https://api.anthropic.com",
        )

    resolved_base_url = base_url or OPENAI_COMPAT_BASE_URLS.get(provider_name)
    if not resolved_base_url:
        raise ValueError(
            "Unknown provider. For any OpenAI-compatible API, pass --provider <name> and --base-url <url>, "
            "or use known presets: openai, perplexity, deepseek, groq, openrouter, together, fireworks."
        )

    return query_openai_compatible(
        prompt,
        model=model,
        api_key=api_key or get_api_key_for_provider(provider_name) or "",
        base_url=resolved_base_url,
    )
