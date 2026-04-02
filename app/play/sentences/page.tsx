"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { sfxPop, sfxRemove, sfxCorrect, sfxWrong } from "@/app/play/sfx";

const SENTENCES = [
  { words: ["The", "cat", "sat", "on", "the", "mat"], emoji: "🐱" },
  { words: ["I", "like", "to", "eat", "apples"], emoji: "🍎" },
  { words: ["The", "sun", "is", "very", "hot"], emoji: "☀️" },
  { words: ["Fish", "swim", "in", "the", "sea"], emoji: "🐟" },
  { words: ["Birds", "can", "fly", "in", "the", "sky"], emoji: "🐦" },
  { words: ["The", "dog", "runs", "very", "fast"], emoji: "🐶" },
  { words: ["We", "go", "to", "school", "every", "day"], emoji: "🏫" },
  { words: ["The", "moon", "shines", "at", "night"], emoji: "🌙" },
  { words: ["Rain", "falls", "from", "the", "clouds"], emoji: "🌧️" },
  { words: ["Trees", "have", "green", "leaves"], emoji: "🌳" },
  { words: ["The", "baby", "is", "sleeping", "now"], emoji: "👶" },
  { words: ["I", "can", "count", "to", "ten"], emoji: "🔢" },
  { words: ["Stars", "twinkle", "in", "the", "dark", "sky"], emoji: "⭐" },
  { words: ["The", "frog", "jumped", "into", "the", "pond"], emoji: "🐸" },
  { words: ["Snow", "is", "cold", "and", "white"], emoji: "❄️" },
];

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export default function SentencesPage() {
  const [idx, setIdx] = useState(0);
  const [placed, setPlaced] = useState<string[]>([]);
  const [pool, setPool] = useState<{ word: string; id: number }[]>(() =>
    shuffle(SENTENCES[0].words.map((w, i) => ({ word: w, id: i })))
  );
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState("");

  const current = SENTENCES[idx];
  const target = current.words.join(" ");

  const initSentence = useCallback((i: number) => {
    const s = SENTENCES[i];
    setIdx(i);
    setPlaced([]);
    setPool(shuffle(s.words.map((w, j) => ({ word: w, id: j }))));
    setFeedback("");
  }, []);

  const addWord = (tile: { word: string; id: number }) => {
    sfxPop();
    setPlaced(prev => [...prev, tile.word]);
    setPool(prev => prev.filter(t => t.id !== tile.id));
  };

  const removeLastWord = () => {
    if (placed.length === 0) return;
    sfxRemove();
    const word = placed[placed.length - 1];
    setPlaced(prev => prev.slice(0, -1));
    setPool(prev => [...prev, { word, id: Date.now() + Math.random() }]);
  };

  const check = () => {
    if (placed.join(" ") === target) {
      setFeedback("🎉 Perfect sentence!");
      setScore(s => s + 1);
      sfxCorrect();
    } else {
      setFeedback("❌ Not quite — try a different order!");
      sfxWrong();
    }
  };

  const next = () => initSentence((idx + 1) % SENTENCES.length);

  const WORD_COLORS = ["#3b82f6", "#8b5cf6", "#22c55e", "#f59e0b", "#ef4444", "#ec4899", "#14b8a6", "#6366f1"];

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>🏠 Home</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>📝 Sentence Scramble</h1>
        <span style={{ fontSize: 13, color: "#888" }}>Score: {score}</span>
      </div>

      <div style={{ padding: "0 16px 16px", maxWidth: 650 }}>
        <div style={{ background: "#111827", borderRadius: 12, border: "1px solid #333", padding: 24 }}>
          {/* Emoji hint */}
          <div style={{ fontSize: 48, textAlign: "center", marginBottom: 8 }}>{current.emoji}</div>

          {/* Sentence area */}
          <div style={{
            minHeight: 60, borderRadius: 10, border: "2px dashed #333", padding: 12, marginBottom: 20,
            display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center",
            background: feedback.startsWith("🎉") ? "#22c55e11" : "#0a0a1a",
          }}>
            {placed.length === 0 && <span style={{ color: "#555", fontSize: 14 }}>Click words below to build the sentence...</span>}
            {placed.map((word, i) => (
              <span key={i} style={{
                padding: "6px 12px", borderRadius: 6, fontSize: 16, fontWeight: 600,
                background: WORD_COLORS[i % WORD_COLORS.length] + "33",
                border: `1px solid ${WORD_COLORS[i % WORD_COLORS.length]}`,
                color: WORD_COLORS[i % WORD_COLORS.length],
              }}>
                {word}
              </span>
            ))}
          </div>

          {/* Word pool */}
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 20, justifyContent: "center" }}>
            {pool.map(tile => (
              <div
                key={tile.id}
                onClick={() => addWord(tile)}
                style={{
                  padding: "8px 16px", borderRadius: 8, fontSize: 16, fontWeight: 600,
                  background: "#1e293b", border: "1px solid #555", cursor: "pointer", userSelect: "none",
                }}
              >
                {tile.word}
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: 8, justifyContent: "center", alignItems: "center" }}>
            {!feedback.startsWith("🎉") && (
              <>
                <button onClick={check} disabled={pool.length > 0} style={{ ...btn, background: "#3b82f6", border: "none", opacity: pool.length > 0 ? 0.4 : 1 }}>✅ Check</button>
                <button onClick={removeLastWord} disabled={placed.length === 0} style={btn}>⬅ Undo</button>
                <button onClick={() => initSentence(idx)} style={btn}>↩ Reset</button>
              </>
            )}
            {feedback.startsWith("🎉") && <button onClick={next} style={{ ...btn, background: "#22c55e", color: "#000", border: "none" }}>Next →</button>}
            {feedback && <span style={{ fontSize: 16 }}>{feedback}</span>}
          </div>
        </div>

        <div style={{ marginTop: 12, fontSize: 12, color: "#666" }}>
          Put the words in the right order to make a sentence!
        </div>
      </div>
    </div>
  );
}

const btn: React.CSSProperties = { padding: "6px 14px", borderRadius: 6, border: "1px solid #555", background: "#1a1a2e", color: "#fff", cursor: "pointer", fontSize: 13 };
