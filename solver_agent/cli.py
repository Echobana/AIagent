"""CLI entrypoint for solver YAML generation."""

import argparse
import os
from pathlib import Path


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Generate solver YAML via Ollama, Anthropic, and any OpenAI-compatible API.")
    parser.add_argument("--prompt", help="Natural language request for configuration generation")
    parser.add_argument("--output", default="generated_config.yaml", help="Output .yaml path")
    parser.add_argument("--base-file", help="Existing YAML file to update")
    parser.add_argument("--provider", default="ollama", help="Provider name: ollama, anthropic, openai, perplexity, deepseek, or custom")
    parser.add_argument("--model", default="gpt-oss:20b", help="Model name for selected provider")
    parser.add_argument("--api-key", help="API key for cloud providers (or via <PROVIDER>_API_KEY / LLM_API_KEY)")
    parser.add_argument("--base-url", help="API base URL (required for unknown/custom provider names)")
    parser.add_argument("--serve", action="store_true", help="Run FastAPI web app")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.serve:
        import uvicorn

        from solver_agent.web import app

        uvicorn.run(app, host=args.host, port=args.port)
        return

    if not args.prompt:
        parser.error("--prompt is required unless --serve is used")

    import yaml

    from solver_agent.generator import generate_config, save_yaml

    base_config = None
    if args.base_file:
        base_config = yaml.safe_load(Path(args.base_file).read_text(encoding="utf-8"))

    provider_name = args.provider.lower().strip()
    env_key = (
        os.getenv(f"{provider_name.upper()}_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
        or os.getenv("LLM_API_KEY")
    )

    try:
        config = generate_config(
            args.prompt,
            base_config,
            model=args.model,
            provider=args.provider,
            api_key=args.api_key or env_key,
            base_url=args.base_url,
        )
    except ValueError as exc:
        if str(exc).startswith("CLARIFICATION:"):
            print(str(exc))
            return
        raise

    out_path = save_yaml(config, Path(args.output))
    print(f"YAML saved to {out_path}")
