"""Long-video deep stats for Doubt Clear (owner OAuth, read-only) -> analysis/long.md.

Reads analysis/long_videos.csv (id,folder,title,posted_ist). For each long video: totals (views, watch minutes,
avg view duration/%, likes, comments, shares, subs), daily views, traffic sources + details (search terms,
suggesting videos, external sites), retention at 5% steps with relative performance, and public comments.
Also channel-wide watch hours since launch (for the 4,000 h goal) and Shorts vs long split.
"""
import csv, json, os, sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "analysis"
IST = timezone(timedelta(hours=5, minutes=30))
KEY = os.environ.get("YOUTUBE_API_KEY") or ""
raw = os.environ.get("YT_OAUTH_TOKEN", "")
if not raw:
    sys.exit("YT_OAUTH_TOKEN not set")
tok = json.loads(raw)
r = requests.post(tok.get("token_uri", "https://oauth2.googleapis.com/token"), data={
    "client_id": tok["client_id"], "client_secret": tok["client_secret"],
    "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"}, timeout=60)
if r.status_code != 200:
    sys.exit(f"token refresh failed {r.status_code}")
H = {"Authorization": "Bearer " + r.json()["access_token"]}
END = date.today().isoformat()


def q(start, **p):
    p.update({"ids": "channel==MINE", "startDate": start, "endDate": END})
    x = requests.get("https://youtubeanalytics.googleapis.com/v2/reports", params=p, headers=H, timeout=60)
    if x.status_code != 200:
        return [["ERR", x.status_code, x.text[:160]]]
    return x.json().get("rows", []) or []


out = ["# Doubt Clear: long videos", "", f"Updated {datetime.now(IST):%d %b %Y %H:%M} IST (Analytics lags 1-2 days).", ""]
ch = q("2026-11-09", metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost")
out += ["## Channel since 9 Nov", "", f"views, minutes watched, subs gained, subs lost: {ch}", ""]
ct = q("2026-11-09", dimensions="creatorContentType", metrics="views,estimatedMinutesWatched,averageViewDuration")
out += [f"by content type (type, views, minutes, avg s): {ct}", ""]

for v in csv.DictReader((A / "long_videos.csv").open(encoding="utf-8")):
    vid, start = v["id"], v["posted_ist"][:10]
    f = f"video=={vid}"
    out += [f"## {v['title']} ({vid}, posted {v['posted_ist']} IST)", ""]
    tot = q(start, filters=f, metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,"
            "likes,comments,shares,subscribersGained")
    out += ["views, minutes, avg s, avg %, likes, dislikes, comments, shares, subs+, subs-, playlist starts:", f"{tot}", ""]
    try:
        cards = q(start, filters=f, metrics="cardImpressions,cardClicks,annotationImpressions,annotationClicks")
        out += [f"cards/endscreen (card impr, card clicks, annot impr, annot clicks): {cards}", ""]
    except Exception as e:
        pass
    out += ["Daily (day, views, minutes):"]
    for d in q(start, dimensions="day", filters=f, metrics="views,estimatedMinutesWatched", sort="day"):
        out.append(f"- {d}")
    out += ["", "Traffic sources (source, views, minutes):"]
    srcs = q(start, dimensions="insightTrafficSourceType", filters=f, metrics="views,estimatedMinutesWatched", sort="-views")
    for s in srcs:
        out.append(f"- {s}")
    for s in srcs:
        if s and s[0] in ("YT_SEARCH", "RELATED_VIDEO", "EXT_URL", "SHORTS_CONTENT_LINKS", "YT_CHANNEL", "PLAYLIST", "END_SCREEN", "NOTIFICATION"):
            det = q(start, dimensions="insightTrafficSourceDetail", filters=f + f";insightTrafficSourceType=={s[0]}",
                    metrics="views", sort="-views", maxResults=15)
            out += [f"  {s[0]} detail: {det}"]
    out += ["", "Devices:", f"{q(start, dimensions='deviceType', filters=f, metrics='views,estimatedMinutesWatched')}", ""]
    out += ["Retention (ratio of video, audienceWatchRatio, relativeRetentionPerformance):"]
    ret = q(start, dimensions="elapsedVideoTimeRatio", filters=f + ";audienceType==ORGANIC",
            metrics="audienceWatchRatio,relativeRetentionPerformance")
    if not ret or ret[0][0] == "ERR":
        ret = q(start, dimensions="elapsedVideoTimeRatio", filters=f, metrics="audienceWatchRatio,relativeRetentionPerformance")
    for row in ret:
        out.append(f"- {row}")
    if KEY:
        c = requests.get("https://www.googleapis.com/youtube/v3/commentThreads", params={
            "part": "snippet", "videoId": vid, "maxResults": 50, "key": KEY, "textFormat": "plainText"}, timeout=60).json()
        out += ["", "Public comments:"]
        for it in c.get("items", []):
            s = it["snippet"]["topLevelComment"]["snippet"]
            out.append(f"- {s.get('authorDisplayName')}: {s.get('textDisplay','')[:200]} (likes {s.get('likeCount')}, replies {it['snippet'].get('totalReplyCount')})")
        st = requests.get("https://www.googleapis.com/youtube/v3/videos", params={"part": "statistics,contentDetails", "id": vid, "key": KEY}, timeout=60).json()
        out += ["", f"Public stats: {st.get('items', [{}])[0].get('statistics')} duration {st.get('items', [{}])[0].get('contentDetails', {}).get('duration')}"]
    out.append("")
out += ["## Search terms behind the search-driven Shorts", ""]
for vid, name in [("5yPFfXIUo28", "GTA 6 India price"), ("QQ5mUOKvQY0", "Mexico pterodactyl"), ("Fp7cRSWnBeI", "Toxic"),
                  ("argEAZpmXY8", "PS5 + GTA 6"), ("gLQFF1Y72o8", "Diwali Bumper"), ("GGCvptk1WoE", "Gold")]:
    det = q("2026-11-10", dimensions="insightTrafficSourceDetail", filters=f"video=={vid};insightTrafficSourceType==YT_SEARCH",
            metrics="views", sort="-views", maxResults=25)
    daily = q("2026-11-10", dimensions="day", filters=f"video=={vid}", metrics="views", sort="day")
    out += [f"### {name}", f"terms: {det}", f"daily: {daily}", ""]
(A / "long.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
