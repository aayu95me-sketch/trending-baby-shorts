<!-- raw reply, unedited. model: gemini-3.5-flash; 2026-11-20 17:12 UTC -->

GOAL: "Make the Doubt Clear accounts (YouTube Shorts + Facebook Reels, India, Hinglish) go viral."

## Where they are right
* **GPT-OSS on Visual Blur:** Relying on `"fit": "blur"` for 16:9 NASA assets degrades visual quality on 9:16 mobile screens, making the reel look low-effort. Sharp central crops with dark gradient vignettes look far more professional.
* **TTS Pacing & Monotone Risk:** Gemini TTS (Orus) can flatten key numbers like "26 arab km" and questions like "Sach?". Adding SSML tags or specific punctuation pauses prevents flat delivery.

## Where they are wrong
* **Moving CTA to the "Power" beat (GPT-OSS Fix 3):** Splitting the viewer's focus by showing "Tag a friend" while explaining that NASA is turning off instruments ruins the story peak. The CTA belongs cleanly at `@cta`.
* **Cutting "Insaan ki sabse door ki cheez" (GPT-OSS Fix 5):** Dropping this phrase removes the emotional scale for non-science viewers. "26 arab km" is just an abstract number; "farthest human-made object" creates the awe.

## Your FINAL scores

| Part | Score /10 | Viral-Help % | One-Line Reason |
| :--- | :---: | :---: | :--- |
| **1. Script** | 8.5 | 40% | High-retention narrative math (1 day out + 1 day back = 2 day reply) paired with a relatable share trigger. |
| **2. Voice** | 7.5 | 20% | *Adjusted down 0.5:* Raw Orus output needs pitch/rate tweaking to avoid flattening dramatic numbers. |
| **3. Visuals** | 7.2 | 15% | *Adjusted down 0.8:* Blurred background fills weaken real NASA asset impact on mobile. |
| **4. Whole Reel** | 7.8 | 25% | Great curiosity topic, but needs crisp framing and voice modulation to lock 70%+ retention. |

*Changes made:* Lowered Visuals (8.0 → 7.2) and Voice (8.0 → 7.5) after validating GPT-OSS's critique on frame blur and TTS monotone tendencies.

---

## The ONE version you back: the ranked fixes (max 5)

1. **Fix Image Framing (Remove Blur):** Replace `"fit": "blur"` with sharp 9:16 center-cropped NASA photos using a subtle bottom dark gradient.
2. **SSML Energy Boost for TTS:** Apply `<prosody pitch="+5%" rate="+3%">` on "Sach?", "26 arab km", and "Tag karo" to enforce natural emphasis.
3. **Space Radio Telemetry FX at 0:00:** Add a subtle 0.4s satellite beep/static overlay in the first frame for immediate audio pattern interrupt.
4. **Light-Speed Visual Overlay at `@mean`:** Insert a quick 1-second light-streak overlay over the Earth graphic to visualize "7+ turns per second".
5. **High-Contrast CTA Banner at `@cta`:** Shift `@cta` text color to high-contrast neon yellow with a subtle pulse to draw immediate eyes to the comment/share action.

---

## Final viral chance after fixes: 64%
