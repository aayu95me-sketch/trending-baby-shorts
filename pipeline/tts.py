"""Voice one script with Gemini TTS (free tier), voice Orus (Indian accent, blind test 9.5/10). Usage: STYLE="..." python pipeline/tts.py <name>  (needs GEMINI_API_KEY in the environment; writes studio/public/<name>/voice_raw.wav)."""
import base64, json, os, subprocess, sys, requests
PY = ".venv/bin/python" if os.path.exists(".venv/bin/python") else sys.executable
name = sys.argv[1]; d = f"studio/public/{name}"
text = subprocess.run([PY, "pipeline/align.py", name, "tts-text"], capture_output=True, text=True).stdout.strip()
# tts.txt (optional): the same words in Devanagari. Puck reads Roman Hinglish with an American accent; Devanagari gives a native Indian accent (Ayush, 3 Nov).
if os.path.exists(f"{d}/tts.txt"):
    text = open(f"{d}/tts.txt", encoding="utf-8").read().strip()
ACCENT = ("Accent: a young Indian from Delhi speaking everyday Hinglish, with a natural Indian accent all the way through, including English words "
          "and numbers (say them the way Indians say them). Never an American or British accent. Read the transcript word for word: add, drop or change nothing. "
          "All money is Indian rupees.")
style = ACCENT + " " + (os.environ.get("STYLE") or ("Fast, young, witty Delhi explainer, Hinglish, real emotion, never a newsreader. Vary pace and pitch. "
         "Short pauses at '...'. Serious on facts, playful on jokes. Never sound like a newsreader or a dictation."))
prompt = f"### DIRECTOR'S NOTES\n{style}\n\n### TRANSCRIPT (speak only this, do not read the notes)\n{text}"
body = {"contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": os.environ.get("TTS_VOICE") or "Orus"}}}}}
# Each free Gemini TTS model has its own daily quota, so when the first one is used up try the other TTS models (all speak Puck).
key = os.environ["GEMINI_API_KEY"]
first = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
try:
    listed = [m["name"].split("/")[-1] for m in requests.get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", headers={"x-goog-api-key": key}, timeout=60).json().get("models", []) if "tts" in m["name"]]
except Exception:
    listed = []
r = None
for model in [first] + [m for m in sorted(listed, reverse=True) if m != first]:
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", headers={"x-goog-api-key": key}, json=body, timeout=180)
    print(model, r.status_code)
    if r.status_code == 200:
        break
    print(r.text[:300])
if r is None or r.status_code != 200:
    sys.exit(1)
pcm = base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "-", f"{d}/voice_raw.wav"], input=pcm, check=True)
print("ok", len(pcm) / 48000, "s")
