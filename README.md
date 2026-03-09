# Solver YAML Agent

Python AI agent that generates solver YAML configuration files from natural language requests.

## Features
- Connects to local Ollama (`http://localhost:11434`)
- Default model: `gpt-oss:20b`
- CLI via `argparse`
- Web GUI via FastAPI
- YAML schema validation (core required fields)
- Supports partial updates by providing a base YAML config
- Saves generated output to `.yaml`
- Modular code split across package files for easier maintenance

## Project structure
- `solver_yaml_agent.py` - executable entrypoint
- `solver_agent/cli.py` - command-line workflow
- `solver_agent/web.py` - FastAPI routes/UI
- `solver_agent/generator.py` - prompt/generation/validation/save logic
- `solver_agent/ollama_client.py` - requests-based Ollama client
- `solver_agent/schema.py` - Pydantic validation schema
- `solver_agent/examples.py` - prompt examples

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## CLI usage
```bash
python solver_yaml_agent.py \
  --prompt "Провести расчет..." \
  --output case.yaml
```

Use an existing file as a base and change only requested parameters:
```bash
python solver_yaml_agent.py \
  --prompt "Измени скорость на входе на 5 м/с" \
  --base-file case.yaml \
  --output case_updated.yaml
```

Override model if needed:
```bash
python solver_yaml_agent.py --prompt "..." --model qwen2.5:14b
```

If the request is ambiguous, the agent returns:
```
CLARIFICATION: ...
```

## Web UI
```bash
python solver_yaml_agent.py --serve --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000`.

## Notes
- Ollama must be running locally.
- Ensure model `gpt-oss:20b` is pulled in your Ollama instance.
