// Shared constants for the Doubt Clear Shorts.
import { useCurrentFrame, useVideoConfig } from "remotion";

export const FPS = 30;
export const GOLD = "#ffd60a";
export const RED = "#ff4d4d";
export const GREEN = "#2ee6a0";
export const DISPLAY = "Anton, 'Noto Color Emoji', sans-serif";
export const useT = () => { const f = useCurrentFrame(); const { fps } = useVideoConfig(); return f / fps; };
