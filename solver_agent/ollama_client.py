"""Ollama HTTP client."""

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gpt-oss:20b"


def query_ollama(prompt: str, model: str = DEFAULT_MODEL, ollama_url: str = OLLAMA_URL) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(ollama_url, json=payload, timeout=180)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()
