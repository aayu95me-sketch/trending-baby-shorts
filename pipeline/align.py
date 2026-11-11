"""Word-timed timeline for a reel from its narrator take, using local Whisper (free) plus real pauses.

Script format (studio/public/<name>/script.txt), one line per narration line:
    RBI ki meeting [5 se 7|paanch se saat]@meeting October tak hai, aur repo rate abhi [5.25%|sawa paanch percent]@rate hai.
  - [shown|spoken] : the subtitle shows the first part, the voice says the second. Write every number as spoken
                     words on the spoken side so the TTS never misreads digits.
  - @key           : after a word or bracket, exports its start time as cue "key" for the composition.

Usage:
    python3 align.py <name> tts-text      # prints the text to send to TTS (spoken side only)
    python3 align.py <name> [tempo]       # voice_raw.wav -> voice.wav + timeline.json (needs faster-whisper)
"""
import difflib, json, os, re, subprocess, sys
from pathlib import Path

import numpy as np

NAME = sys.argv[1]
D = Path(__file__).resolve().parent.parent / "studio" / "public" / NAME
TAIL = 1.0
TOKEN = re.compile(r"\[([^\]|]+)\|([^\]]+)\](?:@(\w+))?|(\S+?)(?:@(\w+))?(?=\s|$)")


def parse():
    """-> list of lines; each line is a list of units {show, spoken: [words], cue}."""
    lines = []
    for raw in (D / "script.txt").read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        units = []
        for m in TOKEN.finditer(raw.strip()):
            if m.group(1):
                units.append({"show": m.group(1), "spoken": m.group(2).split(), "cue": m.group(3)})
            else:
                units.append({"show": m.group(4), "spoken": [m.group(4)], "cue": m.group(5)})
        lines.append(units)
    return lines


V = {"अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au", "ऑ": "o", "ऋ": "ri"}
M = {"ा": "aa", "ि": "i", "ी": "ee", "ु": "u", "ू": "oo", "े": "e", "ै": "ai", "ो": "o", "ौ": "au", "ॉ": "o", "ृ": "ri", "ं": "n", "ँ": "n", "ः": "h", "़": ""}
C = dict(zip("कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह", "k kh g gh n ch chh j jh n t th d dh n t th d dh n p ph b bh m y r l v sh sh s h".split()))
C.update({"क़": "q", "ख़": "kh", "ग़": "g", "ज़": "z", "ड़": "d", "ढ़": "dh", "फ़": "f"})


def translit(w):
    out, i = "", 0
    while i < len(w):
        ch = w[i]
        if ch in C:
            out += C[ch]
            nxt = w[i + 1] if i + 1 < len(w) else ""
            if nxt == "्":
                i += 1
            elif nxt not in M:
                out += "a"
        elif ch in M:
            if out.endswith("a") and M[ch] not in ("n", "h", ""):
                out = out[:-1]
            out += M[ch]
        elif ch in V:
            out += V[ch]
        elif ch.isascii():
            out += ch
        i += 1
    return out


def norm(w):
    w = translit(w.lower())
    w = re.sub(r"[^a-z0-9]", "", w)
    # loose phonetic key: collapse vowels and aspiration, so "faisla"~"phaisalaa", "sattar"~"satar"
    w = w.replace("ph", "f").replace("w", "v").replace("z", "j")
    w = re.sub(r"(?<=[kgcjtdpb])h", "", w)
    w = re.sub(r"[aeiou]+", "a", w)
    return re.sub(r"(.)\1+", r"\1", w)


def sim(x, y):
    return difflib.SequenceMatcher(None, x, y).ratio() if x and y else 0.0


def ff(*a):
    return subprocess.run(["ffmpeg", "-y", "-hide_banner", *a], capture_output=True, text=True, check=True).stderr


lines = parse()
spoken_text = " ".join(" ".join(" ".join(u["spoken"]) for u in l) for l in lines)
if len(sys.argv) > 2 and sys.argv[2] == "tts-text":
    print(spoken_text)
    raise SystemExit

tempo = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
raw, voice = D / "voice_raw.wav", D / "voice.wav"
GAP = os.environ.get("KEEP_PAUSES", "0.2")  # longest pause kept, in seconds (calm takes keep more)
ff("-i", str(raw), "-af",
   "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
   f"silenceremove=stop_periods=-1:stop_duration={GAP}:stop_threshold=-38dB:stop_silence={GAP},"
   f"atempo={tempo},highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,loudnorm=I=-12:TP=-1.5:LRA=9",
   "-ar", "48000", "-ac", "1", str(voice))
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(voice)],
                           capture_output=True, text=True).stdout)
log = ff("-i", str(voice), "-af", "silencedetect=noise=-35dB:d=0.09", "-f", "null", "-")
pauses = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)],
                  [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]))

# --- Whisper word times (romanised by priming with the script) ---
from faster_whisper import WhisperModel  # noqa: E402

pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(voice), "-ar", "16000", "-ac", "1", "-f", "s16le", "-"], capture_output=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
model = WhisperModel(os.environ.get("ALIGN_MODEL", "small"), device="cpu", compute_type="int8")
script_words = [w for l in lines for u in l for w in u["spoken"]]


def hear(lang):
    heard = []
    real = re.compile(r"[A-Za-z0-9\u0900-\u0963\u0966-\u097F]")
    def words(chunk, off, **kw):
        segs, _ = model.transcribe(chunk, language=lang, word_timestamps=True, beam_size=5, condition_on_previous_text=False,
                                   temperature=[0.0, 0.2, 0.4, 0.6], **kw)
        return [(w.word.strip(), w.start + off, w.end + off) for sg in segs for w in sg.words if real.search(w.word)]
    for off in np.arange(0, dur, 7.0):  # short windows: Whisper drops words on long Hinglish takes
        chunk = audio[int(off * 16000):int((off + 8.0) * 16000)]
        got = words(chunk, off, vad_filter=False)
        if len(got) < 4 and len(chunk) > 16000 * 3:  # Whisper looped ("।।।।") on this window: retry with VAD, then as two halves
            got = words(chunk, off, vad_filter=True)
            if len(got) < 4:
                h = len(chunk) // 2
                got = words(chunk[:h + 8000], off, vad_filter=True) + words(chunk[h:], off + h / 16000, vad_filter=True)
            print(f"  whisper {lang}: window at {off:.0f}s looped, retry heard {len(got)} words")
        for wd in got:
            if not heard or wd[1] > heard[-1][1] + 0.05:
                heard.append(wd)
    return heard


def align(heard):
    """Needleman-Wunsch with fuzzy word similarity: script word index -> start time (None when not heard)."""
    a, b = [norm(w) for w in script_words], [norm(h[0]) for h in heard]
    n, m = len(a), len(b)
    S = np.zeros((n + 1, m + 1)); S[:, 0] = -0.4 * np.arange(n + 1); S[0, :] = -0.4 * np.arange(m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            S[i, j] = max(S[i - 1, j - 1] + sim(a[i - 1], b[j - 1]) - 0.35, S[i - 1, j] - 0.4, S[i, j - 1] - 0.4)
    times = [None] * n
    i, j = n, m
    while i > 0 and j > 0:
        if S[i, j] == S[i - 1, j - 1] + sim(a[i - 1], b[j - 1]) - 0.35:
            if sim(a[i - 1], b[j - 1]) >= 0.5:
                times[i - 1] = heard[j - 1][1]
            i, j = i - 1, j - 1
        elif S[i, j] == S[i - 1, j] - 0.4:
            i -= 1
        else:
            j -= 1
    return times


# Hindi decoding first; when it collapses (it sometimes loops on one syllable), try English decoding and keep the better match.
heard = hear("hi"); times = align(heard)
heard_en = None
if sum(t is not None for t in times) < 0.6 * len(script_words):
    heard_en = hear("en"); times_en = align(heard_en)
    print(f"whisper hi matched {sum(t is not None for t in times)}, en matched {sum(t is not None for t in times_en)}")
    if sum(t is not None for t in times_en) > sum(t is not None for t in times):
        heard, times = heard_en, times_en
matched = sum(t is not None for t in times)
direct = {i for i, t in enumerate(times) if t is not None}  # words Whisper actually heard (not interpolated)


def snap(t):
    """Whisper tends to start a word at the end of the previous one; move starts sitting in a pause to its end."""
    for s, e in pauses:
        if s - 0.05 <= t < e:
            return e
    return t


known = [(i, snap(t)) for i, t in enumerate(times) if t is not None]
if not known:
    known = [(0, 0.0)]
known = [(-1, 0.0)] + known + [(len(script_words), dur)] if known[0][0] != 0 else known + [(len(script_words), dur)]
for (i0, t0), (i1, t1) in zip(known, known[1:]):
    for j in range(max(i0 + 1, 0), i1):
        times[j] = t0 + (t1 - t0) * (j - i0) / (i1 - i0)
for i, t in known:
    if 0 <= i < len(times):
        times[i] = t

# --- digit check: Whisper writes long numbers as digits, so compare digit strings (1 slip is allowed but flagged) ---
DEV = str.maketrans("०१२३४५६७८९", "0123456789")
heard_tokens = {re.sub(r"\D", "", h[0].translate(DEV)) for h in heard}
heard_digits = "".join(re.sub(r"\D", "", h[0].translate(DEV)) for h in heard)


def digit_match(exp):
    """Fewest edits (substitute, drop, add one digit) to find exp somewhere in the heard digits; None if hardly any digits were heard."""
    if len(heard_digits) < len(exp) - 1:
        return None
    prev = [0] * (len(heard_digits) + 1)  # free start anywhere in the heard digits
    for i, c in enumerate(exp, 1):
        cur = [i]
        for j, h in enumerate(heard_digits, 1):
            cur.append(min(prev[j - 1] + (c != h), prev[j] + 1, cur[j - 1] + 1))
        prev = cur
    return min(prev)


# --- build display words, lines and cues ---
words, out_lines, cues, numbers, k = [], [], {}, [], 0
for l in lines:
    first = None
    for u in l:
        st = times[k]
        if re.search(r"\d", u["show"]) and not re.fullmatch(r"\d+(st|nd|rd|th)", u["show"].lower()):  # number check (ordinals like 8th are labels, not figures): the spoken words of every on-screen number must be heard
            idx = range(k, k + len(u["spoken"]))
            exp = re.sub(r"\D", "", u["show"])
            share = round(sum(i in direct for i in idx) / len(idx), 2)
            if len(exp) >= 5:
                diff = digit_match(exp)
            elif len(exp) >= 2:  # Whisper splits decimals ("2 .57"), so look for the digits run in the joined digit string
                diff = 0 if exp in heard_digits else None
            else:  # single digit: must be heard as its own token
                diff = 0 if exp and exp in heard_tokens else None
            if diff is not None and diff == 0:
                share = 1.0
            elif diff == 1:
                share = max(share, 0.5)  # near match: pass, but a person should listen
            numbers.append({"show": u["show"], "spoken": " ".join(u["spoken"]), "heard": share, "digit_diff": diff})
        k += len(u["spoken"])
        words.append({"w": u["show"], "start": round(float(st), 3)})
        first = st if first is None else first
        if u["cue"]:
            cues[u["cue"]] = round(float(st), 3)
    out_lines.append({"start": round(first, 3), "text": " ".join(u["show"] for u in l)})
for i, w in enumerate(words):
    w["end"] = round(min(words[i + 1]["start"] - 0.02, w["start"] + 0.8) if i + 1 < len(words) else dur, 3)
for i, l in enumerate(out_lines):
    nxt = out_lines[i + 1]["start"] if i + 1 < len(out_lines) else dur
    gap = [p[0] for p in pauses if nxt - 0.6 <= p[0] <= nxt + 0.01]  # the pause right before the next line
    l["end"] = round(gap[0] if gap else nxt, 3)

(D / "timeline.json").write_text(json.dumps({"total": round(dur + TAIL, 3), "voice": f"{NAME}/voice.wav", "lines": out_lines,
                                             "words": words, "cues": cues, "numbers": numbers, "heard": [h[0] for h in heard]},
                                            ensure_ascii=False, indent=1))
print(f"voice {dur:.2f}s, whisper matched {matched}/{len(script_words)} words")
for l in out_lines:
    print(f"  {l['start']:6.2f}-{l['end']:6.2f}  {l['text']}")
print("cues:", cues)
print("heard:", " ".join(h[0] for h in heard))
weak = [n for n in numbers if n["heard"] < 0.5]
for n in numbers:
    print(f"  number {'OK  ' if n['heard'] >= 0.5 else 'FAIL'}{' (1 digit differs, LISTEN)' if n.get('digit_diff') == 1 else ''} {n['show']} -> {n['spoken']} (heard {n['heard']:.0%})")
# sync check: a line squeezed below ~0.13 s a word means Whisper lost it and the captions would drift
squeezed = [l["text"] for l in out_lines if not 0.13 * len(l["text"].split()) <= (l["end"] - l["start"]) <= 0.9 * len(l["text"].split()) + 1.0]
for s in squeezed:
    print(f"  SYNC FAIL (line too short or too long: Whisper missed it or the voice stalled): {s}")
# wrong-word guard (3 Nov: a Puck take said "29,200 DOLLARS" for Rs 29,200; Whisper and Gemini both heard it, the number check passed).
# TTS sometimes adds words of its own. Listen with English decoding too, and stop if a currency we never wrote is spoken.
if heard_en is None:
    heard_en = hear("en")
FOREIGN = re.compile(r"\$|£|€|dollar|pound|euro|डॉलर|पाउंड|यूरो", re.I)
script_text = " ".join(script_words)
foreign = sorted({h[0] for h in heard + heard_en if FOREIGN.search(h[0]) and not FOREIGN.search(script_text)})
if foreign:
    print(f"  WRONG WORD: the voice seems to say {foreign}, which is not in the script (rupee amounts must never be read as dollars). LISTEN or re-record.")
    if os.environ.get("NUMCHECK_STRICT"):
        sys.exit(f"wrong-word check failed: {foreign}")
if squeezed and os.environ.get("NUMCHECK_STRICT"):
    sys.exit("sync check failed: rerun with whisper=medium")
if weak and os.environ.get("NUMCHECK_STRICT"):
    sys.exit(f"number check failed for: {', '.join(n['show'] for n in weak)}")
