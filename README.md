# Trending baby (Doubt Clear)

Daily Shorts / Reels from Google Trends. For every trending topic we answer the **doubt** people have about it
(is it true? why is it happening? what does it mean?) with the true answer and the source on screen.
Channel name idea: **Doubt Clear**. Language: Hinglish. Voice: AI (Gemini TTS, Orus), labelled "AI VOICE".

## Daily flow
1. Ayush sends the Google Trends CSV (Trending now, India, past 24 h export).
2. `python pipeline/trends.py daily/inbox/<file>.csv` -> `daily/<date>/topics.json` (one job per topic, the doubt-searches pulled
   from "Trend breakdown", repeats from earlier days flagged so the new video takes a different angle).
3. Claude researches each topic and writes `studio/public/<date>-<topic>/`:
   `script.txt` (`[shown|spoken]` pairs, `@cue` markers), `tts.txt` (same words in Devanagari, for the Indian accent),
   `scenes.json` (footage / headline screenshot / big text per beat), `sources.txt`, `labels.json`.
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

Pipeline and template carried over from chunav-diary-reels.
