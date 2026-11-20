<!-- raw reply, unedited. model: openai/gpt-oss-120b; 2026-11-20 17:12 UTC -->

**WHERE THEY ARE RIGHT**

*Claude’s brief* – correctly identified the core hook (“1977 ka yaan, hello bolo → 2 din baad jawab”) and the fact‑check: NASA did announce on 17‑18 Nov 2026 that Voyager 1 is ≈ 1 light‑day (≈ 25.9 bn km) from Earth, so a one‑way signal takes ~24 h. All dates, distances and power‑down info are verifiable (NASA press‑release, EarthSky, Wikipedia).  

*Assistant (Round 1)* – gave realistic scores, flagged the blurred‑out NASA images, noted the flat TTS and the late‑placed CTA, and correctly estimated the current viral‑chance (~22 %). Those are the biggest retention killers.  

*Gemini (Round 1)* – praised the visuals and voice, but those claims clash with the supplied asset list (all images are marked “blur”). The “no‑blur” assumption is false → over‑optimistic scores.

**WHERE THEY ARE WRONG**

| Reviewer | Mistake | Reel Evidence |
|----------|---------|----------------|
| Claude | Over‑states “outside the main lanes” as a strength; the space lane already has decent baseline interest (≈ 42 views) so it’s not a hidden gem. | CSV shows “space” median 42 views – modest, not a breakout. |
| Gemini | Claims “real NASA photos, no text covering key detail”; the script’s scene table shows every frame uses a blurred background with large overlay text that hides details. | `fit":"blur"` in every scene definition. |
| Gemini | Gives a 38 % viral chance without accounting for the first‑second hook weakness; the hook line is 4 seconds long and competes with fast‑scroll Shorts. | Hook appears at `at:0` but no visual punch until 1 s later. |
| Assistant (Round 1) | Rated the script 8 /10 despite a slightly clunky “power kam” line that could be tighter. | Script line “Par power bijli kam ho rahi hai…” is wordy for a 0.8 s beat. |

**YOUR FINAL SCORES (after applying the five fixes below)**  

| Part | Score /10 | Viral‑Help % | What changed |
|------|-----------|--------------|--------------|
| Script | **8.5** | **30 %** | Tightened “power” line, moved CTA earlier, added micro‑emphasis tags in SSML. |
| Voice | **7.5** | **15 %** | Added SSML prosody for emphasis on “ONE LIGHT DAY” and “SACH?”, slight pitch raise on CTA. |
| Visuals | **8.0** | **20 %** | Replaced blurred assets with crisp NASA public‑domain images, added subtle vignette, kept text legible. |
| Whole Reel (stop‑score) | **8.2** | **25 %** | Early CTA, progress bar, light‑pulse animation for “7 + chakkar”. |
| **Overall Viral Chance** | **≈ 48 %** |  | Combined effect of all fixes. |

**THE ONE VERSION YOU BACK – Ranked Fixes (max 5, all free, doable tonight)**  

1. **Swap blurred assets for sharp NASA/JPL public‑domain photos** (NASA Image Library, CC0). Keep a thin vignette only if needed – preserves detail for the “≈ 26 arab km” claim.  
2. **Insert a bottom‑aligned progress bar (0 → 100 %)** that advances each beat; this visual cue dramatically reduces scroll‑away in the first 3 seconds.  
3. **Move CTA to the “power” beat (≈ 2 s earlier)** and overlay a bright, pulsing “Tag your late‑reply friend 👇” bubble; keep the final frame as a quick recap only.  
4. **Add SSML emphasis** (`<prosody rate="+10%" pitch="+5%">ONE LIGHT DAY</prosody>`) on the key fact and a slight pause before “SACH?” to create a pattern‑interrupt.  
5. **Add a 0.8 s light‑pulse animation** circling Earth when saying “roshni … 7 + chakkar” to visualise “light‑day” instantly for a non‑technical audience.

**FINAL VIRAL CHANCE AFTER FIXES** – **≈ 48 %**. This puts the reel in the “high‑share” bracket for the 15‑35 yr Indian Shorts audience: clear truth, visual punch, early share‑bait, and a snappy script that can be produced tonight with zero budget.
