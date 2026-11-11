# Production errors log

Every mistake and its fix, so it never comes back. Newest first.

| Date | Mistake | Fix |
|---|---|---|
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
