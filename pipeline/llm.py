"""Tiny clients for the two free reviewer models. Keys come from the environment (GitHub secrets), never from files."""
import json, os, time, requests


def gemini(prompt, model=None):
    model = model or os.environ.get("GEMINI_TEXT_MODEL", "gemini-flash-latest")
    for wait in (20, 45, 0):  # free tier limits requests per minute: wait and retry on 429/503
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                          headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
                          json={"contents": [{"parts": [{"text": prompt}]}],
                                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2}}, timeout=90)
        if r.status_code in (429, 503) and wait:
            time.sleep(wait)
            continue
        break
    r.raise_for_status()
    return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])


GROQ_MODELS = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile", "openai/gpt-oss-20b"]  # tried in order; Groq retires models, so a 404 moves on


def groq(prompt, model=None, as_json=True):
    models = [model or os.environ["GROQ_MODEL"]] if (model or os.environ.get("GROQ_MODEL")) else GROQ_MODELS
    for i, m in enumerate(models):
        body = {"model": m, "temperature": 0.2, "messages": [{"role": "user", "content": prompt}]}
        if as_json:
            body["response_format"] = {"type": "json_object"}
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                          headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"}, json=body, timeout=90)
        if r.status_code in (400, 404) and i < len(models) - 1:
            print(f"::warning::Groq model {m} refused ({r.status_code}: {r.text[:150]}), trying the next", flush=True)
            continue
        if not r.ok:
            raise requests.HTTPError(f"{r.status_code} {r.text[:300]}", response=r)
        text = r.json()["choices"][0]["message"]["content"]
        return json.loads(text) if as_json else text
