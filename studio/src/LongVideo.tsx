// Doubt Clear long video (Ayush, 18 Nov 2026: 1 long video a week, 8-12 min, 16:9). Faceless explainer built from OUR OWN work:
// own animated charts for every number, real photos of the topic (Wikimedia, free licence, credited), free stock video (Mixkit),
// AI stills with no faces. Never other people's footage (no trailers, posters or news clips). No subtitles: only chapter cards,
// number cards and a chapter bar at the bottom so a viewer who looks away can catch up.
// public/<dir>/long.json = { chapters: [{ at, title }], scenes: [Scene] }, timing from public/<dir>/timeline.json (cues from script.txt @keys).
// Render: npx remotion render src/index.ts Long out.mp4 --props='{"dir":"<dir>"}'
import React from "react";
import { AbsoluteFill, CalculateMetadataFunction, Composition, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Audio, Video } from "@remotion/media";
import { DISPLAY, FPS, GOLD, GREEN, RED, useT } from "./Kit";

type Bar = [string, number];
type Chart =
  | { type: "bars"; bars: Bar[]; unit?: string; hi?: number[]; dim?: number[]; title?: string }
  | { type: "stack"; parts: [string, number, string?][]; unit?: string; title?: string }
  | { type: "compare"; rows: [string, number, string?][]; unit?: string; title?: string; max?: number }
  | { type: "board"; rows: [string, number, string?][]; unit?: string; title?: string; markers?: [string, number, string][] }
  | { type: "fan"; actual: number[]; cases: [string, number[], string][]; unit?: string; title?: string; lines?: [string, number][] }
  | { type: "ticket"; parts: [string, number, string][]; title?: string }
  | { type: "scale"; left: [string, number]; right: [string, number]; title?: string; unit?: string }
  | { type: "numbers"; items: [string, string, string?][]; title?: string }
  | { type: "steps"; items: string[]; title?: string };
type Scene = { at: string | number; say?: string[]; img?: string; video?: string; credit?: string; chapter?: string; big?: string; tag?: string; color?: string; chart?: Chart; focus?: string; stamp?: string };
type Spec = { chapters: { at: string | number; title: string }[]; scenes: Scene[]; sources?: string };
type TL = { total: number; cues: Record<string, number>; words?: { w: string; start: number }[] };
type Props = { dir: string; tl: TL | null; spec: Spec | null };

const W = 1920, H = 1080, XF = 0.6;
const COLORS: Record<string, string> = { gold: GOLD, red: RED, green: GREEN, white: "#fff", grey: "#9aa3ad", blue: "#4db8ff" };
const col = (c?: string) => (c ? COLORS[c] ?? c : GOLD);
const fontCss = `@font-face{font-family:Anton;src:url(${staticFile("fonts/Anton.ttf")}) format("truetype");}@font-face{font-family:Baloo;font-weight:800;src:url(${staticFile("fonts/Baloo2-ExtraBold.ttf")}) format("truetype");}`;
const BODY = "Baloo, Anton, sans-serif";
const stroke: React.CSSProperties = { WebkitTextStroke: "8px #000", paintOrder: "stroke fill", textShadow: "0 6px 0 #000" };
const inr = (n: number, d = 0) => {
  const [i, f] = n.toFixed(d).split(".");
  const s = i.length <= 3 ? i : i.slice(0, -3).replace(/\B(?=(\d{2})+(?!\d))/g, ",") + "," + i.slice(-3);
  return f ? `${s}.${f}` : s;
};
const ease = (x: number) => 1 - Math.pow(1 - x, 3);
const useP = (at: number, dur = 0.8) => { const t = useT(); return ease(Math.min(1, Math.max(0, (t - at) / dur))); };
// Chart items appear when the voice says them: ChartView gets one time per item (from the scene's "say" words), charts ask r(i, fallback).
const RevealCtx = React.createContext<number[]>([]);
const useRev = () => { const ts = React.useContext(RevealCtx); return (i: number, def: number) => (ts[i] !== undefined ? ts[i] : def); };
const norm = (x: string) => x.toLowerCase().replace(/[^a-z0-9]/g, "");
// First spoken word at or after `after` that starts with the pattern (several words: all must follow in order).
const findWord = (tl: TL, pat: string, after: number): number | undefined => {
  const ws = tl.words ?? []; const ps = pat.split(" ").map(norm).filter(Boolean);
  for (let i = 0; i < ws.length; i++) {
    if (ws[i].start < after - 0.05) continue;
    if (ps.every((q, k) => ws[i + k] && norm(ws[i + k].w).startsWith(q))) return ws[i].start;
  }
  return undefined;
};
const isImg = (x?: string) => !!x && /\.(jpe?g|png|webp)$/i.test(x);

// One slow, smooth shot (push in / pull out with a gentle drift), never a jump; crossfades in.
const Shot: React.FC<{ s: Scene; from: number; to: number; i: number; dark: boolean }> = ({ s, from, to, i, dark }) => {
  const t = useT();
  const k = interpolate(t, [from, to + XF], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const z = i % 2 === 0 ? 1.03 + 0.08 * k : 1.11 - 0.08 * k;
  const dx = (i % 3 === 0 ? -1 : i % 3 === 1 ? 1 : 0) * 30 * (k - 0.5);
  const op = interpolate(t, [from, from + XF], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const style: React.CSSProperties = { width: "100%", height: "100%", objectFit: "cover", objectPosition: s.focus ?? "50% 50%", transform: `translateX(${dx}px) scale(${z})`,
    filter: dark ? "blur(14px) brightness(0.35)" : "brightness(0.9)" };
  const src = s.video ?? s.img;
  return (
    <AbsoluteFill style={{ opacity: i === 0 ? 1 : op, overflow: "hidden", background: "#05070a" }}>
      {src ? (isImg(src) ? <Img src={staticFile(src)} style={style} /> : <Video src={staticFile(src)} muted loop style={style} />) : null}
      {!dark && <AbsoluteFill style={{ background: "linear-gradient(180deg, #0000 45%, #000c 100%)" }} />}
    </AbsoluteFill>
  );
};

const Title: React.FC<{ text?: string }> = ({ text }) => text ? <div style={{ fontFamily: DISPLAY, fontSize: 54, color: GOLD, letterSpacing: 2, marginBottom: 30 }}>{text.toUpperCase()}</div> : null;

const Bars: React.FC<{ c: Extract<Chart, { type: "bars" }>; at: number }> = ({ c, at }) => {
  const t = useT(); const r = useRev();
  const max = Math.max(...c.bars.map((b) => b[1]));
  const step = Math.min(0.35, 4 / c.bars.length);
  return (
    <div><Title text={c.title} />
      <div style={{ display: "flex", alignItems: "flex-end", gap: 18, height: 560 }}>
        {c.bars.map(([l, v], i) => {
          const p = ease(Math.min(1, Math.max(0, (t - r(i, at + i * step)) / 0.6)));
          const colr = c.hi?.includes(i) ? GOLD : c.dim?.includes(i) ? "#59616b" : "#e8ecf0";
          return (
            <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-end", height: "100%" }}>
              <div style={{ fontFamily: DISPLAY, fontSize: 34, color: colr, opacity: p }}>{inr(v * p, v % 1 ? 1 : 0)}</div>
              <div style={{ width: "100%", height: `${(v / max) * 470 * p}px`, background: colr, borderRadius: "10px 10px 0 0", boxShadow: c.hi?.includes(i) ? `0 0 40px ${GOLD}88` : undefined }} />
              <div style={{ fontFamily: BODY, fontSize: 26, color: "#cfd6dd", marginTop: 10, whiteSpace: "nowrap" }}>{l}</div>
            </div>
          );
        })}
      </div>
      {c.unit && <div style={{ fontFamily: BODY, fontSize: 28, color: "#9aa3ad", marginTop: 16 }}>{c.unit}</div>}
    </div>
  );
};

const HBars: React.FC<{ rows: [string, number, string?][]; at: number; unit?: string; max?: number; markers?: [string, number, string][] }> = ({ rows, at, unit, max: mx, markers }) => {
  const t = useT(); const r = useRev();
  const max = mx ?? Math.max(...rows.map((r) => r[1]), ...(markers ?? []).map((m) => m[1])) * 1.05;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, position: "relative" }}>
      {rows.map(([l, v, c], i) => {
        const p = ease(Math.min(1, Math.max(0, (t - r(i, at + i * 0.25)) / 0.7)));
        return (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 24 }}>
            <div style={{ width: 380, fontFamily: BODY, fontSize: 38, color: "#fff", textAlign: "right" }}>{l}</div>
            <div style={{ flex: 1, position: "relative", height: 58 }}>
              <div style={{ width: `${(v / max) * 100 * p}%`, height: "100%", background: col(c ?? "white"), borderRadius: 8 }} />
              <div style={{ position: "absolute", left: `calc(${(v / max) * 100 * p}% + 14px)`, top: 4, fontFamily: DISPLAY, fontSize: 40, color: col(c ?? "white"), opacity: p }}>{inr(v * p)}{unit ?? ""}</div>
            </div>
          </div>
        );
      })}
      {markers?.map(([l, v, c], i) => {
        const p = useP(r(rows.length + i, at + rows.length * 0.25 + 0.8 + i * 1.2), 0.6);
        return (
          <div key={`m${i}`} style={{ position: "absolute", top: -40, bottom: -10, left: `calc(404px + (100% - 404px) * ${(v / max) * p})`, borderLeft: `5px dashed ${col(c)}`, opacity: p }}>
            <div style={{ position: "absolute", top: i % 2 ? -95 : -50, left: -10, whiteSpace: "nowrap", fontFamily: DISPLAY, fontSize: 34, color: col(c) }}>{l}</div>
          </div>
        );
      })}
    </div>
  );
};

const Stack: React.FC<{ c: Extract<Chart, { type: "stack" }>; at: number }> = ({ c, at }) => {
  const r = useRev();
  const total = c.parts.reduce((a, p) => a + p[1], 0);
  const palette = [GOLD, "#ff9f43", "#4db8ff", GREEN, "#c084fc", "#ff6b81"];
  return (
    <div><Title text={c.title} />
      <div style={{ display: "flex", height: 130, borderRadius: 14, overflow: "hidden" }}>
        {c.parts.map(([l, v, cc], i) => { const p = useP(r(i, at + i * 0.5), 0.6); return <div key={i} style={{ width: `${(v / total) * 100 * p}%`, background: cc ? col(cc) : palette[i % palette.length] }} />; })}
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "18px 40px", marginTop: 34 }}>
        {c.parts.map(([l, v, cc], i) => { const p = useP(r(i, at + i * 0.5), 0.6); return (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 14, opacity: p }}>
            <div style={{ width: 30, height: 30, borderRadius: 6, background: cc ? col(cc) : palette[i % palette.length] }} />
            <div style={{ fontFamily: BODY, fontSize: 40, color: "#fff" }}>{l} <span style={{ fontFamily: DISPLAY, color: GOLD }}>{inr(v)}{c.unit ?? ""}</span> <span style={{ color: "#9aa3ad" }}>({Math.round((v / total) * 100)}%)</span></div>
          </div>); })}
      </div>
    </div>
  );
};

// Cumulative line: actual points solid, each case dashed from the last actual point; horizontal reference lines (records).
const Fan: React.FC<{ c: Extract<Chart, { type: "fan" }>; at: number }> = ({ c, at }) => {
  const t = useT(); const r = useRev();
  const n = Math.max(c.actual.length, ...c.cases.map((k) => c.actual.length - 1 + k[1].length));
  const max = Math.max(...c.actual, ...c.cases.flatMap((k) => k[1]), ...(c.lines ?? []).map((l) => l[1])) * 1.08;
  const w = 1500, h = 600;
  const X = (i: number) => (i / (n - 1)) * w, Y = (v: number) => h - (v / max) * h;
  const path = (pts: number[], off: number) => pts.map((v, i) => `${i ? "L" : "M"}${X(i + off)},${Y(v)}`).join(" ");
  const pa = useP(at, 1.2);
  const last = c.actual.length - 1;
  // end labels: keep at least 46 px apart so close cases never overprint
  const ends = c.cases.map((k, i) => ({ i, y: Y(k[1][k[1].length - 1]) })).sort((a, b) => a.y - b.y);
  const ly: number[] = [];
  ends.forEach((e, j) => { ly[e.i] = j === 0 ? e.y : Math.max(e.y, ly[ends[j - 1].i] + 46); });
  return (
    <div><Title text={c.title} />
      <svg width={w + 260} height={h + 40} style={{ overflow: "visible" }}>
        {(c.lines ?? []).map(([l, v], i) => (
          <g key={i} opacity={useP(at + 0.3, 0.6)}>
            <line x1={0} x2={w} y1={Y(v)} y2={Y(v)} stroke="#ffffff55" strokeWidth={3} strokeDasharray="10 10" />
            <text x={w + 16} y={Y(v) + 12} fill="#cfd6dd" fontFamily={BODY} fontSize={30}>{l} {inr(v)}</text>
          </g>
        ))}
        <path d={path(c.actual, 0)} stroke="#fff" strokeWidth={8} fill="none" strokeDasharray={3000} strokeDashoffset={3000 * (1 - pa)} />
        {c.cases.map(([l, pts, cc], i) => {
          const p = ease(Math.min(1, Math.max(0, (t - r(i, at + 1.4 + i * 1.6)) / 1.2)));
          const full = [c.actual[last], ...pts];
          const end = full[full.length - 1];
          return (
            <g key={i}>
              <path d={path(full, last)} stroke={col(cc)} strokeWidth={7} fill="none" strokeDasharray="2400" strokeDashoffset={2400 * (1 - p)} />
              <text x={X(n - 1) + 16} y={ly[i] + 12} fill={col(cc)} fontFamily={DISPLAY} fontSize={36} opacity={p > 0.95 ? 1 : 0}>{l}: {inr(end)}</text>
            </g>
          );
        })}
      </svg>
      {c.unit && <div style={{ fontFamily: BODY, fontSize: 28, color: "#9aa3ad" }}>{c.unit}</div>}
    </div>
  );
};

const Ticket: React.FC<{ c: Extract<Chart, { type: "ticket" }>; at: number }> = ({ c, at }) => {
  const r = useRev();
  const total = c.parts.reduce((a, p) => a + p[1], 0);
  const p0 = useP(at, 0.6);
  return (
    <div><Title text={c.title} />
      <div style={{ display: "flex", height: 260, gap: 12, transform: `scale(${0.9 + 0.1 * p0})`, opacity: p0 }}>
        {c.parts.map(([l, v, cc], i) => { const p = useP(r(i, at + 0.8 + i * 1.4), 0.6); return (
          <div key={i} style={{ width: `${(v / total) * 100}%`, background: col(cc), borderRadius: 18, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center",
            transform: `translateY(${(1 - p) * -40}px)`, border: "4px dashed #0006", opacity: 0.35 + 0.65 * p }}>
            <div style={{ fontFamily: DISPLAY, fontSize: 90, color: "#000" }}>₹{v}</div>
            <div style={{ fontFamily: BODY, fontSize: 34, color: "#000", opacity: p }}>{l}</div>
          </div>); })}
      </div>
    </div>
  );
};

const Scale: React.FC<{ c: Extract<Chart, { type: "scale" }>; at: number }> = ({ c, at }) => {
  const p = useP(useRev()(0, at + 0.6), 1.4);
  const tilt = (c.left[1] < c.right[1] ? 1 : -1) * 9 * p;
  const pan = (label: string, v: number, colr: string) => (
    <div style={{ width: 560, textAlign: "center" }}>
      <div style={{ fontFamily: DISPLAY, fontSize: 96, color: colr, ...stroke }}>₹{inr(v)}{c.unit ?? " Cr"}</div>
      <div style={{ fontFamily: BODY, fontSize: 36, color: "#fff" }}>{label}</div>
    </div>
  );
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}><Title text={c.title} />
      <div style={{ width: 1300, height: 10, background: "#cfd6dd", borderRadius: 5, transform: `rotate(${tilt}deg)`, marginTop: 60 }} />
      <div style={{ display: "flex", justifyContent: "space-between", width: 1300, marginTop: 30, transform: `rotate(${tilt}deg)` }}>{pan(c.left[0], c.left[1], GOLD)}{pan(c.right[0], c.right[1], RED)}</div>
    </div>
  );
};

const Numbers: React.FC<{ c: Extract<Chart, { type: "numbers" }>; at: number }> = ({ c, at }) => { const r = useRev(); return (
  <div><Title text={c.title} />
    <div style={{ display: "flex", gap: 30, flexWrap: "wrap" }}>
      {c.items.map(([label, value, cc], i) => { const p = useP(r(i, at + i * 0.9), 0.5); return (
        <div key={i} style={{ flex: "1 1 360px", background: "#0b0f14dd", border: `3px solid ${col(cc)}`, borderRadius: 22, padding: "30px 36px", opacity: p, transform: `translateY(${(1 - p) * 40}px)` }}>
          <div style={{ fontFamily: BODY, fontSize: 36, color: "#cfd6dd" }}>{label}</div>
          <div style={{ fontFamily: DISPLAY, fontSize: 96, color: col(cc), lineHeight: 1.1 }}>{value}</div>
        </div>); })}
    </div>
  </div>
); };

const Steps: React.FC<{ c: Extract<Chart, { type: "steps" }>; at: number }> = ({ c, at }) => { const r = useRev(); return (
  <div><Title text={c.title} />
    {c.items.map((s, i) => { const p = useP(r(i, at + i * 2.2), 0.5); return (
      <div key={i} style={{ display: "flex", gap: 30, alignItems: "center", marginBottom: 34, opacity: p, transform: `translateX(${(1 - p) * -50}px)` }}>
        <div style={{ fontFamily: DISPLAY, fontSize: 100, color: "#000", background: GOLD, borderRadius: 20, width: 140, textAlign: "center" }}>{i + 1}</div>
        <div style={{ fontFamily: BODY, fontSize: 52, color: "#fff", lineHeight: 1.2 }}>{s}</div>
      </div>); })}
  </div>
); };

const ChartView: React.FC<{ c: Chart; at: number; times?: number[] }> = ({ c, at, times }) => {
  const body = (() => {
    switch (c.type) {
      case "bars": return <Bars c={c} at={at} />;
      case "stack": return <Stack c={c} at={at} />;
      case "compare": return <div><Title text={c.title} /><HBars rows={c.rows} at={at} unit={c.unit} max={c.max} /></div>;
      case "board": return <div><Title text={c.title} /><HBars rows={c.rows} at={at} unit={c.unit} markers={c.markers} /></div>;
      case "fan": return <Fan c={c} at={at} />;
      case "ticket": return <Ticket c={c} at={at} />;
      case "scale": return <Scale c={c} at={at} />;
      case "numbers": return <Numbers c={c} at={at} />;
      case "steps": return <Steps c={c} at={at} />;
    }
  })();
  return <RevealCtx.Provider value={times ?? []}><AbsoluteFill style={{ padding: "110px 150px 150px", justifyContent: "center" }}>{body}</AbsoluteFill></RevealCtx.Provider>;
};

const ChapterCard: React.FC<{ n: number; title: string; at: number }> = ({ n, title, at }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const p = spring({ frame: f - Math.round(at * fps), fps, config: { damping: 14, mass: 0.7 } });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div style={{ fontFamily: DISPLAY, fontSize: 60, color: GOLD, letterSpacing: 8, opacity: Math.min(1, p) }}>CHAPTER {n}</div>
      <div style={{ height: 8, width: `${700 * Math.min(1, p)}px`, background: GOLD, borderRadius: 4, margin: "18px 0" }} />
      <div style={{ fontFamily: DISPLAY, fontSize: 150, color: "#fff", transform: `scale(${1.15 - 0.15 * Math.min(1, p)})`, ...stroke }}>{title.toUpperCase()}</div>
    </AbsoluteFill>
  );
};

const BigText: React.FC<{ s: Scene; at: number }> = ({ s, at }) => {
  const p = useP(at, 0.5);
  const c = col(s.color);
  return (
    <div style={{ position: "absolute", left: 110, right: 110, bottom: 140 }}>
      {s.tag && <div style={{ display: "inline-block", fontFamily: DISPLAY, fontSize: 48, color: "#000", background: GOLD, borderRadius: 12, padding: "2px 22px", marginBottom: 14, opacity: p }}>{s.tag}</div>}
      {s.big && <div style={{ fontFamily: DISPLAY, fontSize: s.big.length < 14 ? 150 : 110, lineHeight: 1, color: c, opacity: p, transform: `translateY(${(1 - p) * 30}px)`, ...stroke, textShadow: `0 6px 0 #000, 0 0 50px ${c}88` }}>{s.big}</div>}
    </div>
  );
};

const LongVideo: React.FC<Props> = ({ dir, tl, spec }) => {
  const t = useT();
  if (!tl || !spec) return <AbsoluteFill style={{ background: "#000" }} />;
  const when = (a: string | number) => (typeof a === "number" ? a : tl.cues[a] ?? 0);
  // "w:<word>" = the first time that word is spoken after the scene listed before it (fine-grained sync without re-voicing).
  let prev = 0;
  const scenes = spec.scenes.map((s) => {
    const t0 = typeof s.at === "string" && s.at.startsWith("w:") ? findWord(tl, s.at.slice(2), prev + 0.1) ?? prev + 2 : when(s.at);
    // each "say" word is looked up from the scene start; "" keeps the chart's own timing
    const times = (s.say ?? []).map((w) => (w ? findWord(tl, w, t0 - 0.4) : undefined)) as number[];
    prev = t0; return { ...s, t0, times };
  }).sort((a, b) => a.t0 - b.t0);
  const chapters = spec.chapters.map((c) => ({ ...c, t0: when(c.at) }));
  const end = tl.total;
  const idx = Math.max(0, scenes.findIndex((s, i) => t >= s.t0 && (i === scenes.length - 1 || t < scenes[i + 1].t0)));
  // Background shot: the latest scene at or before idx that has media; charts sit on a blurred, darkened copy of it.
  const visible = scenes.map((s, i) => ({ s, i, to: i < scenes.length - 1 ? scenes[i + 1].t0 : end })).filter(({ i }) => i >= idx - 1 && i <= idx);
  let bgIdx = idx; while (bgIdx > 0 && !scenes[bgIdx].img && !scenes[bgIdx].video) bgIdx--;
  const cur = scenes[idx];
  const chapNo = chapters.filter((c) => t >= c.t0).length;
  const credit = scenes[bgIdx]?.credit;
  return (
    <AbsoluteFill style={{ background: "#05070a" }}>
      <style>{fontCss}</style>
      <Audio src={staticFile(`${dir}/voice.wav`)} />
      <Audio src={staticFile("music/tension1.mp3")} loop volume={0.06} />
      {visible.map(({ s, i, to }) => {
        let b = i; while (b > 0 && !scenes[b].img && !scenes[b].video) b--;
        const dark = !!s.chart || !!s.chapter;
        return <Shot key={`${b}-${dark}`} s={scenes[b]} from={scenes[b].t0} to={to} i={b} dark={dark} />;
      })}
      {cur.chapter && <ChapterCard n={chapters.findIndex((c) => c.title === cur.chapter)} title={cur.chapter} at={cur.t0} />}
      {cur.chart && <ChartView key={idx} c={cur.chart} at={cur.t0} times={cur.times} />}
      {!cur.chart && !cur.chapter && (cur.big || cur.tag) && <BigText key={idx} s={cur} at={cur.t0} />}
      {cur.stamp && <div style={{ position: "absolute", right: 120, top: 120, fontFamily: DISPLAY, fontSize: 44, color: RED, border: `5px solid ${RED}`, borderRadius: 12, padding: "4px 20px", transform: "rotate(6deg)" }}>{cur.stamp.toUpperCase()}</div>}
      {/* corner mark + chapter bar (YouTube-style segments) + credit */}
      <div style={{ position: "absolute", left: 50, top: 40, fontFamily: DISPLAY, fontSize: 36, color: "#fff", opacity: 0.85 }}>DOUBT <span style={{ color: GOLD }}>CLEAR</span></div>
      <div style={{ position: "absolute", left: 50, right: 50, bottom: 34, display: "flex", gap: 8 }}>
        {chapters.map((c, i) => {
          const to = i < chapters.length - 1 ? chapters[i + 1].t0 : end;
          const fill = Math.min(1, Math.max(0, (t - c.t0) / Math.max(0.1, to - c.t0)));
          return (
            <div key={i} style={{ flex: Math.max(1, to - c.t0) }}>
              <div style={{ fontFamily: BODY, fontSize: 22, color: i + 1 === chapNo ? GOLD : "#ffffff88", marginBottom: 6, whiteSpace: "nowrap", overflow: "hidden" }}>{c.title}</div>
              <div style={{ height: 8, background: "#ffffff33", borderRadius: 4 }}><div style={{ width: `${fill * 100}%`, height: "100%", background: GOLD, borderRadius: 4 }} /></div>
            </div>
          );
        })}
      </div>
      {credit && <div style={{ position: "absolute", right: 54, bottom: 92, fontFamily: BODY, fontSize: 20, color: "#ffffffaa" }}>{credit}</div>}
    </AbsoluteFill>
  );
};

const meta: CalculateMetadataFunction<Props> = async ({ props }) => {
  const tl = (await (await fetch(staticFile(`${props.dir}/timeline.json`))).json()) as TL;
  const spec = (await (await fetch(staticFile(`${props.dir}/long.json`))).json()) as Spec;
  // check every media file once, in parallel (a sequential check of ~40 files timed out on the runner, 18 Nov)
  const files = [...new Set(spec.scenes.flatMap((s) => [s.img, s.video]).filter((x): x is string => !!x))];
  const ok = new Map(await Promise.all(files.map(async (f) => [f, (await fetch(staticFile(f), { method: "HEAD" })).ok] as const)));
  for (const s of spec.scenes) {
    for (const k of ["img", "video"] as const) {
      const v = s[k];
      if (v && !ok.get(v)) { console.warn(`missing ${v}`); s[k] = undefined; }
    }
  }
  return { durationInFrames: Math.ceil((tl.total + 0.5) * FPS), props: { ...props, tl, spec } };
};

export const LongVideoComposition = () => (
  <Composition id="Long" component={LongVideo} durationInFrames={600} fps={FPS} width={W} height={H} calculateMetadata={meta} defaultProps={{ dir: "sample", tl: null, spec: null }} />
);
