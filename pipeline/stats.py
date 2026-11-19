"""Analysis step: snapshot public stats of every Doubt Clear video in analysis/videos.csv.

Uses the free YouTube Data API v3 (videos.list, 1 quota unit per 50 videos; free quota is 10,000 units a day).
Key: YOUTUBE_API_KEY, else GOOGLE_API_KEY / GEMINI_API_KEY (works only if "YouTube Data API v3" is enabled on that key's project).
Appends to analysis/snapshots.csv and rewrites analysis/scorecard.md with views nearest to 1 h, 4 h, 24 h and 72 h after posting.
"""
import csv, os, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "analysis"
IST = timezone(timedelta(hours=5, minutes=30))
KEY = os.environ.get("YOUTUBE_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""
CHECKPOINTS = (1, 4, 24, 72)

videos = list(csv.DictReader((A / "videos.csv").open(encoding="utf-8")))
if not videos:
    sys.exit("no videos in analysis/videos.csv")
now = datetime.now(timezone.utc)

stats = {}
ids = [v["id"] for v in videos]
for i in range(0, len(ids), 50):
    r = requests.get("https://www.googleapis.com/youtube/v3/videos",
                     params={"part": "statistics,status", "id": ",".join(ids[i:i + 50]), "key": KEY}, timeout=60)
    if r.status_code != 200:
        sys.exit(f"YouTube Data API {r.status_code}: {r.text[:300]}\n"
                 "Fix: add a YOUTUBE_API_KEY repo secret (a plain Google Cloud API key with YouTube Data API v3 enabled; free). "
                 "The Gemini key is refused by YouTube (401, 'API keys are not supported').")
    for it in r.json().get("items", []):
        stats[it["id"]] = it

snap = A / "snapshots.csv"
new = not snap.exists()
with snap.open("a", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    if new:
        w.writerow(["taken_utc", "id", "hours_since_post", "views", "likes", "comments", "privacy"])
    for v in videos:
        it = stats.get(v["id"])
        posted = datetime.strptime(v["posted_ist"], "%Y-%m-%d %H:%M").replace(tzinfo=IST)
        h = round((now - posted).total_seconds() / 3600, 2)
        if it is None:
            w.writerow([now.strftime("%Y-%m-%d %H:%M"), v["id"], h, "", "", "", "not-found"]); continue
        s = it.get("statistics", {})
        w.writerow([now.strftime("%Y-%m-%d %H:%M"), v["id"], h, s.get("viewCount", ""), s.get("likeCount", ""),
                    s.get("commentCount", ""), it.get("status", {}).get("privacyStatus", "")])

rows = list(csv.DictReader(snap.open(encoding="utf-8")))


def nearest(vid, target):
    """Views from the snapshot closest to <target> hours after posting (within 25% of the target, min 0.5 h)."""
    best = None
    for r in rows:
        if r["id"] != vid or not r["views"]:
            continue
        gap = abs(float(r["hours_since_post"]) - target)
        if gap <= max(0.5, target * 0.25) and (best is None or gap < best[0]):
            best = (gap, r["views"])
    return best[1] if best else "-"


latest = {}
for r in rows:
    if r["views"]:
        latest[r["id"]] = r
views = sorted(int(latest[v["id"]]["views"]) for v in videos if v["id"] in latest)
median = views[len(views) // 2] if views else 0

out = [f"# Doubt Clear scorecard", "", f"Updated {now.astimezone(IST):%d %b %Y %H:%M} IST from the YouTube Data API (public counts). "
       f"Median latest views: {median}. A hit is about 5x the median (playbook rule; re-test).", "",
       "| Posted (IST) | Video | " + " | ".join(f"{c} h" for c in CHECKPOINTS) + " | Latest views | Likes | Comments | Hit? |",
       "|---|---|" + "---|" * (len(CHECKPOINTS) + 4)]
for v in videos:
    L = latest.get(v["id"], {})
    lv = int(L["views"]) if L.get("views") else None
    hit = "yes" if lv is not None and median and lv >= 5 * median else ""
    out.append(f"| {v['posted_ist']} | [{v['title']}](https://youtube.com/shorts/{v['id']}) | "
               + " | ".join(nearest(v["id"], c) for c in CHECKPOINTS)
               + f" | {lv if lv is not None else '-'} | {L.get('likes', '-')} | {L.get('comments', '-')} | {hit} |")
out += ["", "Viewed-vs-swiped, retention and traffic source are only in YouTube Studio; the Mac session reads those at 72 h.", ""]
(A / "scorecard.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
