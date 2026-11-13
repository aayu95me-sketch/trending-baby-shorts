# Trending baby (Doubt Clear)

Daily Shorts / Reels from Google Trends. For every trending topic we answer the **doubt** people have about it
(is it true? why is it happening? what does it mean?) with the true answer and the source on screen.
Channel name idea: **Doubt Clear**. Language: Hinglish. Voice: AI (Gemini TTS, Orus), labelled "AI VOICE".

**How we work:** [PLAYBOOK.md](PLAYBOOK.md) (rules, council, 4 gates, viewer card). Results: [analysis/scorecard.md](analysis/scorecard.md), lessons: [LESSONS.md](LESSONS.md), mistakes: [ERRORS.md](ERRORS.md).

## Daily flow
1. Ayush sends the Google Trends CSV (Trending now, India, past 24 h export).
2. `python pipeline/trends.py daily/inbox/<file>.csv` -> `daily/<date>/topics.json` (one job per topic, the doubt-searches pulled
   from "Trend breakdown", repeats from earlier days flagged so the new video takes a different angle).
3. Claude researches each topic and writes `studio/public/<date>-<topic>/`:
   `script.txt` (`[shown|spoken]` pairs, `@cue` markers), `tts.txt` (same words in Devanagari, for the Indian accent),
   `scenes.json` (footage / headline screenshot / big text per beat), `sources.txt`, `labels.json`, `viewer.md` (viewer-moment card, PLAYBOOK 5.1).
4. Push `daily/<date>/make.txt` (one folder per line) -> GitHub Actions "Make the day's Shorts" voices, checks and renders every
   topic in parallel. Each mp4 lands on branch `render-<folder>` and as an Actions artifact.
5. Claude checks every video (frames + listen-back), then Ayush approves and the Mac session schedules them on YT Shorts + FB Reels.

## Rules
- Facts true and sourced, even when the popular belief says otherwise. Allegations are said as allegations.
- Nothing paid. Posts are scheduled, never live. Only Ayush's own typed message is approval.
- Secrets `GEMINI_API_KEY`, `GROQ_API_KEY` live only in the repo's Actions secrets.

## Repo map
| Path | What |
|---|---|
| `pipeline/trends.py` | CSV -> topic jobs |
| `pipeline/tts.py`, `align.py` | voice (Gemini Orus) and Whisper word timing + spoken-number check |
| `pipeline/review.py`, `llm.py` | auto-review by Gemini + Groq (free) |
| `pipeline/broll.py` | phone-size screenshots of the source headlines (`studio/public/broll/shots.json`) |
| `studio/src/TrendShort.tsx` | the video template (composition `Trend`, `--props='{"dir":"<folder>"}'`) |
| `studio/public/footage/` | free Mixkit stock clips (see CREDITS.md) |
| `.github/workflows/make-day.yml` | the free render farm |
| `pipeline/stats.py`, `.github/workflows/stats.yml` | hourly view snapshots -> `analysis/scorecard.md` (free YouTube Data API) |

Pipeline and template carried over from chunav-diary-reels.

## When GitHub Actions is down
Scenes-only change (voice unchanged): render in the cloud container. Copy `voice.wav` and `timeline.json` from branch `render-<folder>`
into `studio/public/<folder>/`, then `cd studio && npm ci && npx remotion render src/index.ts Trend ../out/<folder>.mp4 --props='{"dir":"<folder>"}'
--browser-executable=/opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell/chrome-headless-shell` (~70 s). New voices need the Gemini key (repo secrets only).
