"""Studio-level numbers for Doubt Clear from the free YouTube Analytics API (owner OAuth, read-only).

Secret YT_OAUTH_TOKEN = the authorized-user JSON made on Ayush's Mac by Connect-Doubt-Clear.command
(holds client_id, client_secret, refresh_token; scopes yt-analytics.readonly + youtube.readonly).
Writes analysis/studio.md: per reel average % viewed, average seconds viewed, subs gained, shares, traffic sources,
and the retention curve (audienceWatchRatio at 10% steps). Analytics data lags about 1-2 days behind real time.
"""
import csv, json, os, sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "analysis"
IST = timezone(timedelta(hours=5, minutes=30))
CHANNEL = "UCnr4ef3wsderFvW-CKri3ZQ"  # Doubt Clear

raw = os.environ.get("YT_OAUTH_TOKEN", "")
if not raw:
    print("YT_OAUTH_TOKEN not set; skipping Studio numbers"); sys.exit(0)
tok = json.loads(raw)
r = requests.post(tok.get("token_uri", "https://oauth2.googleapis.com/token"), data={
    "client_id": tok["client_id"], "client_secret": tok["client_secret"],
    "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"}, timeout=60)
if r.status_code != 200:
    sys.exit(f"token refresh failed {r.status_code}: {r.text[:200]}\n"
             "Fix: double-click Connect-Doubt-Clear.command on the Mac again (Testing-mode tokens expire after about 7 days).")
H = {"Authorization": "Bearer " + r.json()["access_token"]}

me = requests.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet", "mine": "true"}, headers=H, timeout=60).json()
ids = [c["id"] for c in me.get("items", [])]
if CHANNEL not in ids:
    sys.exit(f"token is for {ids}, not Doubt Clear ({CHANNEL}). Re-run Connect-Doubt-Clear.command and pick the Doubt Clear channel.")

videos = list(csv.DictReader((A / "videos.csv").open(encoding="utf-8")))
start = min(v["posted_ist"][:10] for v in videos)
end = date.today().isoformat()


def q(**p):
    p.update({"ids": "channel==MINE", "startDate": start, "endDate": end})
    x = requests.get("https://youtubeanalytics.googleapis.com/v2/reports", params=p, headers=H, timeout=60)
    if x.status_code != 200:
        print("analytics", x.status_code, x.text[:200]); return []
    return x.json().get("rows", []) or []


vid_filter = "video==" + ",".join(v["id"] for v in videos)
main = {row[0]: row[1:] for row in q(dimensions="video", filters=vid_filter,
        metrics="views,averageViewPercentage,averageViewDuration,subscribersGained,shares,likes,comments")}
traffic = {}
for vid, src, views in q(dimensions="video,insightTrafficSourceType", filters=vid_filter, metrics="views"):
    traffic.setdefault(vid, []).append((src, int(views)))

out = ["# Doubt Clear: Studio numbers", "",
       f"Updated {datetime.now(IST):%d %b %Y %H:%M} IST from the YouTube Analytics API ({start} to {end}). "
       "Analytics lags 1-2 days, so the newest reels may show nothing yet.", "",
       "| Video | Views | Avg % viewed | Avg s viewed | Subs gained | Shares | Likes | Comments | Top traffic sources |",
       "|---|---|---|---|---|---|---|---|---|"]
for v in videos:
    m = main.get(v["id"])
    t = ", ".join(f"{s} {n}" for s, n in sorted(traffic.get(v["id"], []), key=lambda z: -z[1])[:3]) or "-"
    if m:
        views, pct, dur, subs, shares, likes, com = m
        out.append(f"| {v['title']} | {int(views)} | {pct:.0f}% | {dur:.1f} | {int(subs)} | {int(shares)} | {int(likes)} | {int(com)} | {t} |")
    else:
        out.append(f"| {v['title']} | - | - | - | - | - | - | - | {t} |")

out += ["", "## Retention (share of viewers still watching at each point of the reel; above 100% = rewatches)", "",
        "| Video | " + " | ".join(f"{p}%" for p in range(0, 101, 10)) + " |", "|---|" + "---|" * 11]
for v in videos:
    rows = q(dimensions="elapsedVideoTimeRatio", filters=f"video=={v['id']}", metrics="audienceWatchRatio")
    if not rows:
        out.append(f"| {v['title']} | " + " | ".join("-" for _ in range(11)) + " |"); continue
    pts = {round(float(a), 2): float(b) for a, b in rows}
    cells = []
    for p in range(0, 101, 10):
        k = min(pts, key=lambda z: abs(z - p / 100))
        cells.append(f"{pts[k] * 100:.0f}")
    out.append(f"| {v['title']} | " + " | ".join(cells) + " |")
out += ["", "Viewed vs swiped away is only shown in YouTube Studio (not in the API).", ""]
(A / "studio.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
