"""FastAPI web app for interactive YAML generation."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse

from solver_agent.generator import generate_config, generate_config_stream, parse_streamed_config, save_yaml
from solver_agent.providers import DEFAULT_MODEL, DEFAULT_PROVIDER

app = FastAPI(title="Solver YAML Agent")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset='utf-8'/>
      <meta name='viewport' content='width=device-width, initial-scale=1'/>
      <title>Solver YAML Agent</title>
      <style>
        :root {{ color-scheme: dark; }}
        body {{ font-family: Inter, Arial, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }}
        .layout {{ max-width: 1080px; margin: 0 auto; padding: 16px; }}
        .panel {{ background: #111827; border: 1px solid #334155; border-radius: 14px; }}
        .chat {{ min-height: 320px; max-height: 58vh; overflow: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; }}
        .msg {{ padding: 10px 12px; border-radius: 12px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; }}
        .msg.user {{ align-self: flex-end; background: #1d4ed8; max-width: 92%; }}
        .msg.bot {{ align-self: flex-start; background: #1f2937; max-width: 95%; }}
        .composer {{ margin-top: 12px; padding: 12px; display: flex; flex-direction: column; gap: 8px; }}
        .row {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; }}
        .row.compact {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        .main-input {{ min-height: 90px; resize: vertical; }}
        .base-yaml {{ min-height: 72px; max-height: 140px; resize: vertical; }}
        label {{ font-size: 12px; opacity: 0.8; }}
        input, textarea, button {{ border-radius: 10px; border: 1px solid #334155; background: #0b1220; color: #e2e8f0; padding: 9px; font-size: 13px; }}
        button {{ background: #2563eb; border: none; cursor: pointer; font-weight: 600; }}
        button:disabled {{ opacity: 0.65; cursor: not-allowed; }}
        .footer {{ display: flex; justify-content: space-between; align-items: center; gap: 10px; }}
        .typing {{ opacity: 0.75; font-size: 12px; }}
        @media (max-width: 900px) {{ .row {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
        @media (max-width: 640px) {{ .row, .row.compact {{ grid-template-columns: 1fr; }} .chat {{ max-height: 48vh; }} }}
      </style>
    </head>
    <body>
      <div class='layout'>
        <div class='panel chat' id='chat'>
          <div class='msg bot'>Готово. Опишите задачу, и я сгенерирую YAML в real-time.</div>
        </div>

        <div class='panel composer'>
          <div class='row compact'>
            <div><label>Provider</label><input id='provider' value='{DEFAULT_PROVIDER}' /></div>
            <div><label>Model</label><input id='model' value='{DEFAULT_MODEL}' /></div>
            <div><label>API key</label><input id='api_key' type='password' placeholder='optional' /></div>
            <div><label>Base URL</label><input id='base_url' placeholder='https://provider.example/v1' /></div>
          </div>

          <div class='row compact'>
            <div><label>Output file</label><input id='filename' value='generated_config.yaml' /></div>
            <div><label>Base YAML (optional)</label><textarea id='base_yaml' class='base-yaml' placeholder='existing YAML'></textarea></div>
          </div>

          <div>
            <label>Request (Enter = send, Shift+Enter = newline)</label>
            <textarea id='request' class='main-input' placeholder='Сгенерируй конфиг...'></textarea>
          </div>

          <div class='footer'>
            <button id='send'>Generate</button>
            <div id='status' class='typing'></div>
          </div>
        </div>
      </div>

      <script>
        const chat = document.getElementById('chat');
        const statusEl = document.getElementById('status');
        const sendBtn = document.getElementById('send');
        const requestEl = document.getElementById('request');

        function addMessage(text, role) {{
          const div = document.createElement('div');
          div.className = `msg ${{role}}`;
          div.textContent = text;
          chat.appendChild(div);
          chat.scrollTop = chat.scrollHeight;
          return div;
        }}

        async function run() {{
          const request = requestEl.value.trim();
          if (!request || sendBtn.disabled) return;

          addMessage(request, 'user');
          requestEl.value = '';
          const bot = addMessage('', 'bot');
          statusEl.textContent = 'Модель печатает...';
          sendBtn.disabled = true;

          const form = new FormData();
          ['provider','model','api_key','base_url','base_yaml','filename'].forEach((id) => {{
            form.append(id, document.getElementById(id).value);
          }});
          form.append('request', request);

          try {{
            const response = await fetch('/generate-stream', {{ method: 'POST', body: form }});
            if (!response.ok || !response.body) {{
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
          }}
        }}

        sendBtn.addEventListener('click', run);
        requestEl.addEventListener('keydown', (event) => {{
          if (event.key === 'Enter' && !event.shiftKey) {{
            event.preventDefault();
            run();
          }}
        }});
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

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
