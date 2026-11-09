// Doubt Clear Short: one trending topic, one doubt, one true answer with the source on screen.
// Built from Chunav Diary's "Paisa ka Sach" template: real footage or a real headline screenshot under every beat,
// a jump cut every ~0.9 s, a flash + impact on scene changes, 1-3 word captions synced to the voice, a save card, a loop tail.
// Scenes live in public/<dir>/scenes.json, timing in timeline.json. Render with --props='{"dir":"<dir>"}'.
//
// scene: { at: cue|seconds, video?: "footage/x.mp4", videos?: [...] (montage), img?: "broll/x.jpg",
//          big?: "SACH KYA HAI?", color?: "gold"|"red"|"green"|"white", tag?: "CPCB DATA",
//          counter?: { from: 0, to: 368, label: "AQI 368" }, shake?: true, note?: "SOURCE: ..." }
import React from "react";
import { AbsoluteFill, CalculateMetadataFunction, Composition, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Audio, Video } from "@remotion/media";
import { DISPLAY, FPS, GOLD, GREEN, RED, useT } from "./Kit";

type W = { w: string; start: number; end: number };
type Counter = { from: number; to: number; label?: string; prefix?: string; suffix?: string };
type Headline = { source: string; title: string; date?: string };
type Scene = { at: string | number; video?: string; videos?: string[]; img?: string; big?: string; color?: string; tag?: string; counter?: Counter; shake?: boolean; note?: string; headline?: Headline; bars?: [string, number][]; barUnit?: string };
type Save = { title: string; lines: string[][]; footer?: string };
type Spec = { mascot?: boolean; note?: string; banner?: string; loopTail?: number; save?: Save; scenes: Scene[] };
type TL = { total: number; cues: Record<string, number>; words: W[]; caps?: string[][] | null; saveAt?: number };
type Props = { dir: string; tl: TL | null; spec: Spec | null };

const COLORS: Record<string, string> = { gold: GOLD, red: RED, green: GREEN, white: "#fff" };
const fontCss = `@font-face{font-family:Anton;src:url(${staticFile("fonts/Anton.ttf")}) format("truetype");}@font-face{font-family:Baloo;font-weight:800;src:url(${staticFile("fonts/Baloo2-ExtraBold.ttf")}) format("truetype");}`;
const HINDI = "Baloo, Anton, sans-serif";
const BLUE = "#4db8ff";
const stroke: React.CSSProperties = { WebkitTextStroke: "14px #000", paintOrder: "stroke fill", textShadow: "0 10px 0 #000" };
const JUMP = 0.9; // jump cut (crop change) inside a shot
const SAVE = 1.6; // seconds the save card stays

const inr = (n: number) => {
  const s = Math.round(n).toString();
  if (s.length <= 3) return s;
  const last3 = s.slice(-3); const rest = s.slice(0, -3);
  return rest.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + "," + last3;
};

// One moving shot: real footage, punched-in crops that jump every 0.9 s (alternating framing), slight push.
const Shot: React.FC<{ src?: string; img?: string; from: number; to: number; i: number }> = ({ src, img, from, to, i }) => {
  const t = useT();
  const k = interpolate(t, [from, to], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const j = Math.floor(Math.max(0, t - from) / JUMP);
  const crops = [[1.0, "50% 50%"], [1.22, "35% 40%"], [1.12, "65% 55%"], [1.3, "50% 35%"]] as const;
  const [z, o] = crops[(j + i) % crops.length];
  const style: React.CSSProperties = { width: "100%", height: "100%", objectFit: "cover", transformOrigin: o, transform: `scale(${(z + 0.06 * k) * 1.02})` };
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      {src ? <Video src={staticFile(src)} muted style={style} /> : img ? <Img src={staticFile(img)} style={style} /> : null}
    </AbsoluteFill>
  );
};

const Big: React.FC<{ s: Scene; at: number }> = ({ s, at }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const p = spring({ frame: f - Math.round(at * fps), fps, config: { damping: 8, mass: 0.5 } });
  const c = COLORS[s.color ?? "gold"] ?? GOLD;
  const big = s.big ?? "";
  const size = big.length <= 6 ? 230 : big.length <= 10 ? 180 : 140;
  return (
    <div style={{ position: "absolute", top: 380, width: "100%", display: "flex", flexDirection: "column", alignItems: "center", gap: 20, padding: "0 50px", boxSizing: "border-box", textAlign: "center" }}>
      {s.tag && <div style={{ fontFamily: DISPLAY, fontSize: 70, color: "#000", background: GOLD, borderRadius: 16, padding: "4px 28px", transform: `scale(${Math.min(1, p)}) rotate(-3deg)` }}>{s.tag}</div>}
      {big && /[\d₹]/.test(big) && p < 0.98 && [0.55, 0.3].map((g, gi) => (
        <div key={gi} style={{ position: "absolute", top: s.tag ? 110 : 0, fontFamily: DISPLAY, fontSize: size, color: c, opacity: g * (1 - p), lineHeight: 0.95,
          transform: `scale(${(4 - 3 * Math.min(1, p)) * (1 + 0.35 * (gi + 1) * (1 - p))}) rotate(${-18 * (1 - p)}deg)`, filter: "blur(6px)" }}>{big}</div>))}
      {big && <div style={{ fontFamily: DISPLAY, fontSize: size, color: c, lineHeight: 0.95, transform: /[\d₹]/.test(big) ? `scale(${4 - 3 * Math.min(1.08, p)}) rotate(${-18 * Math.max(0, 1 - p)}deg)` : `scale(${1.8 - 0.8 * Math.min(1.1, p)})`, opacity: Math.min(1, p * 2), ...stroke, textShadow: `0 10px 0 #000, 0 0 60px ${c}aa` }}>{big}</div>}
    </div>
  );
};

// The maths beat: the rupee figure melts down in front of the viewer, then the rounded result slams in.
const Melt: React.FC<{ c: Counter; from: number; to: number; tag?: string }> = ({ c, from, to, tag }) => {
  const t = useT(); const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const runEnd = from + Math.min(1.0, (to - from) * 0.5);
  const k = interpolate(t, [from + 0.15, runEnd], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) });
  const v = c.from + (c.to - c.from) * k;
  const done = t >= runEnd;
  const shake = !done && k > 0 ? Math.sin(f * 2.3) * 6 : 0;
  const p = spring({ frame: f - Math.round(runEnd * fps), fps, config: { damping: 8, mass: 0.5 } });
  const red = interpolate(k, [0, 1], [0, 1]);
  const col = `rgb(255, ${Math.round(255 - 178 * red)}, ${Math.round(255 - 178 * red)})`;
  return (
    <div style={{ position: "absolute", top: 380, width: "100%", display: "flex", flexDirection: "column", alignItems: "center", gap: 26 }}>
      {tag && <div style={{ fontFamily: DISPLAY, fontSize: 80, color: "#000", background: GOLD, borderRadius: 16, padding: "4px 30px", transform: "rotate(-3deg)" }}>{tag}</div>}
      <div style={{ fontFamily: DISPLAY, fontSize: 150, color: col, transform: `translateX(${shake}px)`, ...stroke, textShadow: `0 10px 0 #000, 0 0 50px ${col}88` }}>{c.prefix ?? "₹"}{inr(v)}{c.suffix ?? ""}</div>
      {c.label && done && <div style={{ fontFamily: DISPLAY, fontSize: 120, color: GOLD, transform: `scale(${1.6 - 0.6 * Math.min(1.1, p)})`, ...stroke }}>{c.label}</div>}
    </div>
  );
};

// A news headline card we draw ourselves (source + headline + date): real attribution, never a blocked page.
const HeadlineCard: React.FC<{ h: Headline; at: number; tag?: string }> = ({ h, at, tag }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const p = spring({ frame: f - Math.round(at * fps), fps, config: { damping: 12, mass: 0.6 } });
  return (
    <div style={{ position: "absolute", top: 300, left: 70, right: 70, transform: `translateY(${(1 - p) * 300}px) rotate(${(1 - p) * -5 - 1.5}deg)`, opacity: Math.min(1, p * 2) }}>
      {tag && <div style={{ fontFamily: DISPLAY, fontSize: 64, color: "#000", background: GOLD, borderRadius: 14, padding: "2px 24px", display: "inline-block", marginBottom: 18 }}>{tag}</div>}
      <div style={{ background: "#fff", borderRadius: 28, padding: "30px 36px", boxShadow: "0 30px 80px #000c", borderLeft: `16px solid ${RED}` }}>
        <div style={{ fontFamily: DISPLAY, fontSize: 40, letterSpacing: 2, color: RED }}>{h.source.toUpperCase()}{h.date ? ` · ${h.date.toUpperCase()}` : ""}</div>
        <div style={{ fontFamily: "Georgia, serif", fontWeight: 700, fontSize: 58, lineHeight: 1.18, color: "#111", marginTop: 12 }}>{h.title}</div>
      </div>
    </div>
  );
};

// Day-by-day bars that grow one after another (stat cards get saved).
const Bars: React.FC<{ bars: [string, number][]; unit?: string; at: number; tag?: string }> = ({ bars, unit, at, tag }) => {
  const t = useT();
  const max = Math.max(...bars.map((b) => b[1]));
  return (
    <div style={{ position: "absolute", top: 330, left: 80, right: 80 }}>
      {tag && <div style={{ fontFamily: DISPLAY, fontSize: 64, color: "#000", background: GOLD, borderRadius: 14, padding: "2px 24px", display: "inline-block", marginBottom: 24 }}>{tag}</div>}
      <div style={{ background: "#000b", borderRadius: 28, padding: "26px 30px" }}>
        {bars.map(([label, v], i) => {
          const k = interpolate(t, [at + 0.12 * i, at + 0.12 * i + 0.4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const top = v === max;
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 18, margin: "12px 0" }}>
              <div style={{ width: 150, fontFamily: DISPLAY, fontSize: 46, color: "#fff" }}>{label}</div>
              <div style={{ flex: 1 }}><div style={{ width: `${(v / max) * 100 * k}%`, height: 64, borderRadius: 12, background: top ? GREEN : GOLD }} /></div>
              <div style={{ width: 170, textAlign: "right", fontFamily: DISPLAY, fontSize: 48, color: top ? GREEN : "#fff", opacity: k }}>{v}{unit ?? ""}</div>
            </div>);
        })}
      </div>
    </div>
  );
};

// One or two words at a time, exactly while spoken; numbers and money words in yellow. Centre of the screen.
const KEY = /\d|₹|%|LAKH|CRORE|SACH|JHOOTH|FAKE|TRUE|AQI|NAHI|HAAN/i;
const Captions: React.FC<{ words: W[] }> = ({ words: raw }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig(); const t = f / fps;
  const words = raw.map((w) => ({ ...w, w: w.w.replace(/^[^\p{L}\p{N}₹]+|[^\p{L}\p{N}%?!]+$/gu, "") })).filter((w) => w.w.length > 0);
  const chunks: { s: number; e: number; txt: string }[] = [];
  for (let i = 0; i < words.length; i++) {
    const a = words[i]; const b = words[i + 1];
    if (b && a.w.length <= 3 && b.w.length <= 7 && b.start - a.end < 0.2) { chunks.push({ s: a.start, e: b.end, txt: `${a.w} ${b.w}` }); i++; }
    else chunks.push({ s: a.start, e: a.end, txt: a.w });
  }
  chunks.forEach((c, i) => { const n = chunks[i + 1]; c.e = Math.max(c.e, n ? Math.min(n.s - 0.02, c.e + 0.3) : c.e + 0.3); });
  const c = chunks.find((x) => t >= x.s && t < x.e); if (!c) return null;
  const p = spring({ frame: f - Math.round(c.s * fps), fps, config: { damping: 9, mass: 0.45 } });
  const len = c.txt.length;
  return (
    <div style={{ position: "absolute", top: 1180, width: "100%", textAlign: "center", fontFamily: DISPLAY, fontSize: len <= 6 ? 170 : len > 12 ? 112 : 140, lineHeight: 1,
      transform: `scale(${0.6 + 0.4 * p}) rotate(${(c.s * 7) % 2 > 1 ? -2 : 2}deg)`, color: KEY.test(c.txt) ? GOLD : "#fff", ...stroke }}>{c.txt.toUpperCase()}</div>
  );
};

// Council 4 Nov pick: Hindi caption pills. caps.txt gives one display token per spoken word (Devanagari, *ENGLISH* = blue keyword,
// "_" joins words). Shows the 3-token phrase around the word being spoken, current token in gold, inside a dark rounded pill.
const PillCaptions: React.FC<{ words: W[]; caps: string[][] }> = ({ words: raw, caps }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig(); const t = f / fps;
  const words = raw.filter((w) => w.w.replace(/[^\p{L}\p{N}₹%]/gu, "").length > 0);
  const flat: { tok: string; line: number; pos: number }[] = [];
  // phrases break after , ? । ! . and every 3 tokens, so a box never mixes two sentences
  let g = 0;
  caps.forEach((ln, li) => { let n = 0; ln.forEach((tok) => { flat.push({ tok, line: li, pos: g }); n++; if (/[,?।!.]$/.test(tok) || n === 3) { g++; n = 0; } }); if (n) g++; });
  const i = words.findIndex((w, k) => t >= w.start && t < (words[k + 1] ? Math.min(words[k + 1].start, w.end + 0.4) : w.end + 0.4));
  if (i < 0 || i >= flat.length) return null;
  const me = flat[i];
  const toks = flat.map((x, k) => ({ ...x, k })).filter((x) => x.pos === me.pos);
  const first = words[toks[0].k]?.start ?? words[i].start;
  const p = spring({ frame: f - Math.round(first * fps), fps, config: { damping: 11, mass: 0.5 } });
  return (
    <div style={{ position: "absolute", top: 1190, width: "100%", display: "flex", justifyContent: "center", transform: `scale(${0.75 + 0.25 * p})` }}>
      <div style={{ background: "#000000c8", borderRadius: 34, padding: "10px 34px 4px", maxWidth: 960, display: "flex", flexWrap: "wrap", justifyContent: "center",
        boxShadow: "0 12px 40px #0008", border: "3px solid #ffffff22" }}>
        {toks.map((x) => {
          const eng = /\*/.test(x.tok); const txt = x.tok.replace(/\*/g, "").replace(/_/g, " ");
          const num = /[\d₹%]/.test(txt); const cur = x.k === i; const said = x.k <= i;
          return <span key={x.k} style={{ fontFamily: HINDI, fontWeight: 800, fontSize: txt.length > 9 ? 96 : 116, lineHeight: 1.35,
            color: cur ? GOLD : eng ? BLUE : num ? GOLD : "#fff", opacity: said ? 1 : 0.45, transform: cur ? "scale(1.08)" : undefined, display: "inline-block", margin: "0 24px" }}>{txt}</span>;
        })}
      </div>
    </div>
  );
};

// Council 4 Nov pick: a "save this" card for 1.6 s after the voice, before the loop (useful content gets saved).
const SaveCard: React.FC<{ save: Save; at: number }> = ({ save, at }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const p = spring({ frame: f - Math.round(at * fps), fps, config: { damping: 12, mass: 0.6 } });
  return (
    <AbsoluteFill style={{ background: "#000a", alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: 900, background: "#fff", borderRadius: 40, padding: "36px 46px", transform: `translateY(${(1 - p) * 500}px) rotate(${(1 - p) * -6}deg)`, boxShadow: "0 30px 90px #000" }}>
        <div style={{ fontFamily: DISPLAY, fontSize: 64, color: "#111", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>{save.title}</span><span style={{ fontSize: 50, background: GOLD, borderRadius: 14, padding: "0 18px" }}>SAVE KARO</span>
        </div>
        {save.lines.map((l, k) => (
          <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "16px 0", borderTop: "3px dashed #0002", fontFamily: DISPLAY, fontSize: 52,
            opacity: Math.min(1, Math.max(0, p * 3 - k * 0.5)) }}>
            <span style={{ color: "#444" }}>{l[0]}</span><span style={{ color: l[2] === "red" ? "#e03131" : l[2] === "green" ? "#0a9e4a" : "#111" }}>{l[1]}</span>
          </div>))}
        <div style={{ fontFamily: DISPLAY, fontSize: 30, color: "#777", textAlign: "right", marginTop: 6 }}>{save.footer ?? "FOLLOW: DOUBT CLEAR"}</div>
      </div>
    </AbsoluteFill>
  );
};

const TrendShort: React.FC<Props> = ({ dir, tl, spec }) => {
  const t = useT(); const f = useCurrentFrame();
  if (!tl || !spec) return null;
  const end = tl.total + (spec.save ? SAVE : 0) + (spec.loopTail ?? 0.6);
  const at = (x: string | number) => (typeof x === "number" ? x : tl.cues[x] ?? 0);
  const starts = spec.scenes.map((s, i) => (i === 0 ? 0 : at(s.at)));
  // the last scene is the loop tail: it starts right after the voice ends and repeats frame 1's shot
  const idx = Math.max(0, starts.filter((s) => s <= t).length - 1);
  const s = spec.scenes[idx]; const from = starts[idx]; const to = starts[idx + 1] ?? end;
  let src = s.video; let sub = 0;
  if (s.videos && s.videos.length) { const n = s.videos.length; sub = Math.min(n - 1, Math.floor(((t - from) / Math.max(0.01, to - from)) * n)); src = s.videos[sub]; }
  const sinceCut = Math.min(t - from, s.videos ? (t - from) - (sub * (to - from)) / (s.videos?.length || 1) : 99);
  const flash = sinceCut < 0.12 && t > 0.05 ? 1 - sinceCut / 0.12 : 0;
  const shake = s.shake && t - from < 0.5 ? Math.sin(f * 3.1) * 26 * (1 - (t - from) / 0.5) : 0;
  // every spoken number punches the frame
  const hits = tl.words.filter((w) => /\d|lakh|crore/i.test(w.w)).map((w) => w.start);
  const punch = hits.reduce((m, h) => (t >= h && t < h + 0.22 ? Math.max(m, 1 - (t - h) / 0.22) : m), 0);
  // frame 1: start zoomed hard and snap out, so the very first frame already moves
  const open = t < 0.45 ? 1 - t / 0.45 : 0;
  const note = s.note ?? spec.note;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <style>{fontCss}</style>
      <AbsoluteFill style={{ transform: `scale(${1 + 0.05 * punch + 0.45 * open}) translate(${shake}px, ${-shake * 0.6}px) rotate(${-4 * open}deg)` }}>
        <Shot key={`${idx}-${sub}`} src={src} img={s.img} from={from} to={to} i={idx + sub} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "linear-gradient(#0009 0%, #0000 30%, #0000 52%, #0008 68%, #000c 100%)" }} />
      {flash > 0 && <AbsoluteFill style={{ background: "#fff", opacity: 0.55 * flash }} />}
      {s.headline ? <HeadlineCard key={`h${idx}`} h={s.headline} at={from} tag={s.tag} /> : s.bars ? <Bars key={`r${idx}`} bars={s.bars} unit={s.barUnit} at={from} tag={s.tag} /> : s.counter ? <Melt key={`m${idx}`} c={s.counter} from={from} to={to} tag={s.tag} /> : <Big key={`b${idx}`} s={s} at={from} />}
      {t < tl.total && (tl.caps ? <PillCaptions words={tl.words} caps={tl.caps} /> : <Captions words={tl.words} />)}
      {spec.banner && <div style={{ position: "absolute", top: 64, left: 50, fontFamily: DISPLAY, fontSize: 40, letterSpacing: 2, color: "#000", background: GOLD, borderRadius: 10, padding: "2px 18px" }}>{spec.banner}</div>}
            {spec.save && tl.saveAt !== undefined && t >= tl.saveAt && t < tl.saveAt + SAVE && <SaveCard save={spec.save} at={tl.saveAt} />}
      {/* honest labels, small and out of the way */}
      <div style={{ position: "absolute", top: 70, right: 50, fontFamily: DISPLAY, letterSpacing: 2, fontSize: 28, color: "#fffc", background: "#0008", borderRadius: 8, padding: "2px 12px" }}>AI VOICE</div>
      {note && !(tl.saveAt !== undefined && t >= tl.saveAt) && <div style={{ position: "absolute", top: 1560, left: 60, right: 60, textAlign: "center", fontFamily: DISPLAY, fontSize: 34, letterSpacing: 1, color: "#fffd", textShadow: "0 2px 6px #000" }}>{note}</div>}
      <Audio src={staticFile(`${dir}/voice.wav`)} />
      <Audio src={staticFile("music/tension1.mp3")} volume={(fr) => interpolate(fr, [0, 4, Math.max(5, tl.total * FPS - 10), end * FPS], [0.15, 0.15, 0.15, 0.08], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
      <Sequence from={0} durationInFrames={30}><Audio src={staticFile("sfx/impact.wav")} volume={0.6} /></Sequence>
      {Array.from({ length: Math.floor(tl.total / JUMP) }, (_, k) => (k + 1) * JUMP).map((x) => (
        <Sequence key={`c${x}`} from={Math.round(x * FPS)} durationInFrames={6}><Audio src={staticFile("sfx/click.wav")} volume={0.25} /></Sequence>))}
      {starts.map((x, i) => i === 0 ? null : (
        <Sequence key={i} from={Math.max(0, Math.round(x * FPS) - 8)} durationInFrames={24}>
          <Audio src={staticFile(spec.scenes[i].shake || spec.scenes[i].counter ? "sfx/impact.wav" : "sfx/whoosh.wav")} volume={spec.scenes[i].shake || spec.scenes[i].counter ? 0.5 : 0.4} />
        </Sequence>))}
    </AbsoluteFill>
  );
};

const meta: CalculateMetadataFunction<Props> = async ({ props }) => {
  const raw = await (await fetch(staticFile(`${props.dir}/timeline.json`))).json();
  const spec = (await (await fetch(staticFile(`${props.dir}/scenes.json`))).json()) as Spec;
  const tl: TL = { total: raw.total, cues: raw.cues, words: raw.words };
  // a headline screenshot that could not be captured falls back to the first scene's footage, so a render never fails on it
  const fallback = spec.scenes.find((x) => x.video)?.video;
  for (const sc of spec.scenes) {
    if (sc.img && !(await fetch(staticFile(sc.img))).ok) { console.warn(`missing ${sc.img}, using footage`); sc.img = undefined; sc.video = sc.video ?? fallback; }
  }
  // the loop tail starts when the voice ends
  const voiceEnd = (tl.words[tl.words.length - 1]?.end ?? tl.total) + 0.25;
  const saveLen = spec.save ? SAVE : 0;
  const last = spec.scenes[spec.scenes.length - 1];
  if (last.at === "end") last.at = voiceEnd + saveLen;
  tl.total = voiceEnd; tl.saveAt = spec.save ? voiceEnd : undefined;
  // Hindi pill captions only when caps.txt has exactly one token per spoken word; otherwise the old captions
  const capsRes = await fetch(staticFile(`${props.dir}/caps.txt`));
  if (capsRes.ok) {
    const caps = (await capsRes.text()).split("\n").map((l) => l.trim()).filter(Boolean).map((l) => l.split(/\s+/));
    const n = tl.words.filter((w) => w.w.replace(/[^\p{L}\p{N}₹%]/gu, "").length > 0).length;
    const m = caps.reduce((a, l) => a + l.length, 0);
    if (n === m) tl.caps = caps; else console.warn(`caps.txt has ${m} tokens, voice has ${n} words: using plain captions`);
  }
  return { durationInFrames: Math.ceil((voiceEnd + saveLen + (spec.loopTail ?? 0.6)) * FPS), props: { ...props, tl, spec } };
};

export const TrendShortComposition = () => (
  <Composition id="Trend" component={TrendShort} durationInFrames={600} fps={FPS} width={1080} height={1920}
    calculateMetadata={meta} defaultProps={{ dir: "sample", tl: null, spec: null }} />
);
