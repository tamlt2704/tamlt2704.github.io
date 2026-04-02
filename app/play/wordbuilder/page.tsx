"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import Link from "next/link";
import { sfxPop, sfxRemove, sfxCorrect, sfxWrong, sfxFanfare } from "@/app/play/sfx";

type Lang = "en" | "cn" | "vn";

const WORDS = [
  { word: "CAT",   en: "🐱 A furry pet that purrs",           cn: "🐱 一种会发出咕噜声的毛茸茸的宠物", vn: "🐱 Một con vật nuôi lông xù biết kêu gừ gừ" },
  { word: "DOG",   en: "🐶 A loyal pet that barks",           cn: "🐶 一种忠诚的会叫的宠物",           vn: "🐶 Một con vật nuôi trung thành biết sủa" },
  { word: "SUN",   en: "☀️ It shines in the sky",              cn: "☀️ 它在天空中闪耀",                  vn: "☀️ Nó tỏa sáng trên bầu trời" },
  { word: "FISH",  en: "🐟 It swims in water",                cn: "🐟 它在水里游泳",                   vn: "🐟 Nó bơi trong nước" },
  { word: "TREE",  en: "🌳 It has leaves and branches",       cn: "🌳 它有叶子和树枝",                 vn: "🌳 Nó có lá và cành" },
  { word: "MOON",  en: "🌙 You see it at night",              cn: "🌙 你在晚上能看到它",               vn: "🌙 Bạn nhìn thấy nó vào ban đêm" },
  { word: "STAR",  en: "⭐ It twinkles in the sky",            cn: "⭐ 它在天空中闪烁",                  vn: "⭐ Nó lấp lánh trên bầu trời" },
  { word: "BIRD",  en: "🐦 It can fly",                       cn: "🐦 它会飞",                         vn: "🐦 Nó có thể bay" },
  { word: "FROG",  en: "🐸 It jumps and says ribbit",         cn: "🐸 它会跳，会呱呱叫",               vn: "🐸 Nó nhảy và kêu ộp ộp" },
  { word: "CAKE",  en: "🎂 A sweet birthday treat",           cn: "🎂 一种甜甜的生日美食",             vn: "🎂 Một món ngọt trong ngày sinh nhật" },
  { word: "RAIN",  en: "🌧️ Water falling from clouds",        cn: "🌧️ 从云中落下的水",                 vn: "🌧️ Nước rơi từ những đám mây" },
  { word: "BOOK",  en: "📖 You read stories in it",           cn: "📖 你在里面读故事",                 vn: "📖 Bạn đọc truyện trong đó" },
  { word: "SHIP",  en: "🚢 It sails on the ocean",            cn: "🚢 它在海洋上航行",                 vn: "🚢 Nó đi trên đại dương" },
  { word: "LAMP",  en: "💡 It gives you light",               cn: "💡 它给你光明",                     vn: "💡 Nó cho bạn ánh sáng" },
  { word: "DRUM",  en: "🥁 You hit it to make music",         cn: "🥁 你敲它来演奏音乐",               vn: "🥁 Bạn đánh nó để tạo ra âm nhạc" },
  { word: "SNOW",  en: "❄️ Cold white flakes in winter",       cn: "❄️ 冬天里冰冷的白色雪花",            vn: "❄️ Những bông tuyết trắng lạnh vào mùa đông" },
  { word: "APPLE", en: "🍎 A red or green fruit",             cn: "🍎 一种红色或绿色的水果",           vn: "🍎 Một loại trái cây màu đỏ hoặc xanh" },
  { word: "HOUSE", en: "🏠 Where you live",                   cn: "🏠 你住的地方",                     vn: "🏠 Nơi bạn sống" },
  { word: "WATER", en: "💧 You drink it every day",           cn: "💧 你每天都喝它",                   vn: "💧 Bạn uống nó mỗi ngày" },
  { word: "CLOUD", en: "☁️ White and fluffy in the sky",       cn: "☁️ 天空中白色蓬松的东西",            vn: "☁️ Trắng và bông xốp trên bầu trời" },
];

const UI: Record<Lang, {
  title: string; home: string; score: string; best: string; streak: string;
  bestStreak: string; check: string; hint: string; answer: string; reset: string;
  next: string; correct: string; tryAgain: string; revealed: string;
  points: string; hintsUsed: string; pts: string; tip: string;
}> = {
  en: {
    title: "🔤 Word Builder", home: "🏠 Home", score: "⭐ Score", best: "🏆 Best",
    streak: "streak", bestStreak: "Best streak", check: "✅ Check", hint: "💡 Hint",
    answer: "👁 Answer", reset: "↩ Reset", next: "Next Word →",
    correct: "🎉 Correct!", tryAgain: "❌ Try again!", revealed: "👁 Answer revealed",
    points: "points", hintsUsed: "Hints used", pts: "pts",
    tip: "Click letters to place them. Click placed letters to remove. Be fast for bonus points! 🔥",
  },
  cn: {
    title: "🔤 拼单词", home: "🏠 首页", score: "⭐ 分数", best: "🏆 最高",
    streak: "连胜", bestStreak: "最佳连胜", check: "✅ 检查", hint: "💡 提示",
    answer: "👁 答案", reset: "↩ 重置", next: "下一个 →",
    correct: "🎉 正确！", tryAgain: "❌ 再试一次！", revealed: "👁 已显示答案",
    points: "分", hintsUsed: "已用提示", pts: "分",
    tip: "点击字母放置。点击已放置的字母移除。速度越快，奖励越多！🔥",
  },
  vn: {
    title: "🔤 Xếp Chữ", home: "🏠 Trang chủ", score: "⭐ Điểm", best: "🏆 Cao nhất",
    streak: "chuỗi", bestStreak: "Chuỗi tốt nhất", check: "✅ Kiểm tra", hint: "💡 Gợi ý",
    answer: "👁 Đáp án", reset: "↩ Làm lại", next: "Từ tiếp theo →",
    correct: "🎉 Chính xác!", tryAgain: "❌ Thử lại!", revealed: "👁 Đã hiện đáp án",
    points: "điểm", hintsUsed: "Đã dùng gợi ý", pts: "điểm",
    tip: "Nhấn chữ cái để đặt. Nhấn chữ đã đặt để gỡ. Nhanh hơn để được thêm điểm! 🔥",
  },
};

const LANG_LABELS: Record<Lang, string> = { en: "EN", cn: "中文", vn: "VN" };

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function randIdx(exclude: number) {
  let i;
  do { i = Math.floor(Math.random() * WORDS.length); } while (i === exclude && WORDS.length > 1);
  return i;
}

export default function WordBuilderPage() {
  const [lang, setLang] = useState<Lang>("en");
  const [wordIdx, setWordIdx] = useState(() => randIdx(-1));
  const [placed, setPlaced] = useState<(string | null)[]>(() => Array(WORDS[0].word.length).fill(null));
  const [available, setAvailable] = useState<{ letter: string; id: number }[]>(() =>
    shuffle(WORDS[0].word.split("").map((l, i) => ({ letter: l, id: i })))
  );
  const [initialized, setInitialized] = useState(false);
  const [score, setScore] = useState(0);
  const [highScore, setHighScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [bestStreak, setBestStreak] = useState(0);
  const [feedback, setFeedback] = useState("");
  const [lastPoints, setLastPoints] = useState(0);
  const [muted, setMuted] = useState(false);
  const [hintsUsed, setHintsUsed] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const roundStart = useRef(Date.now());
  const mutedRef = useRef(false);
  useEffect(() => { mutedRef.current = muted; }, [muted]);

  const t = UI[lang];
  const currentWord = WORDS[wordIdx];
  const hint = currentWord[lang];

  useEffect(() => {
    try {
      const saved = localStorage.getItem("wb_highscore");
      if (saved) setHighScore(parseInt(saved));
    } catch { /* noop */ }
  }, []);

  const saveHigh = (s: number) => {
    if (s > highScore) {
      setHighScore(s);
      try { localStorage.setItem("wb_highscore", String(s)); } catch { /* noop */ }
    }
  };

  const sfx = useCallback((fn: () => void) => { if (!mutedRef.current) fn(); }, []);

  // Initialize first random word on mount
  useEffect(() => {
    if (!initialized) { initWord(randIdx(-1)); setInitialized(true); }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const initWord = useCallback((idx: number) => {
    const w = WORDS[idx];
    setWordIdx(idx);
    setPlaced(Array(w.word.length).fill(null));
    const extras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").filter(l => !w.word.includes(l));
    const distractors = shuffle(extras).slice(0, Math.min(3, extras.length));
    const all = shuffle([...w.word.split(""), ...distractors].map((l, i) => ({ letter: l, id: i })));
    setAvailable(all);
    setFeedback("");
    setLastPoints(0);
    setHintsUsed(0);
    setRevealed(false);
    roundStart.current = Date.now();
  }, []);

  const placeLetter = (tile: { letter: string; id: number }) => {
    const slot = placed.indexOf(null);
    if (slot < 0) return;
    sfx(sfxPop);
    setPlaced(prev => { const p = [...prev]; p[slot] = tile.letter; return p; });
    setAvailable(prev => prev.filter(t => t.id !== tile.id));
  };

  const removeLetter = (slot: number) => {
    if (placed[slot] === null) return;
    sfx(sfxRemove);
    const letter = placed[slot]!;
    setPlaced(prev => { const p = [...prev]; p[slot] = null; return p; });
    setAvailable(prev => [...prev, { letter, id: Date.now() + Math.random() }]);
  };

  const giveHint = () => {
    if (revealed || feedback) return;
    const slot = placed.indexOf(null);
    if (slot < 0) return;
    const correctLetter = currentWord.word[slot];
    const tile = available.find(ti => ti.letter === correctLetter);
    if (tile) {
      sfx(sfxPop);
      setPlaced(prev => { const p = [...prev]; p[slot] = tile.letter; return p; });
      setAvailable(prev => prev.filter(ti => ti.id !== tile.id));
    } else {
      sfx(sfxPop);
      setPlaced(prev => { const p = [...prev]; p[slot] = correctLetter; return p; });
    }
    setHintsUsed(h => h + 1);
  };

  const showAnswer = () => {
    if (revealed || feedback.startsWith("🎉")) return;
    setRevealed(true);
    setPlaced(currentWord.word.split(""));
    setAvailable([]);
    setFeedback(t.revealed);
    setStreak(0);
    sfx(sfxRemove);
  };

  const check = () => {
    if (placed.join("") === currentWord.word) {
      const elapsed = (Date.now() - roundStart.current) / 1000;
      const timeBonus = Math.max(0, Math.round(20 - elapsed));
      const lengthBonus = currentWord.word.length * 2;
      const newStreak = streak + 1;
      const streakBonus = Math.min(newStreak * 5, 50);
      const hintPenalty = hintsUsed * 5;
      const pts = Math.max(1, 10 + lengthBonus + timeBonus + streakBonus - hintPenalty);

      setLastPoints(pts);
      setScore(s => { const ns = s + pts; saveHigh(ns); return ns; });
      setStreak(newStreak);
      if (newStreak > bestStreak) setBestStreak(newStreak);
      setFeedback(t.correct);

      if (newStreak > 0 && newStreak % 3 === 0) sfx(sfxFanfare);
      else sfx(sfxCorrect);
    } else {
      setStreak(0);
      setFeedback(t.tryAgain);
      sfx(sfxWrong);
    }
  };

  const next = () => initWord(randIdx(wordIdx));

  const streakColor = streak >= 5 ? "#f59e0b" : streak >= 3 ? "#8b5cf6" : "#3b82f6";
  const isCorrect = feedback === t.correct;
  const isRevealed = revealed;

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif" }}>
      {/* Header */}
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>{t.home}</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>{t.title}</h1>
        {/* Language toggle */}
        <div style={{ display: "flex", gap: 2, marginLeft: 4 }}>
          {(["en", "cn", "vn"] as Lang[]).map(l => (
            <button key={l} onClick={() => setLang(l)} style={{
              ...btn, padding: "3px 8px", fontSize: 11, fontWeight: 700,
              background: lang === l ? "#3b82f6" : "#1a1a2e",
              borderColor: lang === l ? "#3b82f6" : "#555",
            }}>
              {LANG_LABELS[l]}
            </button>
          ))}
        </div>
        <button onClick={() => setMuted(!muted)} style={{ ...btn, padding: "4px 10px", fontSize: 16 }}>
          {muted ? "🔇" : "🔊"}
        </button>
      </div>

      {/* Score bar */}
      <div style={{ display: "flex", gap: 16, padding: "0 16px 10px", flexWrap: "wrap", alignItems: "center", fontSize: 14 }}>
        <div>{t.score}: <b style={{ color: "#f59e0b", fontSize: 18 }}>{score}</b></div>
        <div style={{ color: "#666" }}>{t.best}: {highScore}</div>
        {streak > 0 && (
          <div style={{
            padding: "2px 10px", borderRadius: 20,
            background: streakColor + "22", border: `1px solid ${streakColor}`,
            color: streakColor, fontWeight: 700, fontSize: 13,
            animation: streak >= 3 ? "pulse 0.6s ease-in-out infinite" : undefined,
          }}>
            🔥 {streak} {t.streak}!
          </div>
        )}
        {bestStreak > 1 && <div style={{ color: "#555", fontSize: 12 }}>{t.bestStreak}: {bestStreak}</div>}
      </div>

      <div style={{ padding: "0 16px 16px", maxWidth: 600 }}>
        <div style={{ background: "#111827", borderRadius: 12, border: "1px solid #333", padding: 24 }}>
          {/* Hint */}
          <div style={{ fontSize: 20, marginBottom: 20, textAlign: "center" }}>{hint}</div>

          {/* Slots */}
          <div style={{ display: "flex", gap: 8, justifyContent: "center", marginBottom: 24 }}>
            {placed.map((letter, i) => {
              const correct = isCorrect;
              const wrong = feedback === t.tryAgain && letter && letter !== currentWord.word[i];
              return (
                <div
                  key={i}
                  onClick={() => removeLetter(i)}
                  style={{
                    width: 52, height: 58, borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 28, fontWeight: 700, transition: "all 0.15s",
                    background: correct ? "#22c55e22" : wrong ? "#ef444422" : "#1a1a2e",
                    border: correct ? "2px solid #22c55e" : wrong ? "2px solid #ef4444" : letter ? "2px solid #3b82f6" : "2px dashed #555",
                    cursor: letter ? "pointer" : "default",
                    color: correct ? "#22c55e" : "#fff",
                    transform: correct ? "scale(1.1)" : "scale(1)",
                  }}
                >
                  {letter || ""}
                </div>
              );
            })}
          </div>

          {/* Points popup */}
          {isCorrect && lastPoints > 0 && (
            <div style={{ textAlign: "center", marginBottom: 12, fontSize: 15, color: "#f59e0b", fontWeight: 700 }}>
              +{lastPoints} {t.points}!
            </div>
          )}

          {/* Available letters */}
          <div style={{ display: "flex", gap: 8, justifyContent: "center", flexWrap: "wrap", marginBottom: 20 }}>
            {available.map(tile => (
              <div
                key={tile.id}
                onClick={() => placeLetter(tile)}
                style={{
                  width: 46, height: 46, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 22, fontWeight: 700, background: "#1e293b", border: "1px solid #555",
                  cursor: "pointer", userSelect: "none", transition: "transform 0.1s",
                }}
                onMouseDown={e => (e.currentTarget.style.transform = "scale(0.9)")}
                onMouseUp={e => (e.currentTarget.style.transform = "scale(1)")}
                onMouseLeave={e => (e.currentTarget.style.transform = "scale(1)")}
              >
                {tile.letter}
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: 8, justifyContent: "center", alignItems: "center", flexWrap: "wrap" }}>
            {!isCorrect && !isRevealed && (
              <>
                <button onClick={check} disabled={placed.includes(null)} style={{ ...btn, background: "#3b82f6", border: "none", opacity: placed.includes(null) ? 0.4 : 1 }}>{t.check}</button>
                <button onClick={giveHint} disabled={!placed.includes(null)} style={{ ...btn, background: "#f59e0b22", borderColor: "#f59e0b", color: "#f59e0b", opacity: placed.includes(null) ? 1 : 0.4 }}>
                  {t.hint}{hintsUsed > 0 ? ` (${hintsUsed})` : ""}
                </button>
                <button onClick={showAnswer} style={{ ...btn, background: "#ef444422", borderColor: "#ef4444", color: "#ef4444" }}>{t.answer}</button>
                <button onClick={() => initWord(wordIdx)} style={btn}>{t.reset}</button>
              </>
            )}
            {(isCorrect || isRevealed) && <button onClick={next} style={{ ...btn, background: "#22c55e", color: "#000", border: "none" }}>{t.next}</button>}
            {feedback && <span style={{ fontSize: 16 }}>{feedback}</span>}
          </div>

          {hintsUsed > 0 && !feedback && (
            <div style={{ textAlign: "center", marginTop: 8, fontSize: 12, color: "#f59e0b88" }}>
              {t.hintsUsed}: {hintsUsed} (−{hintsUsed * 5} {t.pts})
            </div>
          )}
        </div>

        <div style={{ marginTop: 12, fontSize: 12, color: "#666" }}>{t.tip}</div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.08); }
        }
      `}</style>
    </div>
  );
}

const btn: React.CSSProperties = { padding: "6px 14px", borderRadius: 6, border: "1px solid #555", background: "#1a1a2e", color: "#fff", cursor: "pointer", fontSize: 13 };
