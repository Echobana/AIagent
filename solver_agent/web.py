"""FastAPI web app for interactive YAML generation."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse

from solver_agent.generator import generate_config, parse_streamed_config, save_yaml
from solver_agent.providers import DEFAULT_MODEL, DEFAULT_PROVIDER

app = FastAPI(title="Solver YAML Agent")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset='utf-8'/>
      <title>Solver YAML Agent</title>
      <style>
        :root {{ color-scheme: dark; }}
        body {{ font-family: Inter, Arial, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }}
        .layout {{ max-width: 1100px; margin: 0 auto; padding: 24px; display: grid; grid-template-columns: 1fr 360px; gap: 16px; }}
        .panel {{ background: #111827; border: 1px solid #334155; border-radius: 14px; }}
        .chat {{ padding: 16px; min-height: 560px; display: flex; flex-direction: column; gap: 12px; }}
        .msg {{ padding: 12px; border-radius: 12px; white-space: pre-wrap; line-height: 1.45; }}
        .msg.user {{ align-self: flex-end; background: #1d4ed8; max-width: 85%; }}
        .msg.bot {{ align-self: flex-start; background: #1f2937; max-width: 95%; }}
        .typing {{ opacity: 0.75; font-size: 13px; }}
        .controls {{ padding: 16px; display: flex; flex-direction: column; gap: 10px; }}
        label {{ font-size: 13px; opacity: 0.8; }}
        input, textarea, button {{ border-radius: 10px; border: 1px solid #334155; background: #0b1220; color: #e2e8f0; padding: 10px; }}
        textarea {{ min-height: 110px; resize: vertical; }}
        button {{ background: #2563eb; border: none; cursor: pointer; font-weight: 600; }}
        button:disabled {{ opacity: 0.65; cursor: not-allowed; }}
        .composer {{ display:flex; gap:10px; }}
      </style>
    </head>
    <body>
      <div class='layout'>
        <div class='panel chat' id='chat'>
          <div class='msg bot'>Готово. Опишите задачу, и я сгенерирую YAML в real-time.</div>
        </div>
        <div class='panel controls'>
          <label>Provider</label>
          <input id='provider' value='{DEFAULT_PROVIDER}' />
          <label>Model</label>
          <input id='model' value='{DEFAULT_MODEL}' />
          <label>API key</label>
          <input id='api_key' type='password' placeholder='optional' />
          <label>Base URL</label>
          <input id='base_url' placeholder='https://provider.example/v1' />
          <label>Output file</label>
          <input id='filename' value='generated_config.yaml' />
          <label>Base YAML (optional)</label>
          <textarea id='base_yaml' placeholder='existing YAML'></textarea>
          <label>Request</label>
          <textarea id='request' placeholder='Сгенерируй конфиг...'></textarea>
          <div class='composer'>
            <button id='send'>Generate</button>
          </div>
          <div id='status' class='typing'></div>
        </div>
      </div>
      <script>
        const chat = document.getElementById('chat');
        const statusEl = document.getElementById('status');
        const sendBtn = document.getElementById('send');

        function addMessage(text, role) {{
          const div = document.createElement('div');
          div.className = `msg ${{role}}`;
          div.textContent = text;
          chat.appendChild(div);
          chat.scrollTop = chat.scrollHeight;
          return div;
        }}

        async function run() {{
          const request = document.getElementById('request').value.trim();
          if (!request) return;

          addMessage(request, 'user');
          const bot = addMessage('', 'bot');
          statusEl.textContent = 'Модель печатает...';
          sendBtn.disabled = true;

          const form = new FormData();
          ['provider','model','api_key','base_url','base_yaml','filename','request'].forEach((id) => {{
            form.append(id, document.getElementById(id).value);
          }});

          try {{
            const response = await fetch('/generate-stream', {{ method: 'POST', body: form }});
            if (!response.ok) {{
              bot.textContent = `Ошибка HTTP ${{response.status}}`;
              return;
            }}
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {{
              const {{ done, value }} = await reader.read();
              if (done) break;
              buffer += decoder.decode(value, {{ stream: true }});
              const lines = buffer.split('\n');
              buffer = lines.pop() || '';
              for (const line of lines) {{
                if (!line.trim()) continue;
                const event = JSON.parse(line);
                if (event.type === 'token') {{
                  bot.textContent += event.data;
                  chat.scrollTop = chat.scrollHeight;
                }} else if (event.type === 'done') {{
                  statusEl.textContent = `Готово. Сохранено в: ${{event.path}}`;
                }} else if (event.type === 'error') {{
                  statusEl.textContent = `Ошибка: ${{event.message}}`;
                }}
              }}
            }}
          }} catch (err) {{
            bot.textContent = `Ошибка сети: ${{err}}`;
          }} finally {{
            sendBtn.disabled = false;
            if (!statusEl.textContent) statusEl.textContent = 'Завершено';
          }}
        }}

        sendBtn.addEventListener('click', run);
      </script>
    </body>
    </html>
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


@app.post("/generate-stream")
def generate_stream(
    request: str = Form(...),
    provider: str = Form(DEFAULT_PROVIDER),
    model: str = Form(DEFAULT_MODEL),
    api_key: str = Form(""),
    base_url: str = Form(""),
    base_yaml: str = Form(""),
    filename: str = Form("generated_config.yaml"),
) -> StreamingResponse:
    base_config = yaml.safe_load(base_yaml) if base_yaml.strip() else None

    def event_stream():
        chunks: list[str] = []
        try:
            from solver_agent.generator import generate_config_stream

            for chunk in generate_config_stream(
                request,
                base_config,
                model=model,
                provider=provider,
                api_key=api_key or None,
                base_url=base_url or None,
            ):
                chunks.append(chunk)
                yield json.dumps({"type": "token", "data": chunk}, ensure_ascii=False) + "\n"

            config = parse_streamed_config(chunks)
            out_path = save_yaml(config, Path(filename))
            rendered = yaml.safe_dump(config, sort_keys=False, allow_unicode=True)
            yield json.dumps({"type": "done", "path": str(out_path), "yaml": rendered}, ensure_ascii=False) + "\n"
        except Exception as exc:  # noqa: BLE001
            yield json.dumps({"type": "error", "message": str(exc)}, ensure_ascii=False) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")
