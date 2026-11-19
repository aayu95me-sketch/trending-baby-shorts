"""Real visuals of the topic for each script line (Ayush, 9 Nov 2026: "realistic visuals of the topic that sync with the script").
Usage: python pipeline/real.py <folder>
Reads studio/public/<folder>/visuals.json: {"slot": [source, ...], ...}. A source is one of
  {"og": "<article url>"}                      the article's lead photo (og:image / twitter:image)
  {"wiki": "<search words>", "n": 3}           photos from Wikimedia Commons (free licences, author saved)
  {"img": "<direct image url>"}                one image
  {"yt": "<video url or ytsearch1:words>", "start": 12, "dur": 6}   a clip of a news video / trailer (yt-dlp)
Writes studio/public/<folder>/real/<slot>-<n>.jpg|.mp4, real/candidates.json (source + licence per file) and
real/sheet.jpg (every candidate labelled) so Claude can check each one shows the right person/place/thing before using it.
Runs in GitHub Actions (the cloud sandbox has no web access). Every download is time-capped."""
import json, re, subprocess, sys, time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent.parent
NAME = sys.argv[1]
D = ROOT / "studio" / "public" / NAME
OUT = D / "real"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-IN,en;q=0.9"}
WUA = {"User-Agent": "DoubtClearShorts/1.0 (faceless explainer channel; github actions)"}


def get(url, **kw):
    return requests.get(url, headers=kw.pop("headers", UA), timeout=kw.pop("timeout", 45), **kw)


def save_img(url, out, headers=UA):
    r = get(url, headers=headers)
    if r.status_code != 200 or len(r.content) < 15_000:
        print("  skip", r.status_code, len(r.content), url[:120], flush=True)
        return False
    tmp = out.with_suffix(".tmp")
    tmp.write_bytes(r.content)
    try:
        im = Image.open(tmp).convert("RGB")
    except Exception as e:  # noqa: BLE001
        print("  not an image", e, flush=True); tmp.unlink(); return False
    if min(im.size) < 300:
        print("  too small", im.size, flush=True); tmp.unlink(); return False
    im.thumbnail((1600, 1600))
    im.save(out, quality=90)
    tmp.unlink()
    return True


def og(url):
    html = get(url).text
    found = re.findall(r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)(?::src)?["\'][^>]+content=["\']([^"\']+)', html)
    found += re.findall(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|twitter:image)', html)
    return [(u.replace("&amp;", "&"), {"page": url, "lic": "news photo (copyright of the publisher; used as news clip, Ayush's risk)"}) for u in dict.fromkeys(found)][:2]


def wiki(q, n=3):
    r = get("https://commons.wikimedia.org/w/api.php", headers=WUA, params={
        "action": "query", "format": "json", "generator": "search", "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": n,
        "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1600}).json()
    pages = sorted(r.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})
        artist = re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip()
        out.append((ii.get("thumburl") or ii.get("url"), {"page": ii.get("descriptionurl"), "title": p.get("title"),
                                                          "lic": md.get("LicenseShortName", {}).get("value", "?"), "author": artist}))
    return out


def yt(src, out):
    s, dur = float(src.get("start", 0)), float(src.get("dur", 6))
    cmd = ["yt-dlp", "-q", "--no-playlist", "--max-filesize", "300M", "-f", "bv*[height<=1080][ext=mp4]/bv*[height<=1080]/b",
           "--download-sections", f"*{s}-{s + dur}", "--force-keyframes-at-cuts", "-o", str(out.with_suffix(".src.%(ext)s")),
           "--print", "after_move:%(title)s|%(webpage_url)s|%(channel)s", src["yt"]]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    srcs = list(OUT.glob(out.stem + ".src.*"))
    if r.returncode or not srcs:
        print("  yt failed:", (r.stderr or r.stdout)[-300:], flush=True); return None
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(srcs[0]), "-t", str(dur), "-an", "-vf", "scale=-2:1080,fps=30,setsar=1",
                    "-c:v", "libx264", "-crf", "24", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], check=True, timeout=300)
    for f in srcs:
        f.unlink()
    title, url, ch = (r.stdout.strip().splitlines() or ["||"])[-1].split("|", 2)
    return {"page": url, "title": title, "author": ch, "lic": "video clip (copyright of the channel; news clip, Ayush's risk)"}


def sheet(files):
    tiles = []
    for f in files:
        if f.suffix == ".mp4":
            fr = f.with_suffix(".frame.jpg")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", str(f), "-frames:v", "1", str(fr)], timeout=60)
            if not fr.exists():
                continue
            im = Image.open(fr).convert("RGB"); fr.unlink()
        else:
            im = Image.open(f).convert("RGB")
        im = ImageOps.fit(im, (320, 320))
        ImageDraw.Draw(im).rectangle([0, 0, 320, 30], fill="black")
        ImageDraw.Draw(im).text((6, 6), f.name, fill="yellow")
        tiles.append(im)
    if not tiles:
        return
    cols = 5
    s = Image.new("RGB", (cols * 320, ((len(tiles) + cols - 1) // cols) * 320), "black")
    for i, t in enumerate(tiles):
        s.paste(t, ((i % cols) * 320, (i // cols) * 320))
    s.save(OUT / "sheet.jpg", quality=80)


def main():
    spec = json.loads((D / "visuals.json").read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    cands = json.loads((OUT / "candidates.json").read_text()) if (OUT / "candidates.json").exists() else {}
    for slot, sources in spec.items():
        n = 0
        for src in sources:
            print(slot, src, flush=True)
            try:
                if "yt" in src:
                    out = OUT / f"{slot}-{n}.mp4"
                    meta = yt(src, out)
                    if meta:
                        cands[out.name] = meta; n += 1
                    continue
                items = og(src["og"]) if "og" in src else wiki(src["wiki"], src.get("n", 3)) if "wiki" in src else [(src["img"], {"page": src["img"], "lic": src.get("lic", "?")})]
                for url, meta in items:
                    out = OUT / f"{slot}-{n}.jpg"
                    if url and save_img(url, out, WUA if "wikimedia" in url else UA):
                        cands[out.name] = {**meta, "url": url}; n += 1
                    time.sleep(1)
            except Exception as e:  # noqa: BLE001
                print("  error", e, flush=True)
    (OUT / "candidates.json").write_text(json.dumps(cands, indent=1, ensure_ascii=False), encoding="utf-8")
    sheet(sorted(f for f in OUT.iterdir() if f.suffix in (".jpg", ".mp4") and f.name != "sheet.jpg"))
    print(len(cands), "candidates", flush=True)


main()
