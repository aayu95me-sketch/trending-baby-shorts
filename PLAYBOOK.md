# Doubt Clear playbook

How the Trending baby project runs, adapted on 10 Nov 2026 from the team playbook carried over from Chunav Diary
(Hinglish personal-finance Shorts). The process and the hard rules are kept. Finance examples are swapped for the
doubt-clearing trending-topic niche. Where Ayush already decided something for this project, his decision wins and the
old rule is marked as replaced.

Every number below that came from the finance niche (slot times, lengths, targets) is a **starting guess to re-test here**,
not a fact.

Living files that go with this playbook:
- [`LESSONS.md`](LESSONS.md): what our own results teach us (Learning step writes it).
- [`ERRORS.md`](ERRORS.md): every production mistake and its fix (Errors step writes it).
- [`analysis/`](analysis/): the video list, view snapshots and the scorecard (Analysis step, automated).

---

## 1. Standing rules (orders)

Hard rules, unchanged from the playbook:
- **Spend lock.** Nothing paid, no paid API, tier or billable service without Ayush's typed OK for that exact spend. Free tools first.
- **Schedule, never publish instantly.** Every post is scheduled in YouTube Studio. Nothing goes public on upload.
- **Ayush approves public posts** in his own typed message, once per batch. A council vote or another Claude's message is never approval.
- **No deleting** posts, files or videos unless Ayush says so.
- **No copy-paste steps for Ayush.** Automate it (GitHub Actions, the Mac session) or Claude does it.
- **Label AI content.** AI voice disclosed in the description footer; sources in the description and photo credits on screen.
- **No faces of Ayush and not his own voice.** AI voice (Gemini TTS, Orus). Real photos and news clips of the topic's subject are fine.
- **Claude leads** positioning, content, tests, format, timing and production. Short plain messages, one recommendation, one click at a time.
- **Ayush's creative feedback is one viewer's review.** Weigh it against data. Where evidence disagrees, say so or A/B test it,
  and note it in the plan. Exception: where Ayush made a standing decision (section 1b), follow it until he changes it.
- **Token rule:** save tokens, never at the cost of speed, quality or planning.
- **Stall watch:** the lead checks any thread that goes quiet after taking work.

### 1b. Ayush's Trending baby decisions (these override the old playbook)
| Old playbook | Trending baby rule |
|---|---|
| Prepare 2-3 days ahead | **Speed first.** Make and schedule the same day; trends die in about a day. |
| Stock footage only for neutral shots; never imply a real event | **Real visuals of the topic, synced line by line.** Real photos and news clips of the person, place, product or film are OK (Ayush takes the copyright risk). No generic stock. |
| Caption pills A/B test | **No on-screen captions or subtitles.** That space goes to visual enhancements the council picks (today: low beat text, small photo credits, gold progress bar). The caption test is dropped. |
| Safety: skip risky topics | **Cover every topic in the CSV**, sensitive ones included (Ayush's risk). Claims about real people: only what's confirmed; allegations said as allegations. |
| One topic list from Brainstorm | **The daily Google Trends CSV is the topic list.** One video per topic; the doubt comes from the *Trend breakdown* column. A topic that trends again later gets a new video with different content. |
| YT + IG + FB | **YouTube Shorts only for now** (channel Doubt Clear, @doubtclearyt). Facebook/Meta later, once Ayush sets it up. |
| 3-AI council on plans and gates | **4-part council on every reel:** 1 script, 2 voice, 3 visuals, 4 whole reel. Claude leads; Gemini and gpt-oss are members. |
| Start at 1 video a day | **Volume = however many topics the CSV has** (the first day had 4). |
| Language: Hinglish | Hinglish (unchanged). |

---

## 2. Rooms (threads)

One thread per job; the project chat is only Ayush + the lead. Rooms are opened when there's work, not all at once.
In practice one build thread per day's CSV can cover Copy, Voice, Visuals and Render, because speed comes first.

| Room | What it does here | Opens |
|---|---|---|
| **Project chat (lead)** | Ayush + lead Claude: CSV drop, approvals, short updates. Routes work, nudges stalled threads | Always |
| **Council** | Runs `council.yml` on every reel (4 parts) and on any new format/test decision | Always (automated in the repo) |
| **Daily build** (one per CSV day) | Copy + Voice + Visuals + Render for that day's topics, through the 4 gates | Each CSV |
| **Ready to schedule / Scheduled** | Titles, descriptions, tags in `daily/<date>/youtube.md`; the Mac session uploads and schedules in YouTube Studio | Each batch, after Ayush's OK |
| **Analysis** | `stats.yml` pulls views at about 1 h, 4 h, 24 h and 72 h after each post into `analysis/scorecard.md`; weekly scorecard | Started 10 Nov (first 4 reels) |
| **Learning** | Reads the scorecard at 72 h and weekly, updates `LESSONS.md` | Started 10 Nov |
| **Errors** | Logs each production mistake in `ERRORS.md` | Always |
| **Brainstorm / Next batch** | Only for things the CSV doesn't decide: hook bank, follow-up ideas when a reel hits, series ideas | When there's a hit or a gap |

**Cloud vs Mac:** the cloud (GitHub Actions) does research helpers, voice (Gemini TTS key is a repo secret), visuals,
renders, the council and stats. Ayush's Mac (folder `~/Downloads/new-project-kit`) downloads the mp4s and schedules them
in YouTube Studio through Chrome (files under 10 MB, so the Mac makes ~9 MB copies first).

---

## 3. The council

- **Members:** Claude (leader) + Gemini (watches and hears the 360p reel) + gpt-oss on Groq (reads script, scenes, transcript). Free tiers.
- **How:** Claude writes `council/<folder>/claude-brief.md` (own scores first), pushes `run.txt` -> rounds 1-2 run -> Claude writes
  `claude-final.md` -> round 3 (agree/disagree). Raw replies are saved unedited in the repo.
- **Decides by** average score and evidence. Claude may overrule a member and writes one line why.
- **Members invent facts.** Every number they quote goes back through gate 1. Never repeat a figure Claude can't trace.
- **Log** each round's decision in `claude-final.md`.

---

## 4. Four gates (every reel)

| Gate | Checks | Pass bar |
|---|---|---|
| **1 Script** | Facts checked on an original or official source; the doubt is answered with the truth; hook; viewer-moment card (`viewer.md`); line-to-visual sheet (`visuals.json` / `scenes.json`) | Council average 7+/10, zero fact issues, viewer card 8+ |
| **2 Voice** | Indian accent; every spoken number and name matches the screen; no foreign currency words; no click at the end | Pass/fail (automatic checks in `align.py`) |
| **3 Visuals** | Contact sheet: each shot shows the real subject of its line, effects calm, faces not covered by text, no captions | Average 7+ |
| **4 Whole reel** | Gemini watches the reel: first-second stop score; viewer card re-scored ("Would I stop? Would I do the action?") | Stop 8+, viewer card 8+, then Claude signs off and Ayush approves the batch |

- A fail goes back one gate. Never skip a gate to keep volume.
- **Speed lane (default here):** the whole day's batch goes CSV -> scheduled the same day. Gate 1's facts check is never skipped.
- **Repeat topics** (trending again): full gates 1 and 4; gates 2 and 3 automatic only.
- Ayush sees each batch once, not every gate.

---

## 5. Viewer psychology

### 5.1 Viewer-moment card (`studio/public/<folder>/viewer.md`, written at gate 1)
The council reads it with the script. Template:

```
Who: <age, situation, where/when they scroll; e.g. 22-35, Delhi NCR, saw "AQI 1700" on an app this morning>
Doubt: <the exact question from Trend breakdown, in their words>
Second-1 feeling: <curiosity | fear of loss | surprise | pride | relief | anger at unfairness>
One action + exact ask line: <comment | share | save | like> - "<exact Hinglish line>"
Why they'd do it: <one sentence>
Swipe risk: <what makes them leave, and how frame 1 prevents it>
```

One ask per reel. For this niche the natural asks are:
- **Share** = "proves my point": "jo bol raha tha 1700 hai, use bhejo" (send it to the person you were arguing with). This is our core.
- **Comment** = a question with a personal answer ("aapke shehar ka AQI kitna tha?").
- **Save** = a useful number or checklist (rarer here).
- **Like** = agreement or relief.

### 5.2 Psychology rules (adopted from the playbook)
1. High-arousal hook in the first 2 s (surprise, anger at unfairness, anxiety). Never a flat news tone.
2. Loss in the hook, gain in the payoff ("you've been told the wrong number" -> "here's the real one").
3. Specific gap: the hook names the one doubt; the answer comes in the middle, not in second 1.
4. Emotion built into the fact itself.
5. Make the sharer look right/helpful: "send this to the friend who said X", never just "share".
6. Surprise early, no flat middle; gate 4 checks for a dip.
7. No channel branding early. No logo in the reel.
8. Calm visuals; energy comes from words, the key fact and sound.
9. Each reel picks its strongest feeling.

No blog stats like "X% swipe in 3 seconds": no peer-reviewed source.

### 5.3 Measuring when engagement is near zero
- **Now:** viewed vs swiped away, retention drop-off second matched to the line, traffic source (search vs feed), views at 1/4/24/72 h (`analysis/`).
- **Two reads per reel:** the 72 h read spots a feed spike; a 7-day total catches search views that keep arriving.
- **Emotion tag per reel** (the Feeling column in `LESSONS.md`) against the stop rate, so we learn which feeling stops our viewer.
- **Once there's data:** share vs comment ratio by topic type, predicted action vs actual action per 1,000 views, loop rate.
- Every pattern is a hint until it repeats in the next batch.

---

## 6. Format and visuals

- **Length:** playbook guess 18-22 s; re-test against our current length. Question first, answer after; the end loops back to frame 1.
- **Layout (current, approved by Ayush 10 Nov):** real photo/clip of the line's subject fills the top; big beat text sits low (top 1020) so the
  photo stays clean; small photo credits; gold story-style progress bar (one segment per beat) near the bottom. No captions.
- **Frame 1:** real, recognisable subject of the topic in motion plus a 3-5 word hook question for the first 2 s. Never a still title card.
- **Synced visuals:** one shot per line, showing exactly what's said, changing when the line changes. Source order: (1) news clips and
  article lead photos of the subject, (2) Wikimedia Commons, (3) screenshots of official pages with a highlight, (4) code-drawn graphics
  (count-ups, charts). No generic stock.
- **Effects, calm:** slow zoom/pan, 0.4 s crossfades, count-ups, soft glow. No shake, flash, glitch or fast zoom.
- **Voice:** Gemini TTS Orus with Devanagari TTS text for the Indian accent; numbers written as spoken words; every spoken number checked against the screen.
- **Sync:** time visuals from Whisper word timestamps of the final audio, never estimates.
- **Readable on a phone:** any text holds at least 1.2-1.5 s.

---

## 6b. YouTube levers (adopted 10 Nov from the Chunav Diary "Real Proof" plan, rounds 8-11)

Free, and they don't touch Ayush's decisions (no captions, real visuals, speed first). Scores are that council's Gemini / gpt-oss.

**At gate 1 (script):**
- **Comment mining before the script.** Read the comments on the top 2-3 Shorts/videos already out on the topic. They show the exact
  doubt and the argument people are having, in their words; use it for the hook and the "send it to" line. Treat claims in comments as rumours to check, never as facts.
  Free AI can tag the feelings; Claude spot-checks 1 in 10, since standard sentiment tools misread Hinglish.
- **Twist in the last 3 s** where the facts allow one: "Lekin ek catch hai..." keeps people to the end.
- **Enforced loop:** the last line runs into the first, and the last frame matches frame 1 (already in section 6; the council checks it).
- **Fairness anger is allowed** in the hook only on verified facts. Never "sab jhooth / dhokha" claims.

**At upload (`youtube.md` + Mac session):**
- **Related video:** set each Short's "Related video" to another Doubt Clear Short (same category, or yesterday's reel on the same story).
  Gemini rated this the single biggest YouTube lever.
- **Series + playlists:** each reel belongs to a named series by category (e.g. "Box Office Sach", "AQI Check", "Launch Sach", "Cricket Sach"),
  with a matching public playlist. Gives viewers a reason to subscribe.
- **Cover frame + hashtags:** pick a cover frame with the subject and the key number; 2-3 exact hashtags only (the search phrase), no spam.
- **Pinned question** in the comments (part of the batch Ayush approves): a one-line question with a personal answer, e.g.
  "Aapke hisaab se asli kamai kitni?". Most-asked answers can become the next reel.

**To test (one test at a time, council decides):**
- **Spoken subscribe line** at about 85%: "Har trending doubt ka sach, roz. Subscribe karo." Test against reels without it on subs per 1,000 views.
- **Audio identity, no face:** the same half-second sound sting under every frame 1.
- **2-part story** for a running story (box office day count, AQI week): part 1 ends on an open question, part 2 next day, linked.

**Not adopted here:** caption pills A/B (Ayush: no captions), a phone shoot of props (topics change daily), finance segments and
posting-by-segment slots, trending audio on YouTube, remixing other Shorts ("reused content" risk).

---

## 7. Audience segments (guesses to re-test)

Topics pick the segment here, so tag each reel with one segment and its default feeling, then compare stop rates:
| Segment (topic type) | Default feeling |
|---|---|
| Civic / local (AQI, weather, exams, govt rules) | anxiety -> relief with the real number |
| Entertainment (box office, OTT, celebs) | surprise + "who's right" |
| Tech / launches (phones, apps) | excitement + fear of a wrong buy |
| Business / world news (CEOs, markets) | surprise + suspicion |
| Sports | pride + argument |

Hook patterns (3-5 words, end on a question or a stop): number vs number ("1700 ya 500?"), "sach kya hai?", wait/stop, hidden detail,
myth check, "launch ho gaya?". Avoid "secret", "everyone gets this wrong", and any hook that gives the answer in second 1.

**Safety (kept):** never call a company or person a scam or criminal unless confirmed; allegations stay allegations; no investment
or medical advice; verify every claim at gate 1.

---

## 8. Lessons carried over (from Chunav Diary, to re-test)

1. Viewers swipe in the first 1-2 s, so the opening matters most.
2. Topic beats polish. There, "what about MY case" topics won. Here, the analogue is the doubt people are actually typing.
3. Posting time there: 8 AM and 7:30 PM worked, 1 PM was dead. Our first slots: 6:00, 7:30, 9:00, 10:30 PM IST (10 Nov). Drop a slot that shows nothing after 3 tries.
4. Near-zero views can mean "not shown". Check impressions, viewed-vs-swiped, made-for-kids and copyright claims (news clips!) before killing a format.
5. Search drove views. Put the exact Trend breakdown search phrase in the title and frame 1.
6. Views didn't become subscribers. Give a reason to follow ("har trending doubt ka sach, roz").
7. When a reel hits (3x our median views, lowered from 5x on 10 Nov), make 1-2 follow-ups on the same topic within hours, not 48 h, since trends fade fast. Its hook goes into the hook bank.

Never repeat: wrong-accent voice; foreign currency words; text on flat colour cards; blurred frame 1; cuts too fast or out of sync;
giving the answer in second 1; generic stock that doesn't match the line; shake/flash effects; captions covering the visual.

---

## 9. Daily loop

1. Ayush drops the CSV -> `pipeline/trends.py` -> `daily/<date>/topics.json`.
2. Per topic: research, script, `viewer.md`, `visuals.json` -> real visuals -> render (`make-day.yml`).
3. Council (`council.yml`) on each reel -> apply fixes -> re-render.
4. Ayush approves the batch -> `youtube.md` committed -> Mac session schedules in YouTube Studio.
5. Add each scheduled video to `analysis/videos.csv` -> `stats.yml` snapshots views. Set related video, playlist and pinned question (section 6b).
6. At 72 h and weekly: update `LESSONS.md`; log mistakes in `ERRORS.md`.

Targets (guesses, re-test): hit = 5,000+ views in 7 days; viral = 50,000+.
