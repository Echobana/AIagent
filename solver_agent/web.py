"""FastAPI web app for interactive YAML generation."""

from pathlib import Path

import yaml
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from solver_agent.generator import generate_config, save_yaml
from solver_agent.providers import DEFAULT_MODEL, DEFAULT_PROVIDER

app = FastAPI(title="Solver YAML Agent")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return f"""
    <html><body style='font-family:Arial;max-width:980px;margin:40px auto;'>
      <form id='generator-form' method='post' action='/generate'>
        <label>Request:</label><br>
        <textarea id='request' name='request' rows='8' style='width:100%;'></textarea><br><br>

        <label>Provider:</label><br>
        <input list='providers' name='provider' value='{DEFAULT_PROVIDER}' style='width:360px'/>
        <datalist id='providers'>
          <option value='ollama'>Ollama (local)</option>
          <option value='openai'>OpenAI</option>
          <option value='anthropic'>Anthropic</option>
          <option value='perplexity'>Perplexity (OpenAI-compatible)</option>
          <option value='deepseek'>DeepSeek (OpenAI-compatible)</option>
          <option value='groq'>Groq (OpenAI-compatible)</option>
          <option value='openrouter'>OpenRouter (OpenAI-compatible)</option>
          <option value='together'>Together (OpenAI-compatible)</option>
          <option value='fireworks'>Fireworks (OpenAI-compatible)</option>
        </datalist><br><br>

        <label>Model:</label>
        <input type='text' name='model' value='{DEFAULT_MODEL}' style='width:360px'/><br><br>

        <details>
          <summary style='cursor:pointer'>Optional fields</summary>
          <div style='padding-top:10px'>
            <label>API key (for cloud providers):</label>
            <input type='password' name='api_key' style='width:480px' placeholder='api key'/><br><br>

            <label>Base URL (optional, required for unknown custom providers):</label>
            <input type='text' name='base_url' style='width:480px' placeholder='https://your-provider.example/v1'/><br><br>

            <label>Base YAML (optional):</label><br>
            <textarea name='base_yaml' rows='6' style='width:100%;'></textarea><br><br>
          </div>
        </details><br>

        <label>Output file name:</label>
        <input type='text' name='filename' value='generated_config.yaml'/><br><br>

        <button type='submit'>Generate</button>
      </form>
      <script>
        const form = document.getElementById('generator-form');
        const requestField = document.getElementById('request');

        form.addEventListener('submit', () => {{
          requestField.value = '';
        }});

        requestField.addEventListener('keydown', (event) => {{
          if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {{
            event.preventDefault();
            form.requestSubmit();
          }}
        }});
      </script>
    </body></html>
    """


@app.post("/generate", response_class=HTMLResponse)
def generate(
    request: str = Form(...),
    provider: str = Form(DEFAULT_PROVIDER),
    model: str = Form(DEFAULT_MODEL),
    api_key: str = Form(""),
    base_url: str = Form(""),
    base_yaml: str = Form(""),
    filename: str = Form("generated_config.yaml"),
) -> str:
    base_config = yaml.safe_load(base_yaml) if base_yaml.strip() else None

    try:
        config = generate_config(
            request,
            base_config,
            model=model,
            provider=provider,
            api_key=api_key or None,
            base_url=base_url or None,
        )
        out_path = save_yaml(config, Path(filename))
        rendered = yaml.safe_dump(config, sort_keys=False, allow_unicode=True)
        return f"<pre>{rendered}</pre><p>Saved to: {out_path}</p><p><a href='/'>Back</a></p>"
    except Exception as exc:  # noqa: BLE001
        return f"<p>Error: {exc}</p><p><a href='/'>Back</a></p>"
