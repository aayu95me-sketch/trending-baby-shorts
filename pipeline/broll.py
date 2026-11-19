"""Free AI b-roll and real page screenshots for the new-style Shorts (runs on GitHub Actions, no keys, no cost).

studio/public/broll/prompts.json  {"calc": "close-up of a hand typing on a calculator app ...", ...}
    -> studio/public/broll/<name>.jpg  vertical 1080x1920 AI image (Pollinations, keyless free tier, Flux model)
studio/public/broll/shots.json    {"epfo": "https://unifiedportal-mem.epfindia.gov.in/memberinterface/", ...}
    -> studio/public/broll/<name>.jpg  phone-size screenshot of the real page (Playwright Chromium)

Files that already exist are skipped, so a rerun only fetches what is missing. Failures are listed, never fatal:
the composition falls back to the dark grid when an image is missing.
"""
import io, json, sys, time, urllib.parse
from pathlib import Path

import requests
from PIL import Image

D = Path(__file__).resolve().parent.parent / "studio" / "public" / "broll"
W, H = 1080, 1920
failed = []


def fit(img: Image.Image) -> Image.Image:
    """Cover-crop to 1080x1920."""
    img = img.convert("RGB")
    s = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - W) // 2, 0 if img.height > img.width * 1.9 else (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def ai_images():
    p = D / "prompts.json"
    if not p.exists():
        return
    style = ", photorealistic, natural light, shallow depth of field, vertical 9:16, no text, no letters, no watermark, no faces"
    for i, (name, prompt) in enumerate(json.loads(p.read_text()).items()):
        out = D / f"{name}.jpg"
        if out.exists():
            continue
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt + style) + f"?width={W}&height={H}&seed={101 + i}&nologo=true&model=flux"
        for attempt in range(4):
            try:
                r = requests.get(url, timeout=180)
                if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
                    src = Image.open(io.BytesIO(r.content)); fit(src.crop((round(src.width * 0.055), 0, round(src.width * 0.945), round(src.height * 0.94)))).save(out, quality=88)  # drop the free-tier watermark strip
                    print("ai ok", name)
                    break
                print("ai", name, r.status_code, r.text[:120])
            except Exception as e:  # network hiccup or rate limit
                print("ai", name, "error", e)
            time.sleep(20 * (attempt + 1))
        else:
            failed.append(name)
        time.sleep(16)  # anonymous tier: about one image every 15 s


def screenshots():
    p = D / "shots.json"
    if not p.exists():
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": 412, "height": 732}, device_scale_factor=2.62, is_mobile=True, has_touch=True,
                            user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Mobile Safari/537.36",
                            locale="en-IN")
        for name, spec in json.loads(p.read_text()).items():
            out = D / f"{name}.jpg"
            if out.exists():
                continue
            url, clicks = (spec, []) if isinstance(spec, str) else (spec["url"], spec.get("click", []))
            try:
                pg = ctx.new_page()
                pg.goto(url, wait_until="networkidle", timeout=60000)
                pg.wait_for_timeout(2500)
                for sel in clicks:  # close pop-ups (for example EPFO's security notice) so the real page shows
                    try:
                        pg.click(sel, timeout=4000); pg.wait_for_timeout(1200); break
                    except Exception:
                        pass
                fit(Image.open(io.BytesIO(pg.screenshot()))).save(out, quality=90)
                print("shot ok", name)
                pg.close()
            except Exception as e:
                print("shot", name, "failed", str(e)[:160])
                failed.append(name)
        b.close()


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "ai"):
        ai_images()
    if which in ("all", "shots"):
        screenshots()
    print("FAILED:", failed or "none")
