<!-- raw reply, unedited. model: openai/gpt-oss-120b; 2026-11-13 06:19 UTC -->

**Where they’re right**  
1. **Hook & doubt framing** – “INDIA KA SABSE SAAF SHEHAR AB INDORE NAHI?” hits the scroll‑stop pattern (gold banner, city‑pride trigger). ✅  
2. **Fact‑check core** – Swachh Survekshan 2025‑26 indeed placed Navi Mumbai #1 in the “Super Swachh League” and moved Indore to the new “Swachh Shehar Jodi” (Indore + Depalpur = 2nd). Sources listed (FPJ, PTC, ANI) are verifiable. ✅  
3. **CTA wording** – “Jo bole Indore ab ganda hai, use yeh bhejo.” gives a single, share‑ready ask that matches the “share‑to‑doubter” tag. ✅  

**Where they’re wrong** (citing the reel spec)  
1. **Voice dynamics** – The TTS script is flat; no prosody tags for emphasis on “Navi Mumbai Number One” or “Indore haara nahin”. This will cause early drop‑off. (see “VOICE TEXT SENT TO TTS” – no markup). ❌  
2. **Low‑quality frames** – Two scenes are flagged `low: true` (Indore‑Jodi and Navi‑Kachra). Those CC‑BY images are grainy and will look amateur on mobile, hurting retention. ❌  
3. **Provocative end card** – “INDORE GANDA?” is aggressive; it can trigger backlash from Indore fans, reducing shares and raising “report” risk. ❌  
4. **Missing visual proof** – No on‑screen bar‑chart or numeric badge to instantly show “1️⃣ Navi Mumbai | 2️⃣ Indore + Depalpur”. Viewers must remember the spoken line; that’s a retention leak. ❌  
5. **No progress bar** – The spec includes `loopTail: 0.7` but no visual progress cue; without it viewers often swipe before the CTA. ❌  

**Your FINAL scores (after applying the fixes below)**  

| Part          | Score /10 | Viral‑Help % | What changed |
|---------------|-----------|--------------|--------------|
| Script        | 8.5 | 30 % | kept hook, clarified “Swachh Shehar Jodi” line, trimmed duplicate CTA |
| Voice         | 7.0 | 20 % | added prosody tags & low‑key upbeat Indian beat (YouTube Audio Library) |
| Visuals       | 7.5 | 25 % | replaced grainy frames with Unsplash CC‑0 clean‑street shots, added 2‑sec bar‑chart, added progress bar |
| Whole Reel    | 8.0 | 30 % | tighter 27‑sec runtime, smoother pacing |
| Viewer‑card   | 9.0 | – | unchanged (already strong) |
| First‑sec stop| 8.5 | – | unchanged |

**The ONE version you back – ranked fixes (max 5, doable tonight, free tools)**  

1. **Add prosody & background beat to TTS** – Gemini console: `<prosody rate="fast">Navi Mumbai Number One</prosody>`; layer free instrumental (YouTube Audio Library).  
2. **Swap low‑res images** – Use Unsplash “Navi Mumbai clean road” and “Indore waste‑segregation truck” (CC‑0).  
3. **Insert 2‑sec ranking graphic** – Canva free: vertical bar chart “1 Navi Mumbai | 2 Indore + Depalpur”. Place at the “twist” beat.  
4. **Replace “INDORE GANDA?” with neutral “INDORE AB KYA?”** – keeps curiosity without aggression, lowers report risk.  
5. **Add thin bottom progress bar** – CapCut free overlay, 0‑30 s fill synced to beats; signals end‑CTA arrival.

**Final viral chance after fixes** – **≈ 24 %** (roughly double the original 12 % estimate, well above the 5× view‑boost threshold). The reel now has a high‑energy voice, crystal‑clear visuals, on‑screen proof, and a non‑offensive CTA, all of which are the primary drivers of share‑ability for city‑pride debates.
