"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";

const planets = [
  { name: "Mercury", color: "#b5b5b5", size: 8, orbit: 80, period: 4.1, facts: [
    "Smallest planet in the solar system",
    "One day on Mercury lasts 59 Earth days",
    "Temperature swings from -180°C to 430°C",
    "Has no moons and no rings",
    "Closest planet to the Sun at 58M km",
  ]},
  { name: "Venus", color: "#e8cda0", size: 10, orbit: 130, period: 10.5, facts: [
    "Hottest planet at 465°C — hotter than Mercury!",
    "Spins backwards (retrograde rotation)",
    "A day on Venus is longer than its year",
    "Thick CO₂ atmosphere with sulfuric acid clouds",
    "Often called Earth's evil twin",
  ]},
  { name: "Earth", color: "#4da6ff", size: 12, orbit: 190, period: 17, facts: [
    "Only known planet with life",
    "71% of the surface is covered in water",
    "Has a powerful magnetic field protecting us",
    "Tilted 23.5° giving us seasons",
    "Orbits the Sun at 107,000 km/h",
  ]},
  { name: "Mars", color: "#e07040", size: 9, orbit: 260, period: 32, facts: [
    "Home to Olympus Mons — tallest volcano in the solar system",
    "Has the longest canyon: Valles Marineris (4,000 km)",
    "A year on Mars is 687 Earth days",
    "Has two tiny moons: Phobos and Deimos",
    "Sunsets on Mars appear blue",
  ]},
  { name: "Jupiter", color: "#d4a56a", size: 26, orbit: 360, period: 60, facts: [
    "Largest planet — 1,300 Earths could fit inside",
    "Great Red Spot is a storm raging for 350+ years",
    "Has 95 known moons including Ganymede (largest moon)",
    "Rotates in just ~10 hours — fastest spinning planet",
    "Acts as a cosmic vacuum cleaner, deflecting asteroids",
  ]},
  { name: "Saturn", color: "#e8d590", size: 22, orbit: 470, period: 80, facts: [
    "Its rings span 282,000 km but are only ~10m thick",
    "Least dense planet — it would float in water!",
    "Has 146 known moons, including Titan with an atmosphere",
    "Winds can reach 1,800 km/h",
    "A hexagonal storm sits at its north pole",
  ]},
  { name: "Uranus", color: "#7de8e8", size: 16, orbit: 580, period: 110, facts: [
    "Tilted 98° — it rolls around the Sun on its side",
    "Coldest planetary atmosphere at -224°C",
    "Has 13 faint rings",
    "Takes 84 Earth years to orbit the Sun",
    "Discovered in 1781 by William Herschel",
  ]},
  { name: "Neptune", color: "#4466ff", size: 15, orbit: 680, period: 140, facts: [
    "Strongest winds in the solar system at 2,100 km/h",
    "Takes 165 Earth years to orbit the Sun",
    "Has 16 known moons — Triton orbits backwards",
    "Was predicted mathematically before being observed",
    "Its blue color comes from methane in the atmosphere",
  ]},
];

const CENTER = 700;

const EARTH_IDX = 2;
const MOON_ORBIT = 20;
const MOON_SIZE = 4;
const MOON_PERIOD_RATIO = 1 / 12;

const SPEED_PRESETS = [
  { label: "0.25×", value: 0.25 },
  { label: "0.5×", value: 0.5 },
  { label: "1×", value: 1 },
  { label: "2×", value: 2 },
  { label: "5×", value: 5 },
  { label: "10×", value: 10 },
];

export default function SolarSystem() {
  const [selected, setSelected] = useState<number | null>(null);
  const [paused, setPaused] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [positions, setPositions] = useState(() =>
    planets.map(() => ({ angle: Math.random() * Math.PI * 2 }))
  );
  const [moonAngle, setMoonAngle] = useState(0);

  const dragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const lastTime = useRef(0);
  const pausedRef = useRef(paused);
  const speedRef = useRef(speed);
  pausedRef.current = paused;
  speedRef.current = speed;

  // Animation loop — Kepler's 2nd law: dM/dt is constant (mean anomaly increases uniformly)
  useEffect(() => {
    let raf: number;
    const tick = (time: number) => {
      if (lastTime.current) {
        const dt = (time - lastTime.current) / 1000;
        if (!pausedRef.current) {
          const s = speedRef.current;
          setPositions(prev =>
            prev.map((p, i) => ({
              angle: p.angle + (2 * Math.PI / planets[i].period) * dt * s,
            }))
          );
          setMoonAngle(prev => prev + (2 * Math.PI / (planets[EARTH_IDX].period * MOON_PERIOD_RATIO)) * dt * s);
        }
      }
      lastTime.current = time;
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  // Moon phase canvas
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const CV = 320;
  const EARTH_R = 18;
  const MOON_R = 9;
  const MOON_ORBIT_R = 70;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;
    canvas.width = CV;
    canvas.height = CV;
    const cx = CV / 2, cy = CV / 2;

    const eAngle = positions[EARTH_IDX].angle;
    const mAngle = moonAngle;
    const sunAngle = eAngle + Math.PI;

    ctx.clearRect(0, 0, CV, CV);

    const mx = cx + MOON_ORBIT_R * Math.cos(mAngle);
    const my = cy + MOON_ORBIT_R * Math.sin(mAngle);

    // Sun position
    const SUN_DIST = 140;
    const sx = cx + SUN_DIST * Math.cos(sunAngle);
    const sy = cy + SUN_DIST * Math.sin(sunAngle);

    // Sun rays: parallel light from sun direction through the scene
    // Light travels from Sun toward Earth (opposite of sunAngle)
    const lightAngle = sunAngle + Math.PI; // direction light travels (from sun toward earth)
    const perpX = Math.sin(lightAngle);
    const perpY = -Math.cos(lightAngle);

    // Draw ray beam from sun side to far side
    const rayStartX = sx;
    const rayStartY = sy;
    const rayEndX = cx - (SUN_DIST + 40) * Math.cos(sunAngle);
    const rayEndY = cy - (SUN_DIST + 40) * Math.sin(sunAngle);

    const rayGrad = ctx.createLinearGradient(rayStartX, rayStartY, rayEndX, rayEndY);
    rayGrad.addColorStop(0, "#ff8c0044");
    rayGrad.addColorStop(0.4, "#ff8c0018");
    rayGrad.addColorStop(1, "#ff8c0006");

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(rayStartX + perpX * 4, rayStartY + perpY * 4);
    ctx.lineTo(rayStartX - perpX * 4, rayStartY - perpY * 4);
    ctx.lineTo(rayEndX - perpX * 22, rayEndY - perpY * 22);
    ctx.lineTo(rayEndX + perpX * 22, rayEndY + perpY * 22);
    ctx.closePath();
    ctx.fillStyle = rayGrad;
    ctx.fill();
    ctx.restore();

    // Dashed center ray line
    ctx.save();
    ctx.setLineDash([4, 6]);
    ctx.beginPath();
    ctx.moveTo(rayStartX, rayStartY);
    ctx.lineTo(rayEndX, rayEndY);
    ctx.strokeStyle = "#ff8c0033";
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();

    // Sun glow
    const sunGlow = ctx.createRadialGradient(sx, sy, 2, sx, sy, 20);
    sunGlow.addColorStop(0, "#fff700");
    sunGlow.addColorStop(0.5, "#ff8c00");
    sunGlow.addColorStop(1, "#ff8c0000");
    ctx.beginPath();
    ctx.arc(sx, sy, 20, 0, Math.PI * 2);
    ctx.fillStyle = sunGlow;
    ctx.fill();
    ctx.beginPath();
    ctx.arc(sx, sy, 7, 0, Math.PI * 2);
    ctx.fillStyle = "#ffcc00";
    ctx.fill();
    ctx.font = "11px sans-serif";
    ctx.fillStyle = "#ff8c00cc";
    ctx.fillText("Sun ☀", sx - 14, sy - 14);

    // Moon orbit ring + label
    ctx.beginPath();
    ctx.arc(cx, cy, MOON_ORBIT_R, 0, Math.PI * 2);
    ctx.strokeStyle = "#ffffff18";
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.save();
    ctx.font = "10px sans-serif";
    ctx.fillStyle = "#ffffff30";
    const la = -Math.PI / 4;
    const lx = cx + MOON_ORBIT_R * Math.cos(la);
    const ly = cy + MOON_ORBIT_R * Math.sin(la);
    ctx.translate(lx, ly);
    ctx.rotate(la + Math.PI / 2);
    ctx.fillText("Moon orbit", -24, -4);
    ctx.restore();

    // Earth
    const earthGrad = ctx.createRadialGradient(cx - 3, cy - 3, 1, cx, cy, EARTH_R);
    earthGrad.addColorStop(0, "#6ec6ff");
    earthGrad.addColorStop(1, "#2a6faa");
    ctx.beginPath();
    ctx.arc(cx, cy, EARTH_R, 0, Math.PI * 2);
    ctx.fillStyle = earthGrad;
    ctx.fill();
    ctx.font = "bold 12px sans-serif";
    ctx.fillStyle = "#4da6ff";
    ctx.fillText("🌍 Earth", cx - 22, cy + EARTH_R + 16);

    // Moon shading — simple: lit side faces Sun, shadow when behind Earth
    // Angle from Moon to Sun
    const moonToSunAngle = Math.atan2(sy - my, sx - mx);

    // Draw base Moon (fully lit)
    ctx.beginPath();
    ctx.arc(mx, my, MOON_R, 0, Math.PI * 2);
    ctx.fillStyle = "#e8e8d0";
    ctx.fill();

    // Draw dark half on the side away from Sun
    ctx.save();
    ctx.beginPath();
    ctx.arc(mx, my, MOON_R, 0, Math.PI * 2);
    ctx.clip();
    // Dark semicircle on the far side from Sun
    ctx.beginPath();
    ctx.arc(mx, my, MOON_R + 1, moonToSunAngle + Math.PI / 2, moonToSunAngle - Math.PI / 2);
    ctx.closePath();
    ctx.fillStyle = "#222";
    ctx.fill();
    ctx.restore();

    // Earth shadow — when Moon is behind Earth (between Earth and anti-Sun side)
    // Check if Moon is roughly behind Earth relative to Sun
    const moonFromEarth = Math.atan2(my - cy, mx - cx);
    const sunFromEarth = Math.atan2(sy - cy, sx - cx);
    const antiSunAngle2 = sunFromEarth + Math.PI;
    let shadowDiff = moonFromEarth - antiSunAngle2;
    shadowDiff = ((shadowDiff + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
    const moonDist = Math.sqrt((mx - cx) * (mx - cx) + (my - cy) * (my - cy));
    // If Moon is roughly behind Earth (within ~20°) and close, darken it
    if (Math.abs(shadowDiff) < 0.35 && moonDist < MOON_ORBIT_R + 5) {
      const shadowStrength = 1 - Math.abs(shadowDiff) / 0.35;
      ctx.beginPath();
      ctx.arc(mx, my, MOON_R, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(10,10,26,${0.7 * shadowStrength})`;
      ctx.fill();
    }

    // Moon outline
    ctx.beginPath();
    ctx.arc(mx, my, MOON_R, 0, Math.PI * 2);
    ctx.strokeStyle = "#ffffff20";
    ctx.lineWidth = 0.5;
    ctx.stroke();

    ctx.font = "11px sans-serif";
    ctx.fillStyle = "#ccc";
    ctx.fillText("🌙 Moon", mx - 18, my - MOON_R - 6);

    // Phase name — simple for kids
    let elongation = moonFromEarth - sunFromEarth;
    elongation = ((elongation % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
    let phaseName = "";
    if (elongation < Math.PI * 0.125 || elongation > Math.PI * 1.875) phaseName = "🌑 New Moon";
    else if (elongation < Math.PI * 0.375) phaseName = "🌒 Waxing Crescent";
    else if (elongation < Math.PI * 0.625) phaseName = "🌓 First Quarter";
    else if (elongation < Math.PI * 0.875) phaseName = "🌔 Waxing Gibbous";
    else if (elongation < Math.PI * 1.125) phaseName = "🌕 Full Moon";
    else if (elongation < Math.PI * 1.375) phaseName = "🌖 Waning Gibbous";
    else if (elongation < Math.PI * 1.625) phaseName = "🌗 Last Quarter";
    else phaseName = "🌘 Waning Crescent";
    ctx.font = "13px sans-serif";
    ctx.fillStyle = "#ffffffcc";
    ctx.fillText(phaseName, 10, CV - 10);
  }, [positions, moonAngle]);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    setZoom(z => Math.min(8, Math.max(0.3, z * (e.deltaY < 0 ? 1.15 : 0.87))));
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 0) return;
    dragging.current = true;
    dragStart.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
  }, [pan]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragging.current) return;
    setPan({ x: e.clientX - dragStart.current.x, y: e.clientY - dragStart.current.y });
  }, []);

  const handleMouseUp = useCallback(() => { dragging.current = false; }, []);

  const focusEarth = () => { setZoom(4); setPan({ x: 0, y: 0 }); };
  const resetView = () => { setZoom(1); setPan({ x: 0, y: 0 }); };

  // Compute positions on circles
  const planetXY = planets.map((p, i) => ({
    x: Math.cos(positions[i].angle) * p.orbit,
    y: Math.sin(positions[i].angle) * p.orbit,
  }));
  const earthXY = planetXY[EARTH_IDX];
  const moonPos = {
    x: earthXY.x + Math.cos(moonAngle) * MOON_ORBIT,
    y: earthXY.y + Math.sin(moonAngle) * MOON_ORBIT,
  };

  return (
    <div style={{ background: "#0a0a1a", height: "100vh", display: "flex", flexDirection: "column", alignItems: "center", overflow: "hidden", position: "relative" }}>
      {/* Top bar */}
      <div style={{ display: "flex", gap: 8, alignItems: "center", margin: "8px 0 4px", zIndex: 10, flexWrap: "wrap", justifyContent: "center", padding: "0 12px" }}>
        <Link href="/" style={{ ...btnStyle, textDecoration: "none", display: "inline-block" }}>🏠 Home</Link>
        <h1 style={{ color: "#fff", fontSize: "1.3rem", margin: 0 }}>☀️ Solar System</h1>
        <button onClick={() => setPaused(!paused)} style={btnStyle}>
          {paused ? "▶ Play" : "⏸ Pause"}
        </button>
        <button onClick={focusEarth} style={btnStyle}>🌍 Focus Earth</button>
        <button onClick={resetView} style={btnStyle}>↩ Reset</button>
      </div>

      {/* Speed control bar */}
      <div style={{
        display: "flex", alignItems: "center", gap: 10, zIndex: 10,
        background: "#1a1a2e", borderRadius: 8, padding: "6px 14px", margin: "4px 0 6px",
        border: "1px solid #333",
      }}>
        <span style={{ color: "#888", fontSize: 11 }}>Speed</span>
        {SPEED_PRESETS.map(p => (
          <button
            key={p.value}
            onClick={() => setSpeed(p.value)}
            style={{
              ...btnSmall,
              background: speed === p.value ? "#4da6ff" : "#0a0a1a",
              color: speed === p.value ? "#000" : "#aaa",
              borderColor: speed === p.value ? "#4da6ff" : "#444",
            }}
          >
            {p.label}
          </button>
        ))}
        <input
          type="range" min={0.1} max={10} step={0.1} value={speed}
          onChange={e => setSpeed(parseFloat(e.target.value))}
          style={{ width: 100, accentColor: "#4da6ff" }}
        />
        <span style={{ color: "#4da6ff", fontSize: 12, minWidth: 40 }}>{speed.toFixed(1)}×</span>
      </div>

      {selected !== null && (
        <div style={{
          position: "fixed", top: 16, left: "50%", transform: "translateX(-50%)",
          background: "#1a1a3aee", border: `1px solid ${planets[selected].color}44`,
          borderRadius: 12, padding: "14px 20px", maxWidth: 360, zIndex: 30,
          backdropFilter: "blur(8px)",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <span style={{ color: planets[selected].color, fontWeight: 700, fontSize: 15 }}>
              {planets[selected].name}
            </span>
            <span
              onClick={() => setSelected(null)}
              style={{ color: "#666", cursor: "pointer", fontSize: 13 }}
            >✕</span>
          </div>
          <ul style={{ margin: 0, paddingLeft: 18, color: "#ccc", fontSize: 12, lineHeight: 1.7 }}>
            {planets[selected].facts.map((f, j) => <li key={j}>{f}</li>)}
          </ul>
        </div>
      )}

      {/* Viewport */}
      <div
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ flex: 1, width: "100%", cursor: "grab", overflow: "hidden", display: "flex", alignItems: "center", justifyContent: "center" }}
      >
        <div style={{
          position: "relative", width: CENTER * 2, height: CENTER * 2, flexShrink: 0,
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          transition: dragging.current ? "none" : "transform 0.4s ease-out",
          transformOrigin: "center center",
        }}>
          {/* Sun */}
          <div style={{
            position: "absolute", left: "50%", top: "50%", transform: "translate(-50%,-50%)",
            width: 40, height: 40, borderRadius: "50%",
            background: "radial-gradient(circle, #fff700, #ff8c00)", boxShadow: "0 0 40px #ff8c00, 0 0 80px #ff660066",
          }} />

          {/* Circular orbit paths with labels on top */}
          <svg width={CENTER * 2} height={CENTER * 2} style={{ position: "absolute", left: 0, top: 0 }}>
            {planets.map((p, i) => {
              const diagAngle = (-3 * Math.PI) / 4;
              const nextOrbit = i < planets.length - 1 ? planets[i + 1].orbit : p.orbit + 40;
              const labelR = p.orbit + (nextOrbit - p.orbit) / 2;
              const lx = CENTER + labelR * Math.cos(diagAngle);
              const ly = CENTER + labelR * Math.sin(diagAngle);
              return (
              <g key={p.name + "-orbit"}>
                <circle
                  cx={CENTER} cy={CENTER} r={p.orbit}
                  fill="none" stroke={p.name === "Earth" ? "#4da6ff20" : "#ffffff12"} strokeWidth={1}
                  style={{ pointerEvents: "none" }}
                />
                <text
                  x={lx} y={ly}
                  fill={selected === i ? p.color : (p.name === "Earth" ? "#4da6ff66" : "#ffffff33")}
                  fontSize={10} fontFamily="sans-serif"
                  textAnchor="middle" dominantBaseline="middle"
                  transform={`rotate(-45, ${lx}, ${ly})`}
                  style={{ cursor: "pointer", pointerEvents: "auto" }}
                  onClick={() => setSelected(selected === i ? null : i)}
                >
                  {p.name}
                </text>
              </g>
              );
            })}
          </svg>

          {/* Planets */}
          {planets.map((p, i) => {
            const { x: px, y: py } = planetXY[i];
            const x = CENTER + px;
            const y = CENTER + py;
            return (
              <div key={p.name}>
                <div
                  title={p.name}
                  style={{
                    position: "absolute",
                    left: x - p.size / 2, top: y - p.size / 2,
                    width: p.size, height: p.size, borderRadius: "50%",
                    background: p.color, pointerEvents: "none",
                    boxShadow: selected === i ? `0 0 12px ${p.color}` : "none",
                  }}
                />
                {i === EARTH_IDX && (
                  <>
                    {/* Moon orbit ring */}
                    <svg width={MOON_ORBIT * 2} height={MOON_ORBIT * 2} style={{
                      position: "absolute",
                      left: x - MOON_ORBIT, top: y - MOON_ORBIT,
                      pointerEvents: "none", overflow: "visible",
                    }}>
                      <circle cx={MOON_ORBIT} cy={MOON_ORBIT} r={MOON_ORBIT} fill="none" stroke="#ffffff15" strokeWidth={1} />
                      <text x={MOON_ORBIT * 2 + 2} y={MOON_ORBIT + 3} fill="#aaaaaa44" fontSize={7} fontFamily="sans-serif">Moon orbit</text>
                    </svg>
                    {/* Moon */}
                    <div style={{
                      position: "absolute",
                      left: CENTER + moonPos.x - MOON_SIZE / 2,
                      top: CENTER + moonPos.y - MOON_SIZE / 2,
                      width: MOON_SIZE, height: MOON_SIZE, borderRadius: "50%",
                      background: "#ccc", pointerEvents: "none",
                    }} />
                    <div style={{
                      position: "absolute",
                      left: CENTER + moonPos.x + 4,
                      top: CENTER + moonPos.y - 10,
                      color: "#aaa", fontSize: 8, whiteSpace: "nowrap", pointerEvents: "none",
                    }}>
                      Moon
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Moon phase inset */}
      <div style={{
        position: "fixed", bottom: 16, right: 16,
        background: "#0a0a1acc", border: "1px solid #333", borderRadius: 14,
        padding: 12, backdropFilter: "blur(10px)", zIndex: 20,
      }}>
        <div style={{ color: "#fff", fontSize: 13, textAlign: "center", marginBottom: 6, fontWeight: 600 }}>
          🔭 Earth–Moon View
        </div>
        <canvas ref={canvasRef} style={{ width: 320, height: 320 }} />
      </div>

      {/* Zoom indicator */}
      <div style={{ position: "fixed", bottom: 24, left: 20, color: "#555", fontSize: 12, zIndex: 20 }}>
        {zoom.toFixed(1)}×
      </div>
      <div style={{ position: "fixed", bottom: 24, left: 60, color: "#666", fontSize: 11, zIndex: 20 }}>
        Scroll to zoom · Drag to pan
      </div>
    </div>
  );
}

const btnStyle: React.CSSProperties = {
  padding: "5px 12px", borderRadius: 6, border: "1px solid #555",
  background: "#1a1a2e", color: "#fff", cursor: "pointer", fontSize: 13,
};

const btnSmall: React.CSSProperties = {
  padding: "3px 8px", borderRadius: 4, border: "1px solid #444",
  cursor: "pointer", fontSize: 11, fontWeight: 600,
};
