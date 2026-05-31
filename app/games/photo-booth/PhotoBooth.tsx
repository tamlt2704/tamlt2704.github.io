"use client";

import { useState, useRef, useEffect } from "react";

interface Frame {
  id: string;
  name: string;
  emoji: string;
  border: string;
  overlay?: string;
}

interface Sticker {
  id: string;
  emoji: string;
  x: number;
  y: number;
  size: number;
}

const FRAMES: Frame[] = [
  { id: "none", name: "No Frame", emoji: "📷", border: "none" },
  {
    id: "rainbow",
    name: "Rainbow",
    emoji: "🌈",
    border: "8px solid transparent",
    overlay: "linear-gradient(45deg, red, orange, yellow, green, blue, purple) border-box",
  },
  { id: "stars", name: "Stars", emoji: "⭐", border: "12px dashed gold" },
  { id: "hearts", name: "Hearts", emoji: "💖", border: "12px double hotpink" },
  { id: "ocean", name: "Ocean", emoji: "🌊", border: "10px solid #0ea5e9" },
  { id: "jungle", name: "Jungle", emoji: "🌿", border: "10px solid #22c55e" },
  { id: "space", name: "Space", emoji: "🚀", border: "10px solid #7c3aed" },
  { id: "candy", name: "Candy", emoji: "🍭", border: "12px dotted #ec4899" },
  { id: "fire", name: "Fire", emoji: "🔥", border: "10px solid #f97316" },
  { id: "ice", name: "Ice", emoji: "❄️", border: "10px double #67e8f9" },
];

const STICKER_OPTIONS = [
  "😎",
  "🤪",
  "👑",
  "🎀",
  "⭐",
  "💖",
  "🦄",
  "🌈",
  "🎉",
  "🦋",
  "🐱",
  "🐶",
  "🎸",
  "🍕",
  "👽",
  "🤖",
  "🧸",
  "🎈",
  "🌸",
  "🍩",
];

const EFFECTS = [
  { id: "none", name: "Normal", emoji: "📷", filter: "none" },
  { id: "grayscale", name: "B&W", emoji: "🖤", filter: "grayscale(100%)" },
  { id: "sepia", name: "Vintage", emoji: "📜", filter: "sepia(80%)" },
  { id: "bright", name: "Bright", emoji: "☀️", filter: "brightness(1.3) contrast(1.1)" },
  { id: "cool", name: "Cool", emoji: "🧊", filter: "hue-rotate(180deg) saturate(1.2)" },
  { id: "warm", name: "Warm", emoji: "🌅", filter: "hue-rotate(-20deg) saturate(1.4)" },
  { id: "pop", name: "Pop Art", emoji: "🎨", filter: "contrast(1.5) saturate(2)" },
  { id: "dreamy", name: "Dreamy", emoji: "💭", filter: "blur(1px) brightness(1.2)" },
];

export default function PhotoBooth() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [photo, setPhoto] = useState<string | null>(null);
  const [selectedFrame, setSelectedFrame] = useState<Frame>(FRAMES[0]);
  const [selectedEffect, setSelectedEffect] = useState(EFFECTS[0]);
  const [stickers, setStickers] = useState<Sticker[]>([]);
  const [countdown, setCountdown] = useState<number | null>(null);
  const [facingMode, setFacingMode] = useState<"user" | "environment">("user");
  const [tab, setTab] = useState<"frames" | "stickers" | "effects">("frames");
  const [dragging, setDragging] = useState<number | null>(null);
  const photoAreaRef = useRef<HTMLDivElement>(null);

  const streamRef = useRef<MediaStream | null>(null);

  const startCamera = async (mode: "user" | "environment" = facingMode) => {
    try {
      if (streamRef.current) streamRef.current.getTracks().forEach((t) => t.stop());
      const s = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: mode, width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      streamRef.current = s;
      if (videoRef.current) videoRef.current.srcObject = s;
    } catch {
      /* camera denied */
    }
  };

  useEffect(() => {
    startCamera("user");
    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const flipCamera = () => {
    const next = facingMode === "user" ? "environment" : "user";
    setFacingMode(next);
    startCamera(next);
  };

  const takePhoto = () => {
    setCountdown(3);
    let count = 3;
    const interval = setInterval(() => {
      count--;
      if (count === 0) {
        clearInterval(interval);
        setCountdown(null);
        captureFrame();
      } else {
        setCountdown(count);
      }
    }, 1000);
  };

  const captureFrame = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    if (facingMode === "user") {
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
    }
    ctx.filter = selectedEffect.filter;
    ctx.drawImage(video, 0, 0);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.filter = "none";

    setPhoto(canvas.toDataURL("image/png"));
  };

  const retake = () => {
    setPhoto(null);
    setStickers([]);
  };

  const addSticker = (emoji: string) => {
    setStickers((prev) => [...prev, { id: Date.now().toString(), emoji, x: 50, y: 50, size: 48 }]);
  };

  const removeSticker = (id: string) => {
    setStickers((prev) => prev.filter((s) => s.id !== id));
  };

  const handlePointerDown = (idx: number) => setDragging(idx);
  const handlePointerUp = () => setDragging(null);
  const handlePointerMove = (e: React.PointerEvent) => {
    if (dragging === null || !photoAreaRef.current) return;
    const rect = photoAreaRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    setStickers((prev) =>
      prev.map((s, i) =>
        i === dragging
          ? { ...s, x: Math.max(0, Math.min(100, x)), y: Math.max(0, Math.min(100, y)) }
          : s,
      ),
    );
  };

  const downloadPhoto = () => {
    if (!photo) return;
    const canvas = document.createElement("canvas");
    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.drawImage(img, 0, 0);

      // Draw stickers
      stickers.forEach((s) => {
        ctx.font = `${s.size * (img.width / 300)}px serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(s.emoji, (s.x / 100) * img.width, (s.y / 100) * img.height);
      });

      const link = document.createElement("a");
      link.download = `photobooth-${Date.now()}.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
    };
    img.src = photo;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-100 via-pink-50 to-yellow-50 p-4">
      <h1 className="mb-2 text-center text-3xl font-bold text-purple-700">📸 Fun Photo Booth!</h1>
      <p className="mb-4 text-center text-sm text-purple-500">
        Take photos, add frames & stickers!
      </p>

      {/* Camera / Photo area */}
      <div className="mx-auto max-w-md">
        <div
          ref={photoAreaRef}
          className="relative mx-auto aspect-[4/3] overflow-hidden rounded-2xl bg-black shadow-xl"
          style={{
            border: selectedFrame.border,
            backgroundImage: selectedFrame.overlay,
            backgroundOrigin: "border-box",
            backgroundClip: "border-box",
          }}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerLeave={handlePointerUp}
        >
          {!photo ? (
            <>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="h-full w-full object-cover"
                style={{
                  transform: facingMode === "user" ? "scaleX(-1)" : "none",
                  filter: selectedEffect.filter,
                }}
              />
              {countdown !== null && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                  <span className="animate-ping text-8xl font-bold text-white">{countdown}</span>
                </div>
              )}
            </>
          ) : (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={photo} alt="Captured" className="h-full w-full object-cover" />
          )}

          {/* Stickers overlay */}
          {stickers.map((s, i) => (
            <div
              key={s.id}
              className="absolute cursor-grab select-none active:cursor-grabbing"
              style={{
                left: `${s.x}%`,
                top: `${s.y}%`,
                transform: "translate(-50%, -50%)",
                fontSize: s.size,
              }}
              onPointerDown={() => handlePointerDown(i)}
            >
              {s.emoji}
              {photo && (
                <button
                  onClick={() => removeSticker(s.id)}
                  className="absolute -top-2 -right-2 h-5 w-5 rounded-full bg-red-500 text-center text-xs leading-5 text-white"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>

        {/* Camera controls */}
        <div className="mt-4 flex items-center justify-center gap-4">
          {!photo ? (
            <>
              <button
                onClick={flipCamera}
                className="rounded-full bg-purple-200 p-3 text-xl active:scale-90"
              >
                🔄
              </button>
              <button
                onClick={takePhoto}
                disabled={countdown !== null}
                className="rounded-full bg-red-500 p-5 text-2xl text-white shadow-lg ring-4 ring-red-200 active:scale-90 disabled:opacity-50"
              >
                📸
              </button>
              <div className="w-12" />
            </>
          ) : (
            <>
              <button
                onClick={retake}
                className="rounded-full bg-gray-200 px-5 py-3 font-bold text-gray-700 active:scale-90"
              >
                🔄 Retake
              </button>
              <button
                onClick={downloadPhoto}
                className="rounded-full bg-green-500 px-5 py-3 font-bold text-white shadow-lg active:scale-90"
              >
                💾 Save
              </button>
            </>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="mx-auto mt-6 max-w-md">
        <div className="flex overflow-hidden rounded-xl bg-white shadow">
          {(["frames", "stickers", "effects"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex-1 py-3 text-sm font-bold capitalize ${tab === t ? "bg-purple-500 text-white" : "text-purple-600"}`}
            >
              {t === "frames" ? "🖼️" : t === "stickers" ? "✨" : "🎨"} {t}
            </button>
          ))}
        </div>

        {/* Frames */}
        {tab === "frames" && (
          <div className="mt-3 grid grid-cols-5 gap-2">
            {FRAMES.map((f) => (
              <button
                key={f.id}
                onClick={() => setSelectedFrame(f)}
                className={`flex flex-col items-center rounded-xl p-2 transition ${selectedFrame.id === f.id ? "bg-purple-200 ring-2 ring-purple-500" : "bg-white"}`}
              >
                <span className="text-2xl">{f.emoji}</span>
                <span className="text-[10px] text-gray-600">{f.name}</span>
              </button>
            ))}
          </div>
        )}

        {/* Stickers */}
        {tab === "stickers" && (
          <div className="mt-3 grid grid-cols-5 gap-2">
            {STICKER_OPTIONS.map((emoji) => (
              <button
                key={emoji}
                onClick={() => addSticker(emoji)}
                className="rounded-xl bg-white p-3 text-3xl shadow active:scale-90 active:bg-yellow-100"
              >
                {emoji}
              </button>
            ))}
          </div>
        )}

        {/* Effects */}
        {tab === "effects" && (
          <div className="mt-3 grid grid-cols-4 gap-2">
            {EFFECTS.map((e) => (
              <button
                key={e.id}
                onClick={() => setSelectedEffect(e)}
                className={`flex flex-col items-center rounded-xl p-2 transition ${selectedEffect.id === e.id ? "bg-purple-200 ring-2 ring-purple-500" : "bg-white"}`}
              >
                <span className="text-2xl">{e.emoji}</span>
                <span className="text-[10px] text-gray-600">{e.name}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
