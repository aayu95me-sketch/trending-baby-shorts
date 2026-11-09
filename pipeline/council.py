"""Reel council (Ayush, 9 Nov 2026): every reel is judged in 4 parts, 1 script, 2 voice, 3 visuals, 4 the whole reel,
by Claude (leader) + Gemini (watches and hears the reel) + gpt-oss on Groq (reads script, scenes and the spoken transcript).
They debate the reel's chance of going viral and agree on ONE version. Free tiers only.

Usage: python pipeline/council.py <folder>       (folder under studio/public; files go to council/<folder>/)
Needs:  council/<folder>/reel.mp4      360p copy of the render (the workflow makes it from branch render-<folder>)
        council/<folder>/claude-brief.md   Claude's round 0: own scores + proposed fixes, written before seeing any reply
Rounds: 1 blind (each scores alone) -> 2 rebuttal (each reads the others + Claude) -> 3 only if claude-final.md exists
        (Claude's proposed final version; each answers AGREE/DISAGREE with a final score). Raw replies saved unedited.
"""
import base64, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
NAME = sys.argv[1]
src = ROOT / "studio" / "public" / NAME
d = ROOT / "council" / NAME
GK, QK = os.environ.get("GEMINI_API_KEY", ""), os.environ.get("GROQ_API_KEY", "")
stamp = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
read = lambda p: p.read_text(encoding="utf-8") if p.exists() else "(missing)"

tl = json.loads(read(src / "timeline.json")) if (src / "timeline.json").exists() else {}
spoken = " ".join(f"{w['start']:.1f}:{w['w']}" for w in tl.get("words", [])) or "(no timeline)"
PACK = f"""REEL: {NAME}
TOPIC AND LABELS: {read(src / 'labels.json')}
SCRIPT ([shown|spoken] pairs, @cue = scene change):
{read(src / 'script.txt')}
VOICE TEXT SENT TO TTS (Devanagari, Gemini TTS voice Orus):
{read(src / 'tts.txt')}
SCENES (what is on screen per beat):
{read(src / 'scenes.json')}
SPOKEN WORDS WITH START TIMES (Whisper on the final voice), total {tl.get('total', '?')} s:
{spoken}
SOURCES:
{read(src / 'sources.txt')}"""

GOAL = 'GOAL (restate it first): "Make the Doubt Clear accounts (YouTube Shorts + Facebook Reels, India, Hinglish) go viral."'
CONCEPT = ("CONCEPT: for each Google Trends topic, answer the doubt people have about it (the truth, the logic, the purpose or the solution) "
           "so viewers get confirmation they can use. The answer must be TRUE and sourced even when the crowd believes otherwise; allegations stay allegations.")
RULES = ("RULES: Rs 0 spend (free tools only). Faceless, AI voice labelled. Trend topics die in about a day, so fixes must be doable the same evening. "
         "Do not invent numbers, view counts or algorithm facts; write 'verify' when unsure. Be blunt, flattery is useless.")
PARTS = """Judge 4 parts, each 0-10 (10 = best possible for going viral) with the probability (rough %) that THIS part helps the reel get
5x a typical new-channel view count, and the single highest-impact fix:
1 SCRIPT (hook in the first 1.5 s, the doubt, the truth/reveal, pace, one idea per line, ending/CTA, accuracy)
2 VOICE (Indian accent, energy, clarity, numbers and names said right, speed)
3 VISUALS (frame 1 scroll-stop, cut pace, caption readability on a phone, text size and time on screen >= 1.5 s, footage relevance)
4 WHOLE REEL (would a stranger watch to the end, comment, share, follow?)"""
FORMAT = """Answer in this exact shape:
## Goal (restated)
## Scores (table: part | score /10 | viral-help % | one-line reason)
## Viral chance of the whole reel as it is: X% (rough guess, say why)
## Fixes (ranked, max 6, each doable tonight for free; say exactly what to change: line, word, scene, timing)
## Viral chance after your fixes: Y%"""


def save(name, served, text):
    (d / name).write_text(f"<!-- raw reply, unedited. model: {served}; {stamp()} -->\n\n{text.strip()}\n", encoding="utf-8")


def gmodels():
    r = requests.get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", headers={"x-goog-api-key": GK}, timeout=60).json()
    names = [m["name"].split("/")[-1] for m in r.get("models", []) if "flash" in m["name"] and "generateContent" in m.get("supportedGenerationMethods", [])]
    pref = [n for n in ("gemini-3.5-flash", "gemini-flash-latest", "gemini-3.5-flash-lite") if n in names]
    return pref + [n for n in sorted(names, reverse=True) if n not in pref][:3]


def gemini(parts):
    last = ""
    for model in gmodels():
        for attempt in range(3):
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", headers={"x-goog-api-key": GK},
                              json={"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.4}}, timeout=600)
            if r.status_code == 200:
                ps = r.json()["candidates"][0]["content"]["parts"]
                return model, "".join(p.get("text", "") for p in ps if not p.get("thought"))
            last = f"{model} {r.status_code} {r.text[:200]}"; print(last, flush=True); time.sleep(15 * (attempt + 1))
    raise SystemExit("gemini failed: " + last)


def groq(text):
    last = ""
    for model in ("openai/gpt-oss-120b", "llama-3.3-70b-versatile", "openai/gpt-oss-20b"):
        for attempt in range(3):
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": "Bearer " + QK},
                              json={"model": model, "temperature": 0.4, "max_completion_tokens": 3500, "messages": [{"role": "user", "content": text}]}, timeout=300)
            if r.status_code == 200:
                return model, r.json()["choices"][0]["message"]["content"]
            if r.status_code in (400, 404):
                break
            last = f"{model} {r.status_code} {r.text[:200]}"; print(last, flush=True); time.sleep(20 * (attempt + 1))
    raise SystemExit("groq failed: " + last)


BASE = f"You are an independent member of a 3-AI content council (Claude leads; Gemini and gpt-oss are members).\n{GOAL}\n{CONCEPT}\n{RULES}\n\n{PACK}\n\n{PARTS}\n\n{FORMAT}"
video = d / "reel.mp4"

f = d / "round1-gemini.md"
if not f.exists():
    parts = [{"text": "--- THE REEL (watch and listen) ---"}, {"inline_data": {"mime_type": "video/mp4", "data": base64.b64encode(video.read_bytes()).decode()}}] if video.exists() else []
    parts.append({"text": BASE + "\n\nYou watched and heard the reel above. Listen closely to the accent, the numbers, names and currency words. "
                  "Score alone; you have not seen anyone else's scores. Under 900 words."})
    served, text = gemini(parts); save(f.name, served, text); print("gemini r1", served, flush=True)

f = d / "round1-gptoss.md"
if not f.exists():
    served, text = groq(BASE + "\n\nYou cannot watch the video; judge voice from the transcript and timing, visuals from the scene list. "
                        "Score alone; you have not seen anyone else's scores. Under 800 words.")
    save(f.name, served, text); print("gptoss r1", served, flush=True)

g1, o1, c0 = read(d / "round1-gemini.md"), read(d / "round1-gptoss.md"), read(d / "claude-brief.md")
R2 = (f"{GOAL}\n{CONCEPT}\n{RULES}\n\n{PACK}\n\nRound 2 (rebuttal). Below are the other member's round 1 and Claude's brief (written before seeing any reply). "
      "Under 500 words: ## Where they are right ## Where they are wrong (cite the reel) ## Your FINAL scores (table: part | score | viral-help %; say what you changed) "
      "## The ONE version you back: the ranked fixes (max 5) ## Final viral chance after fixes: Y%\n\nCLAUDE'S BRIEF:\n" + c0)
f = d / "round2-gemini.md"
if not f.exists():
    served, text = gemini([{"text": R2 + "\n\nYOUR ROUND 1:\n" + g1 + "\n\nGPT-OSS ROUND 1:\n" + o1}]); save(f.name, served, text); print("gemini r2", served, flush=True)
f = d / "round2-gptoss.md"
if not f.exists():
    served, text = groq(R2 + "\n\nYOUR ROUND 1:\n" + o1 + "\n\nGEMINI ROUND 1:\n" + g1); save(f.name, served, text); print("gptoss r2", served, flush=True)

fin = d / "claude-final.md"
if fin.exists():
    both = "GEMINI ROUND 2:\n" + read(d / "round2-gemini.md") + "\n\nGPT-OSS ROUND 2:\n" + read(d / "round2-gptoss.md")
    q = (f"{GOAL}\n{CONCEPT}\n{RULES}\n\nRound 3 (agreement). Claude, the leader, read both round-2 replies and proposes the ONE final version below. "
         f"Under 300 words: AGREE or DISAGREE per point with why, anything critical still missing, then FINAL score /10 for each of the 4 parts "
         f"and the final viral chance %.\n\n{both}\n\nCLAUDE'S PROPOSED FINAL VERSION:\n" + read(fin))
    for name, fn in (("round3-gemini.md", lambda: gemini([{"text": q}])), ("round3-gptoss.md", lambda: groq(q))):
        if not (d / name).exists():
            served, text = fn(); save(name, served, text); print(name, served, flush=True)
