"""FastAPI web app for interactive YAML generation."""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import yaml
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse

from solver_agent.generator import generate_config, save_yaml
from solver_agent.providers import DEFAULT_MODEL, DEFAULT_PROVIDER

app = FastAPI(title="YAML Generator")
GENERATED_RESULTS: dict[str, dict[str, str]] = {}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return f"""
    <html><body style='font-family:Arial;max-width:980px;margin:40px auto;'>
      <form id='generator-form' method='post' action='/generate'>
        <label>Request:</label><br>
        <textarea id='request' name='request' rows='8' style='width:100%;'></textarea><br>
        <small style='color:#666'>Запуск генерации: Ctrl/Cmd + Enter</small><br><br>

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
          <summary style='cursor:pointer;'>Опциональные поля</summary>
          <div style='margin-top:12px;'>
            <label>API key (for cloud providers):</label>
            <input type='password' name='api_key' style='width:480px' placeholder='api key'/><br><br>

            <label>Base URL (optional, required for unknown custom providers):</label>
            <input type='text' name='base_url' style='width:480px' placeholder='https://your-provider.example/v1'/><br><br>

            <label>Base YAML (optional):</label><br>
            <textarea name='base_yaml' rows='6' style='width:100%;'></textarea><br><br>

            <label>Output file name:</label>
            <input type='text' name='filename' value='generated_config.yaml'/><br><br>
          </div>
        </details>
      </form>
      <p id='status' style='margin-top:16px;color:#444;'></p>
      <div id='result' style='margin-top:8px;'></div>
      <script>
        const form = document.getElementById('generator-form');
        const requestField = document.getElementById('request');
        const status = document.getElementById('status');
        const result = document.getElementById('result');

        async function startGeneration() {{
          const formData = new FormData(form);
          if (!formData.get('request')?.toString().trim()) {{
            status.textContent = 'Введите request для запуска генерации.';
            return;
          }}

          status.textContent = '⏳ Генерация запущена...';
          result.innerHTML = '';
          requestField.value = '';

          try {{
            const response = await fetch('/generate', {{
              method: 'POST',
              body: formData,
            }});
            const payload = await response.json();

            if (!response.ok || !payload.ok) {{
              status.textContent = `❌ Ошибка: ${{payload.error || 'Неизвестная ошибка'}}`;
              return;
            }}

            status.textContent = '✅ Задача выполнена.';
            result.innerHTML = `<p>Файл сохранён: <code>${{payload.saved_to}}</code></p>
                                <p><a href="/result/${{payload.result_id}}" target="_blank" rel="noopener noreferrer">Открыть YAML (опционально)</a></p>`;
          }} catch (error) {{
            status.textContent = `❌ Ошибка сети: ${{error}}`;
          }}
        }}

        requestField.addEventListener('keydown', (event) => {{
          if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {{
            event.preventDefault();
            startGeneration();
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
) -> JSONResponse:
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
        result_id = str(uuid4())
        GENERATED_RESULTS[result_id] = {
            "rendered": rendered,
            "saved_to": str(out_path),
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        return JSONResponse(
            {
                "ok": True,
                "saved_to": str(out_path),
                "result_id": result_id,
            }
        )
    except Exception as exc:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


@app.get("/result/{result_id}", response_class=HTMLResponse)
def result(result_id: str) -> str:
    payload = GENERATED_RESULTS.get(result_id)
    if payload is None:
        return "<p>Result not found or expired.</p><p><a href='/'>Back</a></p>"
    return (
        f"<p>Generated at: {payload['created_at']}</p>"
        f"<pre>{payload['rendered']}</pre>"
        f"<p>Saved to: {payload['saved_to']}</p>"
        "<p><a href='/'>Back</a></p>"
    )
