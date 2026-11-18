"""Gemini listens to each chapter voice of a long video and compares it with the text it was given (Whisper loops on long Hinglish
takes, so its number check is unreliable there; 18 Nov 2026). Usage: python pipeline/listen.py <folder>
Reads studio/public/<folder>/chN/voice_raw.wav + chN/tts.txt; writes studio/public/<folder>/listen-report.md and listen-report.json."""
import base64, json, os, subprocess, sys, time
from pathlib import Path

import requests

D = Path(__file__).resolve().parent.parent / "studio" / "public" / sys.argv[1]
KEY = os.environ["GEMINI_API_KEY"]
ASK = ("You are checking a Hindi/Hinglish text-to-speech take against the exact text it was asked to read. Listen to the whole audio. "
       "List every place where the audio differs from the text: a missing or extra word or sentence, a wrong or garbled number, a mispronounced name, "
       "a long glitch, noise or repeated syllable, a cut-off ending. Numbers matter most. Small accent differences are fine. "
       'Reply with JSON only: {"ok": true/false, "issues": [{"approx_time_s": 0, "expected": "...", "heard": "...", "severity": "high|low"}]}\n\nTEXT:\n')


def models():
    r = requests.get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", headers={"x-goog-api-key": KEY}, timeout=60).json()
    names = [m["name"].split("/")[-1] for m in r.get("models", []) if "generateContent" in m.get("supportedGenerationMethods", []) and ("pro" in m["name"] or "flash" in m["name"]) and "tts" not in m["name"] and "image" not in m["name"]]
    pref = [n for n in ("gemini-3.5-pro", "gemini-pro-latest", "gemini-3.5-flash", "gemini-flash-latest") if n in names]
    return pref + [n for n in sorted(names, reverse=True) if n not in pref][:3]


out, md = {}, ["# Voice check (Gemini listens to each chapter)\n"]
ms = models()
for cd in sorted(D.glob("ch*"), key=lambda p: int(p.name[2:])):
    wav, txt = cd / "voice_raw.wav", cd / "tts.txt"
    if not wav.exists() or not txt.exists():
        continue
    mp3 = cd / "check.mp3"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-ac", "1", "-b:a", "64k", str(mp3)], check=True)
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": "audio/mp3", "data": base64.b64encode(mp3.read_bytes()).decode()}},
                                    {"text": ASK + txt.read_text(encoding="utf-8")}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}}
    res = None
    for m in ms:
        for attempt in range(2):
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent", headers={"x-goog-api-key": KEY}, json=body, timeout=600)
            if r.status_code == 200:
                t = "".join(p.get("text", "") for p in r.json()["candidates"][0]["content"]["parts"] if not p.get("thought"))
                try:
                    res = {"model": m, **json.loads(t[t.find("{"):t.rfind("}") + 1])}
                except Exception:  # noqa: BLE001
                    res = {"model": m, "raw": t}
                break
            print(cd.name, m, r.status_code, r.text[:150], flush=True); time.sleep(20)
        if res:
            break
    out[cd.name] = res or {"error": "no model answered"}
    md.append(f"## {cd.name}: {'OK' if res and res.get('ok') else 'CHECK'} ({(res or {}).get('model', '-')})")
    for i in (res or {}).get("issues", []):
        md.append(f"- ~{i.get('approx_time_s')}s [{i.get('severity')}] expected \"{i.get('expected')}\", heard \"{i.get('heard')}\"")
    print("\n".join(md[-1 - len((res or {}).get('issues', [])):]), flush=True)
(D / "listen-report.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
(D / "listen-report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
