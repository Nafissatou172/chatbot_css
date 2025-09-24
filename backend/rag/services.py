import os
import json
import httpx
from django.conf import settings
from typing import Generator

MISTRAL_API_KEY = getattr(settings, "MISTRAL_API_KEY", "")
MISTRAL_API_URL = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1/chat/completions")

def _build_prompt(question: str, context: str) -> str:
    return (
        "Tu es un assistant qui répond UNIQUEMENT avec les informations ci-dessous.\n"
        "Si la réponse n'est pas présente, dis simplement que tu ne sais pas.\n\n"
        f"<CONTEXTE>\n{context}\n</CONTEXTE>\n\n"
        f"Question: {question}\nRéponse:"
    )

def generate_stream(question: str, context: str) -> Generator[str, None, None]:
    if not MISTRAL_API_KEY:
        raise RuntimeError("⚠️ MISTRAL_API_KEY non défini")

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "mistral-small",  # ou mistral-medium selon ton compte
        "messages": [{"role": "user", "content": _build_prompt(question, context)}],
        "temperature": 0.1,
        "stream": True,
    }

    with httpx.stream("POST", MISTRAL_API_URL, headers=headers, json=payload, timeout=None) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8") if isinstance(line, bytes) else line
            if not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                break
            try:
                j = json.loads(data)
                delta = j["choices"][0]["delta"]
                if "content" in delta:
                    yield delta["content"]
            except Exception:
                continue
