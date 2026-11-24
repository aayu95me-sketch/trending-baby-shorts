<!-- raw reply, unedited. model: openai/gpt-oss-120b; 2026-11-24 01:25 UTC -->

**Audio‑clarity check (0‑11 s & 16‑21 s)**  
- I can’t actually “listen” to the file, so I can’t confirm every phoneme.  
- Run Whisper again with `--language hi` and **force‑align** the output (`--word_timestamps True`). Compare the generated timestamps with the script line‑by‑line. Any word that shows a confidence < 0.85 should be re‑recorded or manually edited in the TTS input.  
- Typical trouble spots in Hindi‑English mixes: “FSSAI” (often rendered as “F‑S‑S‑A‑I”), “PAH” (may be heard as “pah”), and the numeric “12 µg/L”. Insert commas or pause markers (`,`) around those tokens in the TTS markup to force a clear break.

**Verdict fairness**  
- The claim you’re stating is **“a single batch from the Goa plant, tested in September 2025, showed bromate 12 µg/L (limit 10 µg/L) and later a PAH flag.”**  
- That is **true** according to Business Standard, The Week and Reuters (via Daily Star).  
- You also say **“FSSAI has given permission to file a case.”** The FSSAI has *not* issued a formal “permission”; it has **registered a complaint** and is **investigating**. Phrase it as “FSSAI has opened an investigation / is considering legal action.”  
- Because the contamination is limited to one batch, the verdict must be **neutral**: “One batch showed excess bromate; the brand overall is not proven unsafe.” This avoids defamation and keeps the statement balanced.

**Blockers / Risks**  
1. **Defamation risk** – If you imply “Bisleri is unsafe overall,” you could be sued. Keep the wording batch‑specific.  
2. **Source attribution** – You must show the three sources somewhere (end‑screen overlay is fine). No need to repeat per‑frame credits.  
3. **Audio copyright** – Using the free TTS voice is fine; just ensure the generated audio is not mixed with any copyrighted background music.  
4. **Platform policy** – Both YouTube Shorts and Facebook Reels flag “health misinformation” aggressively. Include a **disclaimer**: “Information based on publicly reported tests; not a medical advice.”  

**Action items (free tools)**  
- Re‑run Whisper with word‑level timestamps → spot low‑confidence words.  
- Edit the TTS script: add commas around numbers, spell out “F‑S‑S‑A‑I” as “F‑S‑S‑A‑I” to force pauses.  
- Replace the “case‑chalane ki manzoori” line with “FSSAI ne jaanch shuru kar di hai.”  
- Add a 1‑second visual disclaimer at the end (Canva/Kapwing free).  

Once those three audio fixes and the wording tweak are applied, the reel will be clear, fact‑accurate and safe from legal/algorithmic blocks.
