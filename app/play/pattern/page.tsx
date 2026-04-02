"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { sfxPop, sfxCorrect, sfxWrong } from "@/app/play/sfx";

const SHAPES = ["🔴", "🔵", "🟢", "🟡", "🟣", "🟠"];
const ICONS = ["⭐", "🌙", "💎", "🔥", "🌸", "⚡"];

type PatternDef = { sequence: string[]; repeatLen: number };

function genPattern(difficulty: number): PatternDef {
  const pool = difficulty <= 2 ? SHAPES.slice(0, 3) : difficulty <= 4 ? SHAPES.slice(0, 4) : ICONS.slice(0, 5);
  const repeatLen = difficulty <= 2 ? 2 : difficulty <= 4 ? 3 : 4;
  const base: string[] = [];
  for (let i = 0; i < repeatLen; i++) {
    base.push(pool[Math.floor(Math.random() * pool.length)]);
  }
  // Ensure at least 2 distinct items
  if (new Set(base).size < 2) base[1] = pool[(pool.indexOf(base[0]) + 1) % pool.length];
  const sequence: string[] = [];
  for (let i = 0; i < repeatLen * 3; i++) sequence.push(base[i % repeatLen]);
  return { sequence, repeatLen };
}

export default function PatternPage() {
  const [level, setLevel] = useState(1);
  const [pattern, setPattern] = useState<PatternDef>(() => genPattern(1));
  const [hidden, setHidden] = useState<number[]>(() => {
    const p = genPattern(1);
    return [p.sequence.length - 1]; // hide last
  });
  const [guesses, setGuesses] = useState<Record<number, string>>({});
  const [feedback, setFeedback] = useState("");
  const [score, setScore] = useState(0);

  const initRound = useCallback((lv: number) => {
    const p = genPattern(lv);
    // Hide last `hideCount` items
    const hideCount = Math.min(lv, 4);
    const indices: number[] = [];
    for (let i = p.sequence.length - hideCount; i < p.sequence.length; i++) indices.push(i);
    setPattern(p);
    setHidden(indices);
    setGuesses({});
    setFeedback("");
    return p;
  }, []);

  const startLevel = (lv: number) => {
    setLevel(lv);
    initRound(lv);
  };

  const check = () => {
    const allCorrect = hidden.every(i => guesses[i] === pattern.sequence[i]);
    if (allCorrect) {
      setFeedback("🎉 Correct!");
      setScore(s => s + level);
      sfxCorrect();
    } else {
      setFeedback("❌ Not quite — look at the pattern again!");
      sfxWrong();
    }
  };

  const next = () => {
    const nextLv = Math.min(level + 1, 6);
    setLevel(nextLv);
    initRound(nextLv);
  };

  // Available choices for guessing
  const pool = [...new Set(pattern.sequence)];

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>🏠 Home</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>🧩 Pattern Machine</h1>
        <span style={{ fontSize: 13, color: "#888" }}>Level {level} · Score: {score}</span>
      </div>

      <div style={{ padding: "0 16px 16px" }}>
        <div style={{ background: "#111827", borderRadius: 12, border: "1px solid #333", padding: 20, maxWidth: 700 }}>
          <div style={{ fontSize: 14, color: "#888", marginBottom: 12 }}>Complete the pattern:</div>

          {/* Pattern display */}
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 20, alignItems: "center" }}>
            {pattern.sequence.map((item, i) => {
              const isHidden = hidden.includes(i);
              const guess = guesses[i];
              const correct = feedback.startsWith("🎉") && isHidden;
              return (
                <div
                  key={i}
                  style={{
                    width: 52, height: 52, borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 28, background: isHidden ? (correct ? "#22c55e22" : "#1e293b") : "#1a1a2e",
                    border: isHidden ? (correct ? "2px solid #22c55e" : "2px dashed #f59e0b") : "1px solid #333",
                    position: "relative",
                  }}
                >
                  {isHidden ? (guess || "?") : item}
                  {/* Position indicator */}
                  <span style={{ position: "absolute", bottom: -16, fontSize: 9, color: "#555" }}>{i + 1}</span>
                </div>
              );
            })}
          </div>

          {/* Choices */}
          {!feedback.startsWith("🎉") && (
            <>
              <div style={{ fontSize: 13, color: "#888", marginBottom: 8 }}>
                Click to fill slot {hidden.find(i => !guesses[i]) !== undefined ? `#${(hidden.find(i => !guesses[i])!) + 1}` : ""}:
              </div>
              <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                {pool.map((item, i) => (
                  <div
                    key={i}
                    onClick={() => {
                      const slot = hidden.find(idx => !guesses[idx]);
                      if (slot !== undefined) { sfxPop(); setGuesses(prev => ({ ...prev, [slot]: item })); }
                    }}
                    style={{
                      width: 48, height: 48, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center",
                      fontSize: 26, background: "#1a1a2e", border: "1px solid #555", cursor: "pointer",
                    }}
                  >
                    {item}
                  </div>
                ))}
              </div>
            </>
          )}

          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            {!feedback.startsWith("🎉") && (
              <>
                <button onClick={check} disabled={hidden.some(i => !guesses[i])} style={{ ...btn, background: "#3b82f6", border: "none", opacity: hidden.some(i => !guesses[i]) ? 0.4 : 1 }}>
                  ✅ Check
                </button>
                <button onClick={() => setGuesses({})} style={btn}>↩ Reset</button>
              </>
            )}
            {feedback.startsWith("🎉") && <button onClick={next} style={{ ...btn, background: "#22c55e", color: "#000", border: "none" }}>Next Level →</button>}
            {feedback && <span style={{ fontSize: 15 }}>{feedback}</span>}
          </div>

          {/* Repeat hint */}
          <div style={{ marginTop: 16, fontSize: 12, color: "#666" }}>
            💡 The pattern repeats every <b style={{ color: "#f59e0b" }}>{pattern.repeatLen}</b> items
          </div>
        </div>

        {/* Level selector */}
        <div style={{ display: "flex", gap: 6, marginTop: 12 }}>
          {[1, 2, 3, 4, 5, 6].map(lv => (
            <button key={lv} onClick={() => startLevel(lv)} style={{ ...btn, background: level === lv ? "#8b5cf6" : "#1a1a2e" }}>
              Lv {lv}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

const btn: React.CSSProperties = { padding: "6px 14px", borderRadius: 6, border: "1px solid #555", background: "#1a1a2e", color: "#fff", cursor: "pointer", fontSize: 13 };
