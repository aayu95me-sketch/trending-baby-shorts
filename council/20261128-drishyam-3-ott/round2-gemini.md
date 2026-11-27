<!-- raw reply, unedited. model: gemini-3.5-flash; 2026-11-27 16:57 UTC -->

GOAL: "Make the Doubt Clear accounts (YouTube Shorts + Facebook Reels, India, Hinglish) go viral."

## Where they are right
* **GPT-OSS** correctly notes that burning in accurate Hindi captions and keeping text out of face zones is essential for sound-off scrollers on reels.
* **Gemini** correctly spots that replacing generic news cutouts at `at: date` with a direct, recognizable Netflix UI screenshot builds instant visual credibility.

## Where they are wrong (cite the reel)
* **GPT-OSS** fails the script for an "unverified claim" regarding *3rd biggest Hindi film of 2026*. The Sacnilk source explicitly confirms this ranking (behind *Ramayana* and *Toxic*). Penalizing verified Sacnilk data to crash the baseline score to 5% is a false failure.
* **Gemini** proposes replacing the CTA with *"Yeh video doston ko bhejo..."*, which breaks the clean 28-second timeline and removes the high-converting binary comment prompt (`at: cta`: *"Theatre mein dekhi ya ab Netflix pe dekhoge?"*).

## Your FINAL scores

| Part | Score /10 | Viral-Help % | Reason for Change |
| :--- | :---: | :---: | :--- |
| **1. Script** | 8.5 | 75% | Unchanged. Hits search doubt instantly with verified Sacnilk numbers. |
| **2. Voice** | 8.0 | 70% | Maintained. Numbers (`ikyaasi`, `navaasi`) are correct in Devanagari TTS. |
| **3. Visuals** | 7.5 | 65% | Adjusted -0.5: Needs native Netflix UI insert at frame 2 and clean lower-third margins. |
| **4. Whole Reel** | 8.0 | 72% | Strong baseline targeting a 5K+ high-intent search trend in MH/India. |

## The ONE version you back: the ranked fixes (max 5)

1. **Audio QC Check:** Verify the exported TTS audio for `teen sau ikyaasi` (381) and `paanch sau navaasi` (589) to guarantee zero Whisper artifacting/glitching.
2. **Netflix UI Asset at Beat 2:** Replace `news-5.jpg` at `at: date` with a real Netflix interface screenshot showing *Drishyam 3* on the home carousel.
3. **Burn-in Subtitles:** Add central Hindi captions matching the TTS transcript for sound-off feed retention.
4. **Lower-Third Text Placement:** Shift text overlay tags (`DRISHYAM 3 · HIT YA FLOP?`, `₹381 CR`) strictly into the bottom 30% to avoid covering Ajay Devgn's eyes/face.
5. **Keep Original CTA:** Retain *"Theatre mein dekhi ya ab Netflix pe dekhoge? Comment karo"* to trigger direct comment-section debate.

## Final viral chance after fixes: 82%
