"""Generation and validation pipeline for solver YAML."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import ValidationError

from solver_agent.examples import EXAMPLE_1, EXAMPLE_2
from solver_agent.ollama_client import query_ollama
from solver_agent.schema import SolverConfig


def build_prompt(user_request: str, base_config: Optional[Dict[str, Any]]) -> str:
    base_text = yaml.safe_dump(base_config, sort_keys=False, allow_unicode=True) if base_config else ""
    return f"""
You generate ONLY valid YAML for an LBM solver config.
If request misses critical parameters, return exactly one line:
CLARIFICATION: <question in Russian or English>

Schema expectations are based on these examples:
---EXAMPLE1---
{EXAMPLE_1}
---EXAMPLE2---
{EXAMPLE_2}

If BASE_CONFIG is provided, modify only requested parameters and keep the rest unchanged.

BASE_CONFIG:
{base_text or 'NONE'}

USER_REQUEST:
{user_request}

Output format:
- Either CLARIFICATION: ...
- Or pure YAML without markdown fences.
""".strip()


def extract_yaml(text: str) -> str:
    if text.strip().startswith("CLARIFICATION:"):
        return text.strip()
    fenced = re.findall(r"```(?:yaml)?\n(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced[0].strip()
    return text.strip()


def generate_config(user_request: str, base_config: Optional[Dict[str, Any]], model: str) -> Dict[str, Any]:
    prompt = build_prompt(user_request, base_config)
    raw = query_ollama(prompt, model=model)
    text = extract_yaml(raw)

    if text.startswith("CLARIFICATION:"):
        raise ValueError(text)

    parsed = yaml.safe_load(text)
    if not isinstance(parsed, dict):
        raise ValueError("Model did not return a YAML object.")

    try:
        SolverConfig.model_validate(parsed)
    except ValidationError as exc:
        raise ValueError(f"Generated YAML failed schema validation:\n{exc}") from exc

    return parsed


def save_yaml(config: Dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() not in {".yaml", ".yml"}:
        output_path = output_path.with_suffix(".yaml")
    output_path.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return output_path
