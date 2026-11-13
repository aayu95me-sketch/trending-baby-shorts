"""Backup voice: Kokoro-82M (Apache-2.0, offline, Hindi voices). Used only when Gemini TTS fails.

Usage: python pipeline/tts_kokoro.py <name>   (writes studio/public/<name>/voice_raw.wav)
Kokoro's Hindi voices read Devanagari, so the romanised Hinglish spoken text is first turned into Devanagari
with the free Groq model when GROQ_API_KEY is set. The voice differs from Puck: use only as a fallback.
"""
import os, subprocess, sys

import numpy as np
import soundfile as sf
from kokoro import KPipeline

sys.path.insert(0, os.path.dirname(__file__))
name = sys.argv[1]
d = f"studio/public/{name}"
text = subprocess.run([sys.executable, "pipeline/align.py", name, "tts-text"], capture_output=True, text=True).stdout.strip()
if os.environ.get("GROQ_API_KEY"):
    from llm import groq
    try:
        text = groq("Rewrite this romanised Hinglish narration in Devanagari script so a Hindi text-to-speech voice reads it "
                    "naturally. Keep English words, write them phonetically in Devanagari. Keep '...' pauses. Output only the text.\n\n"
                    + text, as_json=False).strip()
    except Exception as e:  # fall back to the raw text rather than losing the backup voice
        print(f"::warning::Devanagari conversion failed ({e}); Kokoro will read the romanised text", flush=True)
pipe = KPipeline(lang_code="h", repo_id="hexgrad/Kokoro-82M")
audio = np.concatenate([np.asarray(a) for _, _, a in pipe(text, voice=os.environ.get("KOKORO_VOICE", "hm_omega"), speed=1.1)])
sf.write(f"{d}/voice_raw.wav", audio, 24000)
print("ok kokoro", round(len(audio) / 24000, 2), "s")
