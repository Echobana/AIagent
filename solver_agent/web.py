"""FastAPI web app for interactive YAML generation."""

from pathlib import Path

import yaml
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from solver_agent.generator import generate_config, save_yaml
from solver_agent.ollama_client import DEFAULT_MODEL

app = FastAPI(title="Solver YAML Agent")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
    <html><body style='font-family:Arial;max-width:900px;margin:40px auto;'>
      <h2>Solver YAML Agent</h2>
      <form method='post' action='/generate'>
        <label>Request:</label><br>
        <textarea name='request' rows='8' style='width:100%;'></textarea><br><br>
        <label>Base YAML (optional):</label><br>
        <textarea name='base_yaml' rows='12' style='width:100%;'></textarea><br><br>
        <label>Output file name:</label>
        <input type='text' name='filename' value='generated_config.yaml'/><br><br>
        <label>Ollama model:</label>
        <input type='text' name='model' value='gpt-oss:20b'/><br><br>
        <button type='submit'>Generate</button>
      </form>
    </body></html>
    """


@app.post("/generate", response_class=HTMLResponse)
def generate(
    request: str = Form(...),
    base_yaml: str = Form(""),
    filename: str = Form("generated_config.yaml"),
    model: str = Form(DEFAULT_MODEL),
) -> str:
    base_config = yaml.safe_load(base_yaml) if base_yaml.strip() else None

    try:
        config = generate_config(request, base_config, model)
        out_path = save_yaml(config, Path(filename))
        rendered = yaml.safe_dump(config, sort_keys=False, allow_unicode=True)
        return f"<pre>{rendered}</pre><p>Saved to: {out_path}</p><p><a href='/'>Back</a></p>"
    except Exception as exc:  # noqa: BLE001
        return f"<p>Error: {exc}</p><p><a href='/'>Back</a></p>"
