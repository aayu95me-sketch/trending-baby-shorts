"""Stock video + AI stills for a long (16:9) video. Runs in GitHub Actions (the cloud sandbox has no web access). Free, no keys.
Usage: python pipeline/long_assets.py <folder>
Reads studio/public/<folder>/assets.json:
  {"mixkit": {"calc": ["calculator", "finance"], ...},      -> ft/<name>.mp4 (first Mixkit hit per tag list, 1920x1080, 14 s) + ft/<name>-<i>.jpg previews
   "ai":     {"notes": "stacks of Indian rupee notes ...", ...}}  -> ai/<name>.jpg (Pollinations Flux 1920x1080, no faces, no text)
Existing files are skipped. Writes assets-sheet.jpg (every file labelled) and assets-credits.json."""
import io, json, re, subprocess, sys, tempfile, time, urllib.parse
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "studio" / "public" / sys.argv[1]
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
W, H = 1920, 1080
spec = json.loads((D / "assets.json").read_text(encoding="utf-8"))
credits = json.loads((D / "assets-credits.json").read_text()) if (D / "assets-credits.json").exists() else {}


def curl(url, out=None, t=90):
    args = ["curl", "-sSL", "--max-time", str(t), "-A", UA, url] + (["-o", str(out)] if out else [])
    r = subprocess.run(args, capture_output=True, timeout=t + 10)
    return r.stdout.decode("utf-8", "ignore") if not out else r.returncode == 0


def mixkit():
    (D / "ft").mkdir(exist_ok=True)
    for name, tags in spec.get("mixkit", {}).items():
        out = D / "ft" / f"{name}.mp4"
        if out.exists():
            continue
        urls = []
        for tag in tags:
            html = curl(f"https://mixkit.co/free-stock-video/{tag}/") or ""
            urls += [u for u in dict.fromkeys(re.findall(r"https://assets\.mixkit\.co/videos/[^\"' )]+?\.mp4", html)) if u not in urls]
            time.sleep(1)
        print(name, len(urls), "clips", flush=True)
        pick = spec.get("pick", {}).get(name, 0)
        for i, u in enumerate(urls[:4]):  # previews of the first 4 so Claude can choose with "pick"
            tmp = Path(tempfile.mkstemp(suffix=".mp4")[1])
            if curl(u, tmp, 60):
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "2", "-i", str(tmp), "-frames:v", "1", "-vf", "scale=480:-2", str(D / "ft" / f"{name}-{i}.jpg")], timeout=60)
                if i == pick:
                    for v in dict.fromkeys([u.replace("-360.mp4", "-1080.mp4"), u.replace("-360.mp4", "-720.mp4"), u]):
                        if curl(v, tmp, 120) and tmp.stat().st_size > 50_000:
                            break
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-t", "14", "-an", "-vf",
                                    f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,setsar=1",
                                    "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], timeout=600)
                    credits[f"ft/{name}.mp4"] = {"src": v, "lic": "Mixkit free licence (no attribution required)"}
            tmp.unlink(missing_ok=True)


def ai():
    (D / "ai").mkdir(exist_ok=True)
    style = ", photorealistic, cinematic natural light, shallow depth of field, 16:9, no text, no letters, no watermark, no people, no faces"
    for i, (name, prompt) in enumerate(spec.get("ai", {}).items()):
        out = D / "ai" / f"{name}.jpg"
        if out.exists():
            continue
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt + style) + f"?width={W}&height={int(H / 0.94)}&seed={301 + i}&nologo=true&model=flux"
        for attempt in range(4):
            try:
                r = requests.get(url, timeout=180)
                if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
                    src = Image.open(io.BytesIO(r.content)).convert("RGB")
                    src = src.crop((0, 0, src.width, round(src.height * 0.94)))  # drop the free-tier watermark strip
                    ImageOps.fit(src, (W, H)).save(out, quality=88)
                    credits[f"ai/{name}.jpg"] = {"src": "AI image (Pollinations, Flux)", "prompt": prompt}
                    print("ai ok", name, flush=True)
                    break
                print("ai", name, r.status_code, r.text[:120], flush=True)
            except Exception as e:  # noqa: BLE001
                print("ai", name, "error", e, flush=True)
            time.sleep(20 * (attempt + 1))
        time.sleep(16)


def sheet():
    files = sorted(list((D / "ft").glob("*.jpg")) + list((D / "ai").glob("*.jpg")))
    tiles = []
    for f in files:
        im = ImageOps.fit(Image.open(f).convert("RGB"), (480, 270))
        ImageDraw.Draw(im).rectangle([0, 0, 480, 26], fill="black"); ImageDraw.Draw(im).text((6, 6), f"{f.parent.name}/{f.name}", fill="yellow")
        tiles.append(im)
    if tiles:
        s = Image.new("RGB", (4 * 480, ((len(tiles) + 3) // 4) * 270), "black")
        for i, t in enumerate(tiles):
            s.paste(t, ((i % 4) * 480, (i // 4) * 270))
        s.save(D / "assets-sheet.jpg", quality=80)


mixkit(); ai(); sheet()
(D / "assets-credits.json").write_text(json.dumps(credits, indent=1, ensure_ascii=False), encoding="utf-8")
