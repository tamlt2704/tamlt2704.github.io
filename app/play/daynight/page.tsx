"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import Link from "next/link";
import { feature } from "topojson-client";
import type { Topology, GeometryCollection } from "topojson-specification";
import type { FeatureCollection, Geometry } from "geojson";

// Timezone entries: flag, name, UTC offset in minutes
const TIMEZONE_LIST = [
  { flag: "🇸🇬", name: "Singapore", offset: 480 },
  { flag: "🇨🇳", name: "China", offset: 480 },
  { flag: "🇲🇾", name: "Malaysia", offset: 480 },
  { flag: "🇻🇳", name: "Vietnam", offset: 420 },
  { flag: "🇯🇵", name: "Japan", offset: 540 },
  { flag: "🇰🇷", name: "South Korea", offset: 540 },
  { flag: "🇮🇳", name: "India", offset: 330 },
  { flag: "🇹🇭", name: "Thailand", offset: 420 },
  { flag: "🇵🇭", name: "Philippines", offset: 480 },
  { flag: "🇮🇩", name: "Indonesia (WIB)", offset: 420 },
  { flag: "🇦🇺", name: "Australia (AEST)", offset: 600 },
  { flag: "🇳🇿", name: "New Zealand", offset: 720 },
  { flag: "🇬🇧", name: "United Kingdom", offset: 0 },
  { flag: "🇩🇪", name: "Germany", offset: 60 },
  { flag: "🇫🇷", name: "France", offset: 60 },
  { flag: "🇺🇸", name: "US (Eastern)", offset: -300 },
  { flag: "🇺🇸", name: "US (Pacific)", offset: -480 },
  { flag: "🇨🇦", name: "Canada (Eastern)", offset: -300 },
  { flag: "🇧🇷", name: "Brazil", offset: -180 },
  { flag: "🇦🇪", name: "UAE", offset: 240 },
];

const DEFAULT_SELECTED = ["Singapore", "China", "Malaysia", "Vietnam"];

function formatTZ(now: Date, offsetMin: number) {
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const t = new Date(utc + offsetMin * 60000);
  const h = offsetMin / 60;
  const sign = h >= 0 ? "+" : "";
  return {
    time: t.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
    date: t.toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short" }),
    utc: `UTC${sign}${Number.isInteger(h) ? h : h.toFixed(1)}`,
  };
}

// Flat map dimensions
const MW = 960, MH = 480;
// Globe inset dimensions
const GS = 320, GR = 120, GCX = 160, GCY = 150;
const TOPO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json";

function getSunPosition(now: Date) {
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const d = utc / 86400000 - 10957.5;
  const g = ((357.529 + 0.98560028 * d) % 360) * Math.PI / 180;
  const q = (280.459 + 0.98564736 * d) % 360;
  const L = (q + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g)) % 360;
  const e = (23.439 - 0.00000036 * d) * Math.PI / 180;
  const decl = Math.asin(Math.sin(e) * Math.sin(L * Math.PI / 180));
  const hours = (utc / 3600000) % 24;
  const lon = -(hours / 24 * 360 - 180);
  return { lat: decl, lon: ((lon + 540) % 360 - 180) * Math.PI / 180 };
}

/* ── Flat map ── */

function flatXY(lon: number, lat: number): [number, number] {
  return [(lon + 180) / 360 * MW, (90 - lat) / 180 * MH];
}

function drawFlatRing(ctx: CanvasRenderingContext2D, coords: number[][][]) {
  for (const ring of coords) {
    ctx.beginPath();
    for (let i = 0; i < ring.length; i++) {
      const [x, y] = flatXY(ring[i][0], ring[i][1]);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fill();
  }
}

function drawFlatMap(ctx: CanvasRenderingContext2D, geo: FeatureCollection<Geometry>, now: Date) {
  ctx.fillStyle = "#1a3a5c";
  ctx.fillRect(0, 0, MW, MH);

  ctx.fillStyle = "#2e7d32";
  ctx.strokeStyle = "#1b5e20";
  ctx.lineWidth = 0.3;
  for (const f of geo.features) {
    const g = f.geometry;
    if (g.type === "Polygon") { drawFlatRing(ctx, g.coordinates); ctx.stroke(); }
    else if (g.type === "MultiPolygon") {
      for (const poly of g.coordinates) { drawFlatRing(ctx, poly); ctx.stroke(); }
    }
  }

  // Grid
  ctx.strokeStyle = "#ffffff0d";
  ctx.lineWidth = 0.5;
  for (let lon = -180; lon <= 180; lon += 30) {
    const x = (lon + 180) / 360 * MW;
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, MH); ctx.stroke();
  }
  for (let lat = -90; lat <= 90; lat += 30) {
    const y = (90 - lat) / 180 * MH;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(MW, y); ctx.stroke();
  }
  ctx.strokeStyle = "#ffffff18";
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, MH / 2); ctx.lineTo(MW, MH / 2); ctx.stroke();

  // Night shading
  const sun = getSunPosition(now);
  const imgData = ctx.getImageData(0, 0, MW, MH);
  const d = imgData.data;
  for (let y = 0; y < MH; y++) {
    const lat = Math.PI / 2 - (y / MH) * Math.PI;
    const sinL = Math.sin(lat), cosL = Math.cos(lat);
    for (let x = 0; x < MW; x++) {
      const lon = (x / MW) * 2 * Math.PI - Math.PI;
      const cosA = sinL * Math.sin(sun.lat) + cosL * Math.cos(sun.lat) * Math.cos(lon - sun.lon);
      if (cosA < 0.1) {
        const i = (y * MW + x) * 4;
        const f = cosA < -0.1 ? 0.75 : (0.1 - cosA) / 0.2 * 0.75;
        d[i] = d[i] * (1 - f) | 0;
        d[i + 1] = d[i + 1] * (1 - f) | 0;
        d[i + 2] = d[i + 2] * (1 - f) | 0;
      }
    }
  }
  ctx.putImageData(imgData, 0, 0);

  // Terminator
  ctx.beginPath();
  ctx.strokeStyle = "#ffaa0055";
  ctx.lineWidth = 1.5;
  for (let py = 0; py < MH; py++) {
    const lat2 = Math.PI / 2 - (py / MH) * Math.PI;
    const cosLat2 = Math.cos(lat2);
    if (Math.abs(cosLat2) < 0.001) continue;
    const cosH = -Math.tan(sun.lat) * Math.tan(lat2);
    if (Math.abs(cosH) > 1) continue;
    const hA = Math.acos(cosH);
    const x1 = ((sun.lon + hA + Math.PI) / (2 * Math.PI)) * MW;
    const x2 = ((sun.lon - hA + Math.PI) / (2 * Math.PI)) * MW;
    ctx.moveTo(((x1 % MW) + MW) % MW, py); ctx.lineTo(((x1 % MW) + MW) % MW + 0.5, py + 1);
    ctx.moveTo(((x2 % MW) + MW) % MW, py); ctx.lineTo(((x2 % MW) + MW) % MW + 0.5, py + 1);
  }
  ctx.stroke();

  // Sun marker
  const sx = ((sun.lon + Math.PI) / (2 * Math.PI)) * MW;
  const sy = ((Math.PI / 2 - sun.lat) / Math.PI) * MH;
  ctx.beginPath(); ctx.arc(sx, sy, 8, 0, Math.PI * 2);
  ctx.fillStyle = "#ffdd00"; ctx.fill();
  ctx.strokeStyle = "#ff8800"; ctx.lineWidth = 2; ctx.stroke();
}

/* ── Globe inset ── */

function globeProject(lon: number, lat: number, rLon: number, rLat: number): [number, number, boolean] {
  const lam = lon * Math.PI / 180 - rLon;
  const phi = lat * Math.PI / 180;
  const cosc = Math.sin(rLat) * Math.sin(phi) + Math.cos(rLat) * Math.cos(phi) * Math.cos(lam);
  if (cosc < 0) return [0, 0, false];
  return [
    GCX + GR * Math.cos(phi) * Math.sin(lam),
    GCY - GR * (Math.cos(rLat) * Math.sin(phi) - Math.sin(rLat) * Math.cos(phi) * Math.cos(lam)),
    true,
  ];
}

function drawGlobe(ctx: CanvasRenderingContext2D, geo: FeatureCollection<Geometry>, now: Date, rLon: number, rLat: number) {
  ctx.fillStyle = "#0a0a1a";
  ctx.fillRect(0, 0, GS, GS);

  const sun = getSunPosition(now);

  // Stars
  for (let i = 0; i < 80; i++) {
    ctx.fillStyle = `rgba(255,255,255,${0.2 + ((i * 3571) % 100) / 200})`;
    ctx.fillRect((42 * (i + 1) * 7919) % GS, (42 * (i + 1) * 6271) % GS, 1, 1);
  }

  // Ocean sphere
  ctx.beginPath(); ctx.arc(GCX, GCY, GR, 0, Math.PI * 2);
  ctx.fillStyle = "#0d2847"; ctx.fill();

  // Land
  ctx.fillStyle = "#1a6b1a";
  ctx.strokeStyle = "#0f4f0f";
  ctx.lineWidth = 0.4;
  const drawCoords = (coords: number[][][]) => {
    for (const ring of coords) {
      ctx.beginPath();
      let started = false, prevVis = false;
      for (let i = 0; i < ring.length; i++) {
        const [px, py, vis] = globeProject(ring[i][0], ring[i][1], rLon, rLat);
        if (vis) {
          if (!started || !prevVis) { ctx.moveTo(px, py); started = true; }
          else ctx.lineTo(px, py);
        }
        prevVis = vis;
      }
      ctx.closePath(); ctx.fill(); ctx.stroke();
    }
  };
  for (const f of geo.features) {
    const g = f.geometry;
    if (g.type === "Polygon") drawCoords(g.coordinates);
    else if (g.type === "MultiPolygon") for (const p of g.coordinates) drawCoords(p);
  }

  // Grid
  ctx.strokeStyle = "#ffffff10";
  ctx.lineWidth = 0.3;
  for (let lon = -180; lon < 180; lon += 30) {
    ctx.beginPath(); let s = false;
    for (let lat = -90; lat <= 90; lat += 3) {
      const [px, py, v] = globeProject(lon, lat, rLon, rLat);
      if (v) { s ? ctx.lineTo(px, py) : ctx.moveTo(px, py); s = true; } else s = false;
    }
    ctx.stroke();
  }
  for (let lat = -60; lat <= 60; lat += 30) {
    ctx.beginPath(); let s = false;
    for (let lon = -180; lon <= 180; lon += 3) {
      const [px, py, v] = globeProject(lon, lat, rLon, rLat);
      if (v) { s ? ctx.lineTo(px, py) : ctx.moveTo(px, py); s = true; } else s = false;
    }
    ctx.stroke();
  }

  // Night pixel shading
  const ox = GCX - GR, oy = GCY - GR, sz = GR * 2;
  const imgData = ctx.getImageData(ox, oy, sz, sz);
  const d = imgData.data;
  const r2 = GR * GR;
  for (let py = 0; py < sz; py++) {
    for (let px = 0; px < sz; px++) {
      const dx = px - GR, dy = py - GR;
      if (dx * dx + dy * dy > r2) continue;
      const dz = Math.sqrt(r2 - dx * dx - dy * dy);
      const x3 = dx / GR, y3 = -dy / GR, z3 = dz / GR;
      const cosR2 = Math.cos(rLat), sinR2 = Math.sin(rLat);
      const yr = cosR2 * y3 + sinR2 * z3;
      const zr = -sinR2 * y3 + cosR2 * z3;
      const lat = Math.asin(yr);
      const lon = Math.atan2(x3, zr) + rLon;
      const cosA = Math.sin(lat) * Math.sin(sun.lat) + Math.cos(lat) * Math.cos(sun.lat) * Math.cos(lon - sun.lon);
      if (cosA < 0.1) {
        const i = (py * sz + px) * 4;
        const f = cosA < -0.1 ? 0.72 : (0.1 - cosA) / 0.2 * 0.72;
        d[i] = d[i] * (1 - f) | 0;
        d[i + 1] = d[i + 1] * (1 - f) | 0;
        d[i + 2] = d[i + 2] * (1 - f) | 0;
      }
    }
  }
  ctx.putImageData(imgData, ox, oy);

  // Atmosphere
  const atm = ctx.createRadialGradient(GCX, GCY, GR - 2, GCX, GCY, GR + 12);
  atm.addColorStop(0, "rgba(100,180,255,0)");
  atm.addColorStop(0.5, "rgba(80,160,255,0.1)");
  atm.addColorStop(1, "rgba(60,120,255,0)");
  ctx.beginPath(); ctx.arc(GCX, GCY, GR + 12, 0, Math.PI * 2);
  ctx.fillStyle = atm; ctx.fill();

  // Sun sphere
  const sunDist = 280;
  const sunSX = GCX + sunDist * Math.cos(sun.lat) * Math.sin(sun.lon - rLon);
  const sunSY = GCY - sunDist * (Math.cos(rLat) * Math.sin(sun.lat) - Math.sin(rLat) * Math.cos(sun.lat) * Math.cos(sun.lon - rLon));
  const sR = 18;

  // Glow
  const glow = ctx.createRadialGradient(sunSX, sunSY, sR * 0.3, sunSX, sunSY, sR * 3.5);
  glow.addColorStop(0, "rgba(255,220,50,0.35)");
  glow.addColorStop(0.3, "rgba(255,180,30,0.12)");
  glow.addColorStop(1, "rgba(255,140,0,0)");
  ctx.beginPath(); ctx.arc(sunSX, sunSY, sR * 3.5, 0, Math.PI * 2);
  ctx.fillStyle = glow; ctx.fill();

  // Body
  const sg = ctx.createRadialGradient(sunSX - sR * 0.2, sunSY - sR * 0.2, sR * 0.1, sunSX, sunSY, sR);
  sg.addColorStop(0, "#ffffee");
  sg.addColorStop(0.4, "#ffee44");
  sg.addColorStop(0.8, "#ffaa00");
  sg.addColorStop(1, "#ff6600");
  ctx.beginPath(); ctx.arc(sunSX, sunSY, sR, 0, Math.PI * 2);
  ctx.fillStyle = sg; ctx.fill();

  // Light beam
  ctx.beginPath();
  ctx.strokeStyle = "rgba(255,220,80,0.05)";
  ctx.lineWidth = 40;
  ctx.moveTo(sunSX, sunSY); ctx.lineTo(GCX, GCY);
  ctx.stroke();
}

/* ── Page ── */

export default function DayNightPage() {
  const mapRef = useRef<HTMLCanvasElement>(null);
  const globeRef = useRef<HTMLCanvasElement>(null);
  const geoRef = useRef<FeatureCollection<Geometry> | null>(null);
  const [clock, setClock] = useState("");
  const [loading, setLoading] = useState(true);
  const [offsetMin, setOffsetMin] = useState(0);
  const [selected, setSelected] = useState<string[]>(DEFAULT_SELECTED);
  const [tzTimes, setTzTimes] = useState<Record<string, { time: string; date: string; utc: string }>>({});
  const [rotLon, setRotLon] = useState(0);
  const [rotLat, setRotLat] = useState(0.3);
  const [globeMin, setGlobeMin] = useState(false);
  const dragging = useRef(false);
  const lastMouse = useRef({ x: 0, y: 0 });

  useEffect(() => {
    fetch(TOPO_URL)
      .then(r => r.json())
      .then((topo: Topology<{ land: GeometryCollection }>) => {
        geoRef.current = feature(topo, topo.objects.land) as unknown as FeatureCollection<Geometry>;
        setLoading(false);
      });
  }, []);

  const draw = useCallback(() => {
    if (!geoRef.current) return;
    const now = new Date(Date.now() + offsetMin * 60000);
    const mapCtx = mapRef.current?.getContext("2d");
    if (mapCtx) drawFlatMap(mapCtx, geoRef.current, now);
    const globeCtx = globeRef.current?.getContext("2d");
    if (globeCtx) drawGlobe(globeCtx, geoRef.current, now, rotLon, rotLat);
    const gmt8 = new Date(now.getTime() + (now.getTimezoneOffset() + 480) * 60000);
    setClock(
      gmt8.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) +
      " GMT+8 · " +
      gmt8.toLocaleDateString("en-GB", { weekday: "short", year: "numeric", month: "short", day: "numeric" })
    );
    const times: Record<string, { time: string; date: string; utc: string }> = {};
    for (const tz of TIMEZONE_LIST) {
      if (selected.includes(tz.name)) times[tz.name] = formatTZ(now, tz.offset);
    }
    setTzTimes(times);
  }, [offsetMin, rotLon, rotLat, selected]);

  useEffect(() => {
    if (loading) return;
    draw();
    const id = setInterval(draw, 1000);
    return () => clearInterval(id);
  }, [loading, draw]);

  const onMouseDown = (e: React.MouseEvent) => { dragging.current = true; lastMouse.current = { x: e.clientX, y: e.clientY }; };
  const onMouseMove = (e: React.MouseEvent) => {
    if (!dragging.current) return;
    const dx = e.clientX - lastMouse.current.x, dy = e.clientY - lastMouse.current.y;
    lastMouse.current = { x: e.clientX, y: e.clientY };
    setRotLon(p => p - dx * 0.008);
    setRotLat(p => Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, p + dy * 0.008)));
  };
  const onMouseUp = () => { dragging.current = false; };

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", padding: 20, position: "relative" }}>
      <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 12 }}>
        <Link href="/" style={{ padding: "5px 12px", borderRadius: 6, border: "1px solid #555", background: "#1a1a2e", color: "#fff", textDecoration: "none", fontSize: 13 }}>🏠 Home</Link>
        <h1 style={{ color: "#fff", fontSize: "1.3rem", margin: 0 }}>🌍 Day & Night Map</h1>
      </div>
      <div style={{ color: "#4da6ff", fontSize: 16, fontFamily: "monospace", marginBottom: 6 }}>🕐 {clock}</div>

      {/* Timezone clocks */}
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 10, flexWrap: "wrap", justifyContent: "center" }}>
        {selected.map(name => {
          const tz = TIMEZONE_LIST.find(t => t.name === name);
          const t = tzTimes[name];
          if (!tz || !t) return null;
          return (
            <div key={name} style={{ background: "#1a1a2e", border: "1px solid #333", borderRadius: 8, padding: "4px 10px", display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ fontSize: 18 }}>{tz.flag}</span>
              <div style={{ lineHeight: 1.3 }}>
                <div style={{ color: "#ccc", fontSize: 11 }}>{tz.name}</div>
                <div style={{ color: "#4da6ff", fontSize: 13, fontFamily: "monospace", fontWeight: 600 }}>{t.time}</div>
                <div style={{ color: "#666", fontSize: 9 }}>{t.date} · {t.utc}</div>
              </div>
              <span
                onClick={() => setSelected(s => s.filter(n => n !== name))}
                style={{ color: "#555", cursor: "pointer", fontSize: 11, marginLeft: 2 }}
              >✕</span>
            </div>
          );
        })}
        <select
          value=""
          onChange={e => {
            if (e.target.value && !selected.includes(e.target.value)) setSelected(s => [...s, e.target.value]);
          }}
          style={{ background: "#1a1a2e", color: "#4da6ff", border: "1px solid #444", borderRadius: 6, padding: "4px 8px", fontSize: 12, cursor: "pointer" }}
        >
          <option value="">+ Add timezone</option>
          {TIMEZONE_LIST.filter(tz => !selected.includes(tz.name)).map(tz => (
            <option key={tz.name} value={tz.name}>{tz.flag} {tz.name}</option>
          ))}
        </select>
      </div>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4, marginBottom: 12, background: "#1a1a2e", borderRadius: 8, padding: "8px 14px", border: "1px solid #333" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ color: "#888", fontSize: 11 }}>-24h</span>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 400 }}>
            <input type="range" min={-1440} max={1440} step={10} value={offsetMin}
              onChange={e => setOffsetMin(Number(e.target.value))}
              list="time-ticks"
              style={{ width: "100%", accentColor: "#4da6ff" }} />
            <datalist id="time-ticks">
              {Array.from({ length: 49 }, (_, i) => (i - 24) * 60).map(v => (
                <option key={v} value={v} />
              ))}
            </datalist>
            <div style={{ display: "flex", justifyContent: "space-between", width: "100%", padding: "0 2px" }}>
              {[-24, -18, -12, -6, 0, 6, 12, 18, 24].map(h => (
                <span
                  key={h}
                  onClick={() => setOffsetMin(h * 60)}
                  style={{ color: h === 0 ? "#4da6ff" : "#666", fontSize: 9, cursor: "pointer", userSelect: "none", minWidth: 20, textAlign: "center" }}
                >
                  {h === 0 ? "Now" : `${h > 0 ? "+" : ""}${h}h`}
                </span>
              ))}
            </div>
          </div>
          <span style={{ color: "#888", fontSize: 11 }}>+24h</span>
          <span style={{ color: "#4da6ff", fontSize: 12, minWidth: 60, textAlign: "center" }}>
            {offsetMin === 0 ? "Now" : `${offsetMin > 0 ? "+" : ""}${(offsetMin / 60).toFixed(1)}h`}
          </span>
          {offsetMin !== 0 && (
            <button onClick={() => setOffsetMin(0)} style={{ padding: "2px 8px", borderRadius: 4, border: "1px solid #555", background: "#0a0a1a", color: "#4da6ff", cursor: "pointer", fontSize: 11 }}>Now</button>
          )}
        </div>
      </div>
      {loading && <div style={{ color: "#888", margin: 40 }}>Loading world map…</div>}
      <canvas ref={mapRef} width={MW} height={MH}
        style={{ maxWidth: "100%", borderRadius: 8, border: "1px solid #333", display: loading ? "none" : "block" }} />
      <div style={{ color: "#888", fontSize: 11, marginTop: 10 }}>
        ☀️ Sun position · Orange line = terminator · Dark areas = nighttime
      </div>

      {/* Globe inset */}
      <div style={{
        position: "fixed", bottom: 16, right: 16,
        background: "#0a0a1acc", border: "1px solid #333", borderRadius: 14,
        padding: 10, backdropFilter: "blur(10px)", zIndex: 20,
        display: loading ? "none" : "block",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: globeMin ? 0 : 4 }}>
          <span style={{ color: "#fff", fontSize: 12, fontWeight: 600 }}>🔭 3D Globe</span>
          <span
            onClick={() => setGlobeMin(g => !g)}
            style={{ color: "#888", cursor: "pointer", fontSize: 14, lineHeight: 1, padding: "0 2px" }}
            title={globeMin ? "Expand" : "Minimize"}
          >{globeMin ? "＋" : "−"}</span>
        </div>
        {!globeMin && (
          <>
            <canvas ref={globeRef} width={GS} height={GS}
              onMouseDown={onMouseDown} onMouseMove={onMouseMove} onMouseUp={onMouseUp} onMouseLeave={onMouseUp}
              style={{ width: GS, height: GS, cursor: "grab", borderRadius: 8 }} />
            <div style={{ color: "#666", fontSize: 10, textAlign: "center", marginTop: 4 }}>Drag to rotate</div>
          </>
        )}
      </div>
    </div>
  );
}
