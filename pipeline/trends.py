"""Read Ayush's daily Google Trends CSV ("Trending now" export) and list one video job per topic.

Usage: python pipeline/trends.py daily/inbox/trending_IN_1d_20261109-2104.csv
Writes daily/<YYYY-MM-DD>/topics.json and prints a short table.

CSV columns: Trends, Search volume, Started, Ended, Trend breakdown, Explore link.
- "Trend breakdown" is what people actually typed. The questions inside it (kya, kyu, why, how, is, real, fake, truth...)
  are the doubt the video answers.
- A topic that was already covered on an earlier day is marked repeat=True with the earlier angles, so the new video
  takes a different angle (Ayush, 9 Nov 2026).
"""
import csv, json, re, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAILY = ROOT / "daily"
DOUBT = re.compile(r"\b(kya|kyu|kyun|kaise|kab|kitna|kaun|sach|jhooth|why|how|what|when|who|is|real|fake|true|truth|rumou?r|affair|"
                   r"price|date|launch|collection|today|now|live|age|wife|news)\b", re.I)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def volume(v: str) -> int:
    m = re.match(r"([\d.]+)\s*([KM]?)", v or "")
    if not m:
        return 0
    return int(float(m.group(1)) * {"": 1, "K": 1_000, "M": 1_000_000}[m.group(2)])


def history() -> dict:
    """topic slug -> [{date, angle}] from earlier days' topics.json files that recorded an angle."""
    seen: dict = {}
    for f in sorted(DAILY.glob("*/topics.json")):
        for t in json.loads(f.read_text(encoding="utf-8")):
            if t.get("angle"):
                seen.setdefault(t["slug"], []).append({"date": f.parent.name, "angle": t["angle"]})
    return seen


def main(path: str):
    p = Path(path)
    m = re.search(r"(\d{8})-(\d{4})", p.name)
    day = datetime.strptime(m.group(1), "%Y%m%d").date().isoformat() if m else datetime.now().date().isoformat()
    past = history()
    topics = []
    with p.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            name = (row.get("Trends") or "").strip()
            if not name:
                continue
            terms = [t.strip() for t in (row.get("Trend breakdown") or "").split(",") if t.strip()]
            terms = list(dict.fromkeys(t for t in terms if len(t) > 3))
            doubts = [t for t in terms if DOUBT.search(t) and t.lower() != name.lower()]
            s = slug(name)
            earlier = [h for h in past.get(s, []) if h["date"] != day]
            topics.append({
                "slug": s, "dir": f"{day.replace('-', '')}-{s[:24].strip('-')}", "topic": name,
                "volume": row.get("Search volume", ""), "volume_n": volume(row.get("Search volume", "")),
                "started": row.get("Started", ""), "ended": row.get("Ended", ""),
                "searches": terms[:40], "doubt_searches": doubts[:15],
                "explore": "https://trends.google.com/trends/" + (row.get("Explore link") or "").lstrip("./"),
                "repeat": bool(earlier), "earlier_angles": earlier, "angle": None, "status": "new",
            })
    topics.sort(key=lambda t: -t["volume_n"])
    out = DAILY / day
    out.mkdir(parents=True, exist_ok=True)
    (out / "topics.json").write_text(json.dumps(topics, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{day}: {len(topics)} topics -> {out / 'topics.json'}")
    for t in topics:
        print(f"- {t['topic']} ({t['volume']}){' REPEAT' if t['repeat'] else ''}: {', '.join(t['doubt_searches'][:5])}")


if __name__ == "__main__":
    main(sys.argv[1])
