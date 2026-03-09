"""CLI entrypoint for solver YAML generation."""

import argparse
from pathlib import Path


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Generate solver YAML via Ollama.")
    parser.add_argument("--prompt", help="Natural language request for configuration generation")
    parser.add_argument("--output", default="generated_config.yaml", help="Output .yaml path")
    parser.add_argument("--base-file", help="Existing YAML file to update")
    parser.add_argument("--model", default="gpt-oss:20b", help="Ollama model name")
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

    try:
        config = generate_config(args.prompt, base_config, args.model)
    except ValueError as exc:
        if str(exc).startswith("CLARIFICATION:"):
            print(str(exc))
            return
        raise

    out_path = save_yaml(config, Path(args.output))
    print(f"YAML saved to {out_path}")
