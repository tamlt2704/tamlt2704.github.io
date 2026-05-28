"use client";

import { useState, useEffect, useRef } from "react";
import Matter from "matter-js";

const { Engine, Render, Runner, Bodies, Composite, Mouse, MouseConstraint, Constraint, Events } =
  Matter;

type Demo =
  | "gravity"
  | "bounce"
  | "friction"
  | "pendulum"
  | "newton-cradle"
  | "stack"
  | "slingshot";

const DEMOS: { key: Demo; label: string; desc: string }[] = [
  {
    key: "gravity",
    label: "🍎 Gravity",
    desc: "Drop objects — see how mass doesn't affect fall speed",
  },
  { key: "bounce", label: "🏀 Bounce", desc: "Adjust restitution (bounciness) of objects" },
  { key: "friction", label: "🧊 Friction", desc: "Compare surfaces: ice vs rubber vs normal" },
  { key: "pendulum", label: "🕐 Pendulum", desc: "Simple pendulum — drag and release" },
  {
    key: "newton-cradle",
    label: "⚖️ Newton's Cradle",
    desc: "Conservation of momentum and energy",
  },
  { key: "stack", label: "📦 Stacking", desc: "Stack boxes and watch them topple" },
  { key: "slingshot", label: "🏹 Slingshot", desc: "Pull back and launch — projectile motion" },
];

export default function PhysicsLab() {
  const [demo, setDemo] = useState<Demo>("gravity");
  const [gravity, setGravity] = useState(1);
  const canvasRef = useRef<HTMLDivElement>(null);
  const engineRef = useRef<Matter.Engine | null>(null);
  const renderRef = useRef<Matter.Render | null>(null);
  const runnerRef = useRef<Matter.Runner | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    // Cleanup previous
    if (renderRef.current) Render.stop(renderRef.current);
    if (runnerRef.current) Runner.stop(runnerRef.current);
    if (engineRef.current) Engine.clear(engineRef.current);
    canvasRef.current.innerHTML = "";

    const w = 700,
      h = 500;
    const engine = Engine.create({ gravity: { x: 0, y: gravity } });
    const render = Render.create({
      element: canvasRef.current,
      engine,
      options: { width: w, height: h, wireframes: false, background: "#1a1a2e" },
    });

    // Ground + walls
    const ground = Bodies.rectangle(w / 2, h + 25, w + 100, 50, {
      isStatic: true,
      render: { fillStyle: "#4a5568" },
    });
    const wallL = Bodies.rectangle(-25, h / 2, 50, h, {
      isStatic: true,
      render: { fillStyle: "#4a5568" },
    });
    const wallR = Bodies.rectangle(w + 25, h / 2, 50, h, {
      isStatic: true,
      render: { fillStyle: "#4a5568" },
    });
    Composite.add(engine.world, [ground, wallL, wallR]);

    // Demo-specific setup
    setupDemo(demo, engine, w, h);

    // Mouse interaction
    const mouse = Mouse.create(render.canvas);
    const mc = MouseConstraint.create(engine, {
      mouse,
      constraint: { stiffness: 0.2, render: { visible: false } },
    });
    Composite.add(engine.world, mc);
    render.mouse = mouse;

    Render.run(render);
    const runner = Runner.create();
    Runner.run(runner, engine);

    engineRef.current = engine;
    renderRef.current = render;
    runnerRef.current = runner;

    return () => {
      Render.stop(render);
      Runner.stop(runner);
      Engine.clear(engine);
      render.canvas.remove();
    };
  }, [demo, gravity]);

  return (
    <div className="flex flex-col items-center gap-4 p-4">
      <h1 className="text-2xl font-bold">⚛️ Physics Lab — Matter.js</h1>

      <div className="flex flex-wrap justify-center gap-2">
        {DEMOS.map((d) => (
          <button
            key={d.key}
            onClick={() => setDemo(d.key)}
            className={`rounded-full px-3 py-1.5 text-sm transition ${
              demo === d.key
                ? "bg-blue-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            {d.label}
          </button>
        ))}
      </div>

      <p className="text-sm text-gray-500">{DEMOS.find((d) => d.key === demo)?.desc}</p>

      <div className="flex items-center gap-4 text-sm">
        <label>Gravity: {gravity.toFixed(1)}</label>
        <input
          type="range"
          min="0"
          max="3"
          step="0.1"
          value={gravity}
          onChange={(e) => setGravity(+e.target.value)}
          className="w-32"
        />
        <button
          onClick={() => setDemo(demo)}
          className="rounded bg-gray-600 px-3 py-1 text-sm text-white hover:bg-gray-700"
        >
          Reset
        </button>
      </div>

      <div ref={canvasRef} className="overflow-hidden rounded-lg border border-gray-700" />

      <p className="text-xs text-gray-400">Click and drag objects to interact</p>
    </div>
  );
}

function setupDemo(demo: Demo, engine: Matter.Engine, w: number, h: number) {
  const world = engine.world;

  switch (demo) {
    case "gravity": {
      const colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"];
      for (let i = 0; i < 8; i++) {
        const r = 15 + Math.random() * 25;
        const x = 100 + Math.random() * (w - 200);
        const body = Bodies.circle(x, 50 + Math.random() * 100, r, {
          restitution: 0.6,
          render: { fillStyle: colors[i % colors.length] },
        });
        Composite.add(world, body);
      }
      // Add some boxes too
      for (let i = 0; i < 4; i++) {
        const s = 20 + Math.random() * 30;
        Composite.add(
          world,
          Bodies.rectangle(150 + i * 120, 80, s, s, {
            restitution: 0.4,
            render: { fillStyle: colors[(i + 2) % colors.length] },
          }),
        );
      }
      break;
    }
    case "bounce": {
      // Three balls with different restitution
      const balls = [
        { x: 200, r: 0.1, label: "Clay (0.1)", color: "#8B4513" },
        { x: 350, r: 0.6, label: "Rubber (0.6)", color: "#e74c3c" },
        { x: 500, r: 0.95, label: "Super (0.95)", color: "#2ecc71" },
      ];
      balls.forEach((b) => {
        Composite.add(
          world,
          Bodies.circle(b.x, 80, 25, {
            restitution: b.r,
            render: { fillStyle: b.color },
            label: b.label,
          }),
        );
      });
      break;
    }
    case "friction": {
      // Ramp
      const ramp = Bodies.rectangle(w / 2, 300, 500, 20, {
        isStatic: true,
        angle: Math.PI * 0.1,
        render: { fillStyle: "#718096" },
      });
      Composite.add(world, ramp);
      // Three boxes with different friction
      const boxes = [
        { x: 180, f: 0.001, label: "Ice", color: "#63b3ed" },
        { x: 250, f: 0.1, label: "Normal", color: "#f6ad55" },
        { x: 320, f: 0.8, label: "Rubber", color: "#e74c3c" },
      ];
      boxes.forEach((b) => {
        Composite.add(
          world,
          Bodies.rectangle(b.x, 200, 40, 40, {
            friction: b.f,
            render: { fillStyle: b.color },
            label: b.label,
          }),
        );
      });
      break;
    }
    case "pendulum": {
      const anchor = { x: w / 2, y: 50 };
      const bob = Bodies.circle(w / 2 + 150, 250, 25, { render: { fillStyle: "#e74c3c" } });
      const rope = Constraint.create({
        pointA: anchor,
        bodyB: bob,
        length: 200,
        stiffness: 1,
        render: { strokeStyle: "#fff", lineWidth: 2 },
      });
      Composite.add(world, [bob, rope]);
      break;
    }
    case "newton-cradle": {
      const num = 5,
        size = 20,
        sep = size * 2.05;
      const startX = w / 2 - (num * sep) / 2;
      for (let i = 0; i < num; i++) {
        const x = startX + i * sep;
        const ball = Bodies.circle(i === 0 ? x - 100 : x, i === 0 ? 150 : 300, size, {
          restitution: 1,
          friction: 0,
          frictionAir: 0.0001,
          render: { fillStyle: i === 0 ? "#e74c3c" : "#ccc" },
        });
        const constraint = Constraint.create({
          pointA: { x, y: 50 },
          bodyB: ball,
          length: 250,
          stiffness: 1,
          render: { strokeStyle: "#666", lineWidth: 1 },
        });
        Composite.add(world, [ball, constraint]);
      }
      break;
    }
    case "stack": {
      const cols = 6,
        rows = 8;
      for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
          const x = w / 2 - (cols * 42) / 2 + col * 42 + 21;
          const y = h - 60 - row * 42;
          Composite.add(
            world,
            Bodies.rectangle(x, y, 40, 40, {
              render: { fillStyle: `hsl(${(row * 40 + col * 20) % 360}, 70%, 60%)` },
            }),
          );
        }
      }
      // Wrecking ball
      Composite.add(
        world,
        Bodies.circle(100, 100, 35, {
          density: 0.01,
          render: { fillStyle: "#e74c3c" },
        }),
      );
      break;
    }
    case "slingshot": {
      const anchor = { x: 200, y: 350 };
      const ball = Bodies.circle(200, 350, 20, {
        density: 0.005,
        render: { fillStyle: "#e74c3c" },
      });
      const elastic = Constraint.create({
        pointA: anchor,
        bodyB: ball,
        stiffness: 0.05,
        render: { strokeStyle: "#fff", lineWidth: 3 },
      });
      Composite.add(world, [ball, elastic]);
      // Targets
      for (let i = 0; i < 5; i++) {
        Composite.add(
          world,
          Bodies.rectangle(500 + i * 10, h - 60 - i * 45, 35, 35, {
            render: { fillStyle: `hsl(${i * 60}, 70%, 60%)` },
          }),
        );
      }
      // Fire on release
      Events.on(engine, "afterUpdate", () => {
        if (ball.position.x > 220 && elastic.bodyB === ball) {
          // Ball was launched
        }
      });
      break;
    }
  }
}
