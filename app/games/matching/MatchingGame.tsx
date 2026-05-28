"use client";

import {
  FaReact,
  FaDocker,
  FaGithub,
  FaPython,
  FaNode,
  FaAws,
  FaLinux,
  FaJava,
  FaRust,
  FaVuejs,
  FaAngular,
  FaPhp,
  FaSwift,
  FaDatabase,
  FaServer,
  FaCss3,
  FaHtml5,
  FaJs,
  FaNpm,
  FaGitAlt,
  FaWindows,
  FaApple,
  FaAndroid,
  FaSlack,
  FaFigma,
  FaCloud,
  FaLock,
  FaBolt,
  FaCog,
  FaRocket,
  FaStar,
  FaHeart,
  FaFire,
  FaGlobe,
  FaCode,
  FaBug,
  FaWifi,
  FaCamera,
  FaMusic,
  FaGamepad,
} from "react-icons/fa";
import {
  SiTypescript,
  SiKubernetes,
  SiTerraform,
  SiGo,
  SiDotnet,
  SiElixir,
  SiRuby,
  SiCplusplus,
  SiFlutter,
  SiFirebase,
  SiMongodb,
  SiPostgresql,
  SiRedis,
  SiGraphql,
  SiWebpack,
  SiVite,
  SiNextdotjs,
  SiTailwindcss,
  SiVercel,
  SiNginx,
} from "react-icons/si";
import {
  GiTreasureMap,
  GiCat,
  GiSittingDog,
  GiElephant,
  GiDolphin,
  GiFrog,
  GiSpiderFace,
  GiSnake,
  GiBat,
  GiOwl,
  GiPenguin,
  GiRabbit,
  GiTurtle,
  GiSpermWhale,
  GiSeahorse,
  GiButterfly,
  GiSheep,
  GiMonkey,
  GiLion,
  GiEagleHead,
  GiHummingbird,
  GiPolarBear,
  GiSquirrel,
  GiCrab,
  GiJellyfish,
  GiScorpion,
  GiRooster,
  GiGoat,
  GiCamel,
  GiHorseHead,
  GiPanda,
  GiDeer,
  GiRhinocerosHorn,
  GiHedgehog,
  GiOctopus,
  GiSwan,
  GiParrotHead,
  GiCrocJaws,
  GiWool,
  GiMouse,
  GiFlamingo,
  GiSeaTurtle,
  GiSnail,
  GiLadybug,
  GiBeehive,
  GiSoccerBall,
  GiBasketballBall,
  GiTennisRacket,
  GiBoxingGlove,
  GiCycling,
  GiMountainClimbing,
  GiRunningShoe,
  GiSwimfins,
  GiWeightLiftingUp,
  GiArcheryTarget,
  GiPingPongBat,
  GiGolfFlag,
  GiSkier,
  GiSurfBoard,
  GiHockey,
  GiDart,
  GiChessKnight,
  GiBowlingStrike,
  GiBaseballBat,
  GiAmericanFootballBall,
  GiVolleyballBall,
  GiShuttlecock,
  GiKatana,
  GiHamburger,
  GiPizzaSlice,
  GiCupcake,
  GiIceCreamCone,
  GiCherry,
  GiGrapes,
  GiWatermelon,
  GiCarrot,
  GiCorn,
  GiMushroomGills,
  GiChocolateBar,
  GiCookie,
  GiCoffeeCup,
  GiWineGlass,
  GiBeerStein,
  GiNoodles,
  GiSushis,
  GiTacos,
  GiCroissant,
  GiDonut,
  GiCandyCanes,
  GiShinyApple,
  GiPear,
  GiBanana,
  GiStrawberry,
  GiAvocado,
  GiCheeseWedge,
  GiBroccoli,
  GiHotDog,
} from "react-icons/gi";
import type { IconType } from "react-icons";
import { useState, useCallback } from "react";

const TOPICS: Record<string, { label: string; icons: IconType[] }> = {
  tech: {
    label: "💻 Tech",
    icons: [
      FaReact,
      FaDocker,
      FaGithub,
      FaPython,
      SiTypescript,
      SiKubernetes,
      FaNode,
      FaAws,
      FaLinux,
      FaJava,
      FaRust,
      FaVuejs,
      FaAngular,
      FaPhp,
      FaSwift,
      FaDatabase,
      FaServer,
      FaCss3,
      FaHtml5,
      FaJs,
      FaNpm,
      FaGitAlt,
      FaWindows,
      FaApple,
      FaAndroid,
      FaSlack,
      FaFigma,
      FaCloud,
      FaLock,
      FaBolt,
      FaCog,
      FaRocket,
      FaStar,
      FaHeart,
      FaFire,
      FaGlobe,
      FaCode,
      FaBug,
      FaWifi,
      FaCamera,
      FaMusic,
      FaGamepad,
      SiTerraform,
      SiGo,
      SiDotnet,
      SiElixir,
      SiRuby,
      SiCplusplus,
      SiFlutter,
      SiFirebase,
      SiMongodb,
      SiPostgresql,
      SiRedis,
      SiGraphql,
      SiWebpack,
      SiVite,
      SiNextdotjs,
      SiTailwindcss,
      SiVercel,
      SiNginx,
    ],
  },
  animals: {
    label: "🐾 Animals",
    icons: [
      GiCat,
      GiSittingDog,
      GiElephant,
      GiDolphin,
      GiFrog,
      GiSpiderFace,
      GiSnake,
      GiBat,
      GiOwl,
      GiPenguin,
      GiRabbit,
      GiTurtle,
      GiSpermWhale,
      GiSeahorse,
      GiButterfly,
      GiSheep,
      GiMonkey,
      GiLion,
      GiEagleHead,
      GiHummingbird,
      GiPolarBear,
      GiSquirrel,
      GiCrab,
      GiJellyfish,
      GiScorpion,
      GiRooster,
      GiGoat,
      GiCamel,
      GiHorseHead,
      GiPanda,
      GiDeer,
      GiRhinocerosHorn,
      GiHedgehog,
      GiOctopus,
      GiSwan,
      GiParrotHead,
      GiCrocJaws,
      GiWool,
      GiMouse,
      GiFlamingo,
      GiSeaTurtle,
      GiSnail,
      GiLadybug,
      GiBeehive,
    ],
  },
  sports: {
    label: "⚽ Sports",
    icons: [
      GiSoccerBall,
      GiBasketballBall,
      GiTennisRacket,
      GiBoxingGlove,
      GiCycling,
      GiMountainClimbing,
      GiRunningShoe,
      GiSwimfins,
      GiWeightLiftingUp,
      GiArcheryTarget,
      GiPingPongBat,
      GiGolfFlag,
      GiSkier,
      GiSurfBoard,
      GiHockey,
      GiDart,
      GiChessKnight,
      GiBowlingStrike,
      GiBaseballBat,
      GiAmericanFootballBall,
      GiVolleyballBall,
      GiShuttlecock,
      GiKatana,
    ],
  },
  food: {
    label: "🍕 Food",
    icons: [
      GiHamburger,
      GiPizzaSlice,
      GiCupcake,
      GiIceCreamCone,
      GiCherry,
      GiGrapes,
      GiWatermelon,
      GiCarrot,
      GiCorn,
      GiMushroomGills,
      GiChocolateBar,
      GiCookie,
      GiCoffeeCup,
      GiWineGlass,
      GiBeerStein,
      GiNoodles,
      GiSushis,
      GiTacos,
      GiCroissant,
      GiDonut,
      GiCandyCanes,
      GiShinyApple,
      GiPear,
      GiBanana,
      GiStrawberry,
      GiAvocado,
      GiCheeseWedge,
      GiBroccoli,
      GiHotDog,
    ],
  },
};

const COLORS = [
  "#e11d48",
  "#2563eb",
  "#16a34a",
  "#9333ea",
  "#ea580c",
  "#0891b2",
  "#4f46e5",
  "#dc2626",
];

function getIconConfig(index: number, icons: IconType[]) {
  const iconIdx = index % icons.length;
  const colorIdx = Math.floor(index / icons.length) % COLORS.length;
  return { Icon: icons[iconIdx], color: COLORS[colorIdx] };
}

interface Card {
  id: number;
  pairIndex: number;
  flipped: boolean;
  matched: boolean;
  isSecret: boolean;
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function buildCards(size: number): Card[] {
  const total = size * size;
  const isOdd = total % 2 !== 0;
  const pairCount = Math.floor(total / 2);
  const indices = [...Array(pairCount).keys()];
  const pairs: (number | "secret")[] = [...indices, ...indices];
  if (isOdd) pairs.push("secret");
  const shuffled = shuffle(pairs);
  return shuffled.map((val, id) => ({
    id,
    pairIndex: val === "secret" ? -1 : val,
    flipped: false,
    matched: false,
    isSecret: val === "secret",
  }));
}

const SIZES = Array.from({ length: 17 }, (_, i) => i + 4);

export default function MatchingGame() {
  const [size, setSize] = useState(4);
  const [selectedTopics, setSelectedTopics] = useState<string[]>(["animals"]);
  const [cards, setCards] = useState(() => buildCards(4));
  const [selected, setSelected] = useState<number[]>([]);
  const [moves, setMoves] = useState(0);
  const [locked, setLocked] = useState(false);
  const [revealAll, setRevealAll] = useState(false);
  const [secretFound, setSecretFound] = useState(false);
  const [bw, setBw] = useState(false);

  const icons = selectedTopics.flatMap((t) => TOPICS[t].icons);
  const toggleTopic = (key: string) => {
    const next = selectedTopics.includes(key)
      ? selectedTopics.filter((t) => t !== key)
      : [...selectedTopics, key];
    if (next.length === 0) return; // must have at least one
    setSelectedTopics(next);
    setCards(buildCards(size));
    setSelected([]);
    setMoves(0);
    setLocked(false);
    setRevealAll(false);
    setSecretFound(false);
  };
  const hasSecret = (size * size) % 2 !== 0;
  const won = cards.every((c) => c.matched || c.isSecret);

  const handleFlip = useCallback(
    (id: number) => {
      if (locked || revealAll) return;
      const card = cards[id];
      if (card.flipped || card.matched) return;
      if (card.isSecret) {
        setCards((prev) => prev.map((c) => (c.id === id ? { ...c, flipped: true } : c)));
        setSecretFound(true);
        setMoves((m) => m + 1);
        return;
      }
      const flipped = cards.map((c) => (c.id === id ? { ...c, flipped: true } : c));

      if (selected.length === 0) {
        setCards(flipped);
        setSelected([id]);
      } else {
        // Second card flipped — check match
        const firstId = selected[0];
        setMoves((m) => m + 1);
        if (flipped[firstId].pairIndex === flipped[id].pairIndex) {
          setCards(
            flipped.map((c) => (c.id === firstId || c.id === id ? { ...c, matched: true } : c)),
          );
          setSelected([]);
        } else {
          setCards(flipped);
          setSelected([]);
          setLocked(true);
          setTimeout(() => {
            setCards((prev) =>
              prev.map((c) => (c.id === firstId || c.id === id ? { ...c, flipped: false } : c)),
            );
            setLocked(false);
          }, 800);
        }
      }
    },
    [cards, locked, revealAll, selected],
  );

  const reset = (newSize?: number) => {
    const s = newSize ?? size;
    setSize(s);
    setCards(buildCards(s));
    setSelected([]);
    setMoves(0);
    setLocked(false);
    setRevealAll(false);
    setSecretFound(false);
  };

  const cardPx = Math.floor(720 / size) - 4;
  const iconSize = Math.floor(cardPx * 0.6);

  return (
    <div className="flex flex-col items-center gap-4 p-4">
      <style>{`
        @media print {
          body * { visibility: hidden; }
          #print-grid, #print-grid * { visibility: visible; }
          #print-grid { position: absolute; top: 0; left: 0; width: 190mm; padding: 5mm; }
          .no-print { display: none !important; }
        }
      `}</style>

      <h1 className="no-print text-2xl font-bold">Memory Matching Game</h1>

      <div className="no-print flex flex-wrap items-center gap-3">
        <div className="flex flex-wrap gap-2">
          {Object.entries(TOPICS).map(([key, { label }]) => (
            <label key={key} className="flex cursor-pointer items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={selectedTopics.includes(key)}
                onChange={() => toggleTopic(key)}
                className="rounded"
              />
              {label}
            </label>
          ))}
        </div>
        <select
          value={size}
          onChange={(e) => reset(Number(e.target.value))}
          className="rounded border px-2 py-1"
        >
          {SIZES.map((s) => (
            <option key={s} value={s}>
              {s}×{s} ({Math.floor((s * s) / 2)} pairs{(s * s) % 2 !== 0 ? " + 🗝️" : ""})
            </option>
          ))}
        </select>
        <button
          onClick={() => setRevealAll((r) => !r)}
          className="rounded bg-gray-600 px-3 py-1 text-sm text-white hover:bg-gray-700"
        >
          {revealAll ? "Hide All" : "Reveal All"}
        </button>
        <button
          onClick={() => window.print()}
          className="rounded bg-purple-600 px-3 py-1 text-sm text-white hover:bg-purple-700"
        >
          🖨️ Print
        </button>
        <label className="flex cursor-pointer items-center gap-1 text-sm">
          <input
            type="checkbox"
            checked={bw}
            onChange={() => setBw((v) => !v)}
            className="rounded"
          />
          B&W
        </label>
      </div>

      <div className="no-print flex gap-4 text-sm text-gray-600">
        <span>Moves: {moves}</span>
        {hasSecret && (
          <span className={secretFound ? "font-semibold text-amber-600" : ""}>
            Secret: {secretFound ? "✅ Found!" : "🗝️ Hidden..."}
          </span>
        )}
      </div>

      {won && (
        <p className="no-print text-lg font-semibold text-green-600">
          🎉 You won in {moves} moves!
        </p>
      )}

      <div
        id="print-grid"
        className="grid gap-1"
        style={{ gridTemplateColumns: `repeat(${size}, 1fr)` }}
      >
        {cards.map((card) => {
          const show = revealAll || card.flipped || card.matched;
          let content;
          if (show && card.isSecret) {
            content = (
              <GiTreasureMap
                className={bw ? "text-black" : "text-amber-500"}
                style={{ fontSize: `${iconSize}px` }}
              />
            );
          } else if (show) {
            const { Icon, color } = getIconConfig(card.pairIndex, icons);
            content = <Icon style={{ color: bw ? "#000" : color, fontSize: `${iconSize}px` }} />;
          } else {
            content = <span className="text-gray-400">?</span>;
          }
          return (
            <button
              key={card.id}
              onClick={() => handleFlip(card.id)}
              style={{ width: `${cardPx}px`, height: `${cardPx}px` }}
              className={`flex items-center justify-center rounded border-2 transition-all duration-200 ${
                card.isSecret && card.flipped
                  ? "animate-pulse border-amber-400 bg-amber-50"
                  : card.matched
                    ? "border-green-400 bg-green-50"
                    : show
                      ? "border-blue-400 bg-blue-50"
                      : "border-gray-300 bg-gray-100 hover:bg-gray-200"
              }`}
              aria-label={
                card.isSecret && show
                  ? "Secret card"
                  : show
                    ? `Card ${card.pairIndex}`
                    : "Hidden card"
              }
            >
              {content}
            </button>
          );
        })}
      </div>

      <button
        onClick={() => reset()}
        className="no-print rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Reset
      </button>
    </div>
  );
}
