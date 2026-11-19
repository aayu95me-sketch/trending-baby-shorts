"""Voice + timing for a long video, one chapter at a time (Gemini TTS truncates and drifts on 10-minute takes; Whisper alignment is O(n*m)).
Usage: GEMINI_API_KEY=... python pipeline/long_voice.py <folder>
studio/public/<folder>/script.txt and tts.txt are split into chapters by lines starting with '## ' (the text after '## ' in tts.txt is that
chapter's director's note: pace/energy). script.txt uses align.py's format ([shown|spoken], @cue). Each chapter goes to <folder>/chN/,
is voiced (Orus) and aligned with pipeline/align.py (strict number check, medium Whisper on a retry), then all chapters are joined with
a short pause into <folder>/voice.wav + timeline.json (cues shifted to the joined time). A chapter whose tts text did not change keeps its voice."""
import base64, json, os, subprocess, sys, time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
NAME = sys.argv[1]
D = ROOT / "studio" / "public" / NAME
GAP = 0.7
ACCENT = ("Accent: a young Indian from Delhi speaking everyday Hinglish, with a natural Indian accent all the way through, including English words "
          "and numbers (say them the way Indians say them). Never an American or British accent. Read the transcript word for word: add, drop or change nothing. "
          "All money is Indian rupees. This is one chapter of a 10-minute YouTube explainer: a friendly, sharp storyteller who did the maths himself, never a newsreader.")


def split(path):
    chs, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            cur = {"note": line[3:].strip(), "lines": []}; chs.append(cur)
        elif line.strip() and cur is not None:
            cur["lines"].append(line.strip())
    return chs


def tts(text, note, out):
    key = os.environ["GEMINI_API_KEY"]
    prompt = f"### DIRECTOR'S NOTES\n{ACCENT} {note}\n\n### TRANSCRIPT (speak only this, do not read the notes)\n{text}"
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": os.environ.get("TTS_VOICE") or "Orus"}}}}}
    try:
        listed = [m["name"].split("/")[-1] for m in requests.get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", headers={"x-goog-api-key": key}, timeout=60).json().get("models", []) if "tts" in m["name"]]
    except Exception:  # noqa: BLE001
        listed = []
    first = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
    for attempt in range(3):
        for model in [first] + [m for m in sorted(listed, reverse=True) if m != first]:
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", headers={"x-goog-api-key": key}, json=body, timeout=300)
            print(" ", model, r.status_code, flush=True)
            if r.status_code == 200:
                pcm = base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "-", str(out)], input=pcm, check=True)
                return len(pcm) / 48000
            print(" ", r.text[:200], flush=True)
        time.sleep(40 * (attempt + 1))  # free tier: requests per minute
    sys.exit("tts failed")


sc, tt = split(D / "script.txt"), split(D / "tts.txt")
assert len(sc) == len(tt), f"script.txt has {len(sc)} chapters, tts.txt {len(tt)}"
offset, words, cues, lines, numbers, parts, flagged = 0.0, [], {}, [], [], [], []
for i, (s, t) in enumerate(zip(sc, tt), 1):
    cd = D / f"ch{i}"; cd.mkdir(exist_ok=True)
    (cd / "script.txt").write_text("\n".join(s["lines"]) + "\n", encoding="utf-8")
    text = "\n".join(t["lines"])
    same = (cd / "tts.txt").exists() and (cd / "tts.txt").read_text(encoding="utf-8") == text + "\n" and (cd / "voice_raw.wav").exists()
    (cd / "tts.txt").write_text(text + "\n", encoding="utf-8")
    print(f"chapter {i}: {len(text.split())} words, {'reusing voice' if same else 'voicing'}", flush=True)
    if not same:
        print("  raw", round(tts(text, t["note"], cd / "voice_raw.wav"), 1), "s", flush=True)
    env = {**os.environ, "NUMCHECK_STRICT": "1", "KEEP_PAUSES": "0.35"}
    ok = subprocess.run([sys.executable, "pipeline/align.py", f"{NAME}/ch{i}", "1.0"], env={**env, "ALIGN_MODEL": "small"}).returncode == 0
    if not ok:
        # medium Whisper took ~20 min a chapter on the runner (18 Nov); only use it when LONG_MEDIUM=1
        if os.environ.get("LONG_MEDIUM") != "1" or subprocess.run([sys.executable, "pipeline/align.py", f"{NAME}/ch{i}", "1.0"], env={**env, "ALIGN_MODEL": "medium"}).returncode != 0:
            # Whisper often loops on one window of a long Hinglish take (18 Nov), so a second miss does not stop the build:
            # the timeline is still written, the chapter is flagged, and the council (Gemini listens to the render) checks the audio.
            print(f"::warning::chapter {i} failed the number/sync check twice: LISTEN to it in the render", flush=True)
            flagged.append(i)
    tl = json.loads((cd / "timeline.json").read_text(encoding="utf-8"))
    dur = tl["total"] - 1.0  # align.py adds a 1 s tail
    for w in tl["words"]:
        words.append({**w, "start": round(w["start"] + offset, 3), "end": round(w["end"] + offset, 3)})
    for l in tl["lines"]:
        lines.append({**l, "start": round(l["start"] + offset, 3), "end": round(l["end"] + offset, 3)})
    cues.update({k: round(v + offset, 3) for k, v in tl["cues"].items()})
    numbers += tl.get("numbers", [])
    parts.append(cd / "voice.wav")
    offset += dur + GAP

lst = D / "concat.txt"
sil = D / "gap.wav"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(GAP), str(sil)], check=True)
lst.write_text("".join(f"file '{p.resolve()}'\nfile '{sil.resolve()}'\n" for p in parts))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-ar", "48000", "-ac", "1", str(D / "voice.wav")], check=True)
(D / "timeline.json").write_text(json.dumps({"total": round(offset + 1.5, 3), "cues": cues, "lines": lines, "words": words, "numbers": numbers}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"voice {offset:.1f}s in {len(parts)} chapters; cues: {cues}")
(D / "listen.txt").write_text("".join(f"chapter {i}: number/sync check failed twice, listen\n" for i in flagged) or "all chapters passed\n")
