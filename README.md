# Solver YAML Agent

Python AI agent that generates solver YAML configuration files from natural language requests.

## Features
- Supports multiple LLM providers:
  - Local Ollama (`http://localhost:11434`)
  - Anthropic Claude API
  - Any OpenAI-compatible API (including OpenAI, Perplexity, DeepSeek, Groq, OpenRouter, Together, Fireworks, and custom endpoints)
- CLI via `argparse`
- Simple web GUI via FastAPI (for minimizing CLI usage)
- YAML schema validation (core required fields)
- Supports partial updates by providing a base YAML config
- Saves generated output to `.yaml`
- Modular code split across package files for easier maintenance

## Project structure
- `solver_yaml_agent.py` - executable entrypoint
- `solver_agent/cli.py` - command-line workflow
- `solver_agent/web.py` - FastAPI routes/UI
- `solver_agent/generator.py` - prompt/generation/validation/save logic
- `solver_agent/providers.py` - API clients and provider routing
- `solver_agent/schema.py` - Pydantic validation schema
- `solver_agent/examples.py` - prompt examples

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## CLI usage
### Local Ollama
```bash
python solver_yaml_agent.py \
  --prompt "Провести расчет..." \
  --provider ollama \
  --model gpt-oss:20b \
  --output case.yaml
```

### Any OpenAI-compatible provider (preset names)
```bash
export PERPLEXITY_API_KEY="..."
python solver_yaml_agent.py \
  --prompt "Сгенерируй YAML для расчета" \
  --provider perplexity \
  --model sonar \
  --output case_perplexity.yaml
```

```bash
export DEEPSEEK_API_KEY="..."
python solver_yaml_agent.py \
  --prompt "Сгенерируй YAML с inlet velocity 5 м/с" \
  --provider deepseek \
  --model deepseek-chat \
  --output case_deepseek.yaml
```

### Custom OpenAI-compatible provider (truly any)
```bash
export LLM_API_KEY="..."
python solver_yaml_agent.py \
  --prompt "Сгенерируй базовую конфигурацию" \
  --provider my-provider \
  --base-url https://my-provider.example/v1 \
  --model my-model \
  --output case_custom.yaml
```

### Anthropic (Claude API)
```bash
export ANTHROPIC_API_KEY="..."
python solver_yaml_agent.py \
  --prompt "Сгенерируй YAML" \
  --provider anthropic \
  --model claude-3-5-sonnet-latest \
  --output case_claude.yaml
```

Use an existing file as a base and change only requested parameters:
```bash
python solver_yaml_agent.py \
  --prompt "Измени скорость на входе на 5 м/с" \
  --base-file case.yaml \
  --output case_updated.yaml
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

In GUI you can enter any provider name, choose a known one from suggestions, set model/API key/base URL, and generate YAML without CLI arguments.

## Notes
- For Ollama, make sure local service is running and model is pulled.
- API key lookup order: explicit `--api-key`/GUI field, then `<PROVIDER>_API_KEY`, then `LLM_API_KEY`.
- Unknown provider names are treated as OpenAI-compatible and require `base_url`.
