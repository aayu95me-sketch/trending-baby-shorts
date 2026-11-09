"""Free real stock video for the "Paisa ka Sach" Shorts, from Mixkit (free licence: commercial use, no attribution, no key).
Usage: python pipeline/footage.py find  -> studio/public/footage/candidates/<slot>-<n>.jpg (4 frames each) + candidates.json
       python pipeline/footage.py get   -> clips from picks.json cut to 1080x1920 h264: studio/public/footage/<slot>.mp4
Runs in GitHub Actions (the cloud sandbox has no web access). Every download is capped at 90 s (curl --max-time)."""
import json, re, subprocess, sys, tempfile, time
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "studio" / "public" / "footage"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def curl(url, out=None, t=90):
    args = ["curl", "-sSL", "--max-time", str(t), "-A", UA, url]
    if out:
        args += ["-o", str(out)]
    r = subprocess.run(args, capture_output=True, timeout=t + 10)
    return r.stdout.decode("utf-8", "ignore") if not out else r.returncode == 0


def search(tag):
    html = curl(f"https://mixkit.co/free-stock-video/{tag}/")
    urls = re.findall(r"https://assets\.mixkit\.co/videos/[^\"' )]+?\.mp4", html or "")
    seen, out = set(), []
    for u in urls:
        m = re.search(r"/videos/(?:preview/)?(?:mixkit-)?([^/]*?)(\d+)", u)
        key = m.group(2) if m else u
        if key in seen:
            continue
        seen.add(key)
        title = re.search(r"/videos/(?:preview/)?([^/]+)\.mp4", u)
        out.append({"url": u, "title": title.group(1) if title else u.rsplit("/", 1)[-1], "tag": tag, "lic": "Mixkit free licence"})
    print("search", tag, len(urls), "urls", len(out), "unique", flush=True)
    if not out:
        print((html or "")[:400], flush=True)
    return out


def find():
    qs = json.loads((D / "queries.json").read_text())
    (D / "candidates").mkdir(exist_ok=True)
    allc, cache = {}, {}
    for slot, tags in qs.items():
        cands, seen = [], set()
        for tag in tags:
            cache.setdefault(tag, search(tag)); time.sleep(1)
            for c in cache[tag]:
                if c["url"] not in seen:
                    seen.add(c["url"]); cands.append(c)
        cands = cands[:10]
        for i, c in enumerate(cands):
            tmp = Path(tempfile.mkstemp(suffix=".mp4")[1])
            if not curl(c["url"], tmp, 60):
                continue
            out = D / "candidates" / f"{slot}-{i}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-vf", "fps=0.6,scale=-2:200,tile=4x1", "-frames:v", "1", str(out)], timeout=120)
            dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(tmp)], capture_output=True, text=True).stdout.strip()
            c["dur"] = dur; c["sheet"] = out.name if out.exists() else None
            tmp.unlink(missing_ok=True)
            print(slot, i, c["title"], dur, flush=True)
        allc[slot] = cands
    (D / "candidates.json").write_text(json.dumps(allc, indent=1, ensure_ascii=False))


def get():
    picks = json.loads((D / "picks.json").read_text())
    for slot, p in picks.items():
        tmp = Path(tempfile.mkstemp(suffix=".mp4")[1])
        urls = [p["url"].replace("-360.mp4", "-1080.mp4"), p["url"].replace("-360.mp4", "-720.mp4"), p["url"]]
        for u in dict.fromkeys(urls):
            if curl(u, tmp, 120) and tmp.stat().st_size > 50_000:
                break
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1"
        if p.get("speed"):
            vf = f"setpts=PTS/{p['speed']}," + vf
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(p.get("start", 0)), "-i", str(tmp), "-t", str(p.get("dur", 6)), "-an", "-vf", vf,
                        "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(D / f"{slot}.mp4")], check=True, timeout=600)
        print("got", slot, u, flush=True)
    old = (D / "CREDITS.md").read_text() if (D / "CREDITS.md").exists() else "# Footage\nAll clips: Mixkit (mixkit.co) free stock video licence, no attribution required.\n"
    (D / "CREDITS.md").write_text(old +
                                  "\n".join(f"- {s}: {p['title']}" for s, p in picks.items()) + "\n")


def mascot():
    """Cartoon presenter poses from Pollinations (free, no key): mascot.json {pose: prompt} -> studio/public/mascot/<pose>.png"""
    from urllib.parse import quote
    m = json.loads((D / "mascot.json").read_text())
    out = D.parent / "mascot"; out.mkdir(exist_ok=True)
    for pose, prompt in m["poses"].items():
        url = f"https://image.pollinations.ai/prompt/{quote(m['base'] + ', ' + prompt)}?width=768&height=768&nologo=true&seed={m.get('seed', 7)}&model=flux"
        for attempt in range(3):
            if curl(url, out / f"{pose}.jpg", 150) and (out / f"{pose}.jpg").stat().st_size > 20_000:
                break
            time.sleep(10)
        print("mascot", pose, (out / f"{pose}.jpg").stat().st_size if (out / f"{pose}.jpg").exists() else 0, flush=True)


{"find": find, "get": get, "mascot": mascot}[sys.argv[1]]()
