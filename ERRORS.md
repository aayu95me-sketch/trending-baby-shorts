# Production errors log

Every mistake and its fix, so it never comes back. Newest first.

| Date | Mistake | Fix |
|---|---|---|
| 13 Nov 2026 | Hook scene skipped on 2 reels again: "Haan@yes." and "Nahi@no." (marker word with punctuation glued) | Before every render push: `grep -nE '@[a-z]+[.,?!]' studio/public/<folder>/script.txt` must print nothing |
| 13 Nov 2026 | Private-repo Actions minutes ran out at 12:04 IST; every job failed in 2 s with no logs, ~4 h lost | Repo made public (Actions free, secrets stay hidden). Scenes-only re-renders can run in the cloud container (README) |
| 13 Nov 2026 | Re-pushed make.txt with the same line, so it wasn't in the commit diff and no render started (~25 min lost) | Add a changing comment line (e.g. `# v2 <reason>`) to make.txt, or use workflow_dispatch with `names` |
| 13 Nov 2026 | Ready reels sat unscheduled for hours waiting for Ayush's typed schedule line; the 13:30 slot was missed | Send each reel with its exact schedule line as soon as it passes gate 4, and propose slots that are still at least 1 h away |
| 10 Nov 2026 | Counter showed "₹1,248" for crop fires and "₹160" for runs: the counter adds ₹ unless told not to | Set `"prefix": ""` on every non-money counter |
| 10 Nov 2026 | 4 of 5 voices failed the number check: dense number lists ("309 par 7", "GPT 43, Gemini 41") and Whisper small looping on a window | Speak fewer numbers per line, put extra figures on screen only; make-day now re-listens with Whisper medium when small fails |
| 10 Nov 2026 | Un-blurred wide title card got cropped to "le Fable 5 / and Myth" on 9:16 | Keep `fit: "blur"` for wide graphics with text |
| 10 Nov 2026 | `youtube.md` left uncommitted when the Mac session needed it | Commit titles/descriptions before starting the Mac session |
| 10 Nov 2026 | Chrome upload tool refuses files over 10 MB | Mac re-encodes to ~9.2 MB copies in `./doubt-clear/small/` (originals kept) |
| 9 Nov 2026 | Generic Mixkit stock didn't match the line; shake/flash felt harsh (Ayush) | Real photos/clips of each line's subject via `visuals.yml`; slow zoom + 0.4 s crossfades |
| 9 Nov 2026 | Word captions covered the visual (Ayush) | Captions off; beat text sits low; gold progress bar |
| 9 Nov 2026 | First render failed: API key secrets missing | Keys added as repo secrets (Gemini key as GOOGLE_API_KEY) |

## Carried over from Chunav Diary (never repeat)
Wrong-accent voice; voice saying a foreign currency word; text on flat colour cards; blurred frame 1; cuts too fast or out of sync;
stock footage with foreign money; giving the whole answer in second 1; big "get rich"-style hooks.
