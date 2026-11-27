"""A/B voice test: voice voicetest/<n>/tts.txt (first '## ' line = director's note) once per voice in voices.txt,
same model, same note, same accent prompt as pipeline/long_voice.py. Writes voicetest/<n>/<Voice>.wav (no ffmpeg needed)."""
import base64, os, sys, time, wave
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
D = Path(__file__).resolve().parent.parent / "voicetest" / sys.argv[1]
ACCENT = ("Accent: a young Indian from Delhi speaking everyday Hinglish, with a natural Indian accent all the way through, including English words "
          "and numbers (say them the way Indians say them). Never an American or British accent. Read the transcript word for word: add, drop or change nothing. "
          "All money is Indian rupees. This is one chapter of a 10-minute YouTube explainer: a friendly, sharp storyteller who did the maths himself, never a newsreader.")
lines = D.joinpath("tts.txt").read_text(encoding="utf-8").splitlines()
note, text = lines[0][3:].strip(), "\n".join(l for l in lines[1:] if l.strip())
key = os.environ["GEMINI_API_KEY"]
model = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
for voice in [v.strip() for v in D.joinpath("voices.txt").read_text().split() if v.strip()]:
    prompt = f"### DIRECTOR'S NOTES\n{ACCENT} {note}\n\n### TRANSCRIPT (speak only this, do not read the notes)\n{text}"
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    for attempt in range(4):
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                          headers={"x-goog-api-key": key}, json=body, timeout=300)
        print(voice, model, r.status_code, flush=True)
        if r.status_code == 200:
            pcm = base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            with wave.open(str(D / f"{voice}.wav"), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
            print(voice, round(len(pcm) / 48000, 1), "s", flush=True)
            break
        print(r.text[:300], flush=True); time.sleep(40 * (attempt + 1))
