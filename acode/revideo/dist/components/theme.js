"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Theme = void 0;
exports.Theme = {
    // ── Scene ─────────────────────────────────────
    /** The darkest layer — nothing should be this dark except the scene. */
    sceneBg: "#141414",
    // ── IDE shell ─────────────────────────────────
    /** Main IDE window background. One step above the scene. */
    ideBg: "#1e1e1e",
    /** IDE window border / subtle outline. */
    ideBorder: "#2b2b2b",
    // ── Panels ────────────────────────────────────
    /** Sidebar (explorer) and terminal background. */
    panelBg: "#252526",
    /** Menu bar, tab bar, and panel header background. */
    headerBg: "#333333",
    /** Thin dividers between panels. */
    divider: "#3c3c3c",
    // ── Status bar ────────────────────────────────
    /** The accent-colored bar at the bottom. */
    statusBg: "#007acc",
    // ── Text ──────────────────────────────────────
    /** Primary text (code, file names). */
    text: "#cccccc",
    /** Dimmed text (headings like EXPLORER, TERMINAL). */
    textDim: "#888888",
    /** Bright text (selected file, active label). */
    textBright: "#ffffff",
    /** Accent text (terminal prompt, success messages). */
    textAccent: "#4ec9b0",
    /** Warning / instruction text. */
    textWarning: "#e6a700",
    // ── Selection ─────────────────────────────────
    /** File selection highlight in the explorer. */
    selection: "#094771",
    // ── Browser ───────────────────────────────────
    /** Browser window background (same as IDE for consistency). */
    browserBg: "#1e1e1e",
    /** Browser title bar. */
    browserHeader: "#2d2d2d",
    /** Address bar background. */
    addressBarBg: "#333333",
    /** Address bar text. */
    addressBarText: "#aaaaaa",
    /** Browser preview area (the "web page"). */
    previewBg: "#ffffff",
    /** Text inside the preview area. */
    previewText: "#1e1e1e",
    // ── Window dots (macOS style) ─────────────────
    dotClose: "#ff5f57",
    dotMinimize: "#febc2e",
    dotMaximize: "#28c840",
    // ── Fonts ─────────────────────────────────────
    fontMono: "JetBrains Mono, Courier New, monospace",
    fontSans: "sans-serif",
    fontSizeCode: 14,
    fontSizeUI: 13,
    fontSizeSmall: 11,
    fontSizeLabel: 12,
};
//# sourceMappingURL=theme.js.map