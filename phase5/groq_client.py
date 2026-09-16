"""
Shared Groq client for compact, optional LLM calls.
"""

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


def load_env(project_root):
    env_path = Path(project_root) / ".env"
    if not env_path.exists():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'").strip()
            os.environ[key.strip()] = value


def extract_json_object(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in Groq response")
    candidate = text[start:end + 1]
    try:
        return json.loads(candidate, strict=False)
    except json.JSONDecodeError:
        sanitized = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', candidate)
        return json.loads(sanitized, strict=False)


def call_groq_json(project_root, system_prompt, user_payload, max_tokens=1800, temperature=0.2):
    load_env(project_root)
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        api_key = api_key.strip().strip('"').strip("'").strip()
    model = os.environ.get("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip()
    if not api_key:
        return {
            "ok": False,
            "error": "GROQ_API_KEY not found",
            "data": None,
        }

    body = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
    }
    request = urllib.request.Request(
        GROQ_API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
        return {
            "ok": True,
            "error": None,
            "data": extract_json_object(content),
            "usage": result.get("usage", {}),
            "model": model,
        }
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "error": f"HTTP {exc.code}: {error_body}",
            "data": None,
            "model": model,
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "data": None,
            "model": model,
        }
