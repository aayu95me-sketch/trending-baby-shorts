"""Auto-reviewer: two free models (Gemini Flash, Groq Llama) read a script before it is voiced and rendered.

Usage: python pipeline/review.py <name>
Reads studio/public/<name>/script.txt (and hooks.txt, one hook per line, if present).
Writes studio/public/<name>/review.json and prints a short report.
Blocks (exit 1) only when BOTH reviewers flag a number mismatch or a compliance problem.
A reviewer that is down or out of free quota is skipped, never blocks.
"""
import json, os, sys
from pathlib import Path

from llm import gemini, groq

name = sys.argv[1]
d = Path(__file__).resolve().parent.parent / "studio" / "public" / name
script = (d / "script.txt").read_text(encoding="utf-8")
hooks = [h.strip() for h in (d / "hooks.txt").read_text(encoding="utf-8").splitlines() if h.strip()] if (d / "hooks.txt").exists() else []

PROMPT = f"""You review a 20-30 second Hinglish YouTube Short script for "Doubt Clear", an Indian channel that answers the doubt behind a trending topic (news, tech, films, sport, weather).
Script format: [shown|spoken] means the screen shows the first part and the voice says the second. Lines are narration.

SCRIPT:
{script}

HOOK OPTIONS (pick the strongest first line for a 1-second scroll stop):
{chr(10).join(f"{i}: {h}" for i, h in enumerate(hooks)) or "none given"}

Check strictly:
1. number_mismatches: any [shown|spoken] pair where the spoken words do not say exactly the shown number/date/amount.
2. compliance_flags: a claim stated as fact that is only an allegation or a rumour, a defamatory statement about a real person,
   stock tips or buy/sell advice, or a number without a source. Reported claims clearly attributed ("report ke mutabik", "memo ka daawa") are fine.
3. hook_scores: 1-10 for each hook option (scroll-stopping, clear number, curiosity). best_hook: index of the best, or -1.
4. hinglish_issues: words that sound unnatural for a young Delhi speaker.
Return only JSON: {{"number_mismatches": [], "compliance_flags": [], "hook_scores": [], "best_hook": -1, "hinglish_issues": [], "one_line_verdict": ""}}"""

results = {}
for label, fn, key in (("gemini", gemini, "GEMINI_API_KEY"), ("groq", groq, "GROQ_API_KEY")):
    if not os.environ.get(key):
        results[label] = {"skipped": f"{key} not set"}
        continue
    try:
        results[label] = fn(PROMPT)
    except Exception as e:  # quota, outage, bad JSON: skip, never block on a reviewer being down
        results[label] = {"skipped": str(e)[:200]}
        print(f"::warning::{label} reviewer skipped: {str(e)[:200]}", flush=True)

live = [r for r in results.values() if "skipped" not in r]
block = []
if len(live) == 2:
    for field in ("number_mismatches", "compliance_flags"):
        if all(r.get(field) for r in live):
            block.append(field)
scores = [r.get("hook_scores") or [] for r in live]
best = -1
if hooks and scores:
    avg = [sum(s[i] for s in scores if i < len(s)) / max(1, sum(1 for s in scores if i < len(s))) for i in range(len(hooks))]
    best = max(range(len(hooks)), key=lambda i: avg[i])
report = {"reviewers": results, "blocked_on": block, "chosen_hook": best, "chosen_hook_text": hooks[best] if best >= 0 else None}
(d / "review.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

lines = [f"## Auto-review: {name}"]
for label, r in results.items():
    if "skipped" in r:
        lines.append(f"- **{label}**: skipped ({r['skipped']})")
    else:
        lines.append(f"- **{label}**: {r.get('one_line_verdict', '')} | numbers: {r.get('number_mismatches') or 'ok'} | "
                     f"compliance: {r.get('compliance_flags') or 'ok'} | hook scores: {r.get('hook_scores')}")
if best >= 0:
    lines.append(f"- **Chosen hook:** {hooks[best]}")
lines.append(f"- **Result:** {'BLOCKED on ' + ', '.join(block) + ' (Claude rewrites once)' if block else 'pass'}")
text = "\n".join(lines)
print(text)
if os.environ.get("GITHUB_STEP_SUMMARY"):
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
        f.write(text + "\n")
sys.exit(1 if block else 0)
