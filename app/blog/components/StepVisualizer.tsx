"use client";

import { useState } from "react";

interface Step {
  data: number[];
  highlights: number[];
  label: string;
}

interface Props {
  steps: Step[] | string;
  title?: string;
}

export function StepVisualizer({ steps: rawSteps, title }: Props) {
  const steps: Step[] = typeof rawSteps === "string" ? JSON.parse(rawSteps) : rawSteps;
  const [current, setCurrent] = useState(0);
  const step = steps[current];

  return (
    <div className="not-prose my-8 rounded-lg border border-gray-200 bg-white p-5">
      {title && <p className="mb-3 text-sm font-semibold text-gray-700">{title}</p>}
      <div className="mb-4 flex justify-center gap-1">
        {step.data.map((val, i) => (
          <div
            key={i}
            className={`flex h-10 w-10 items-center justify-center rounded border font-mono text-sm transition-all ${
              step.highlights.includes(i)
                ? "scale-110 border-teal-500 bg-teal-100 text-teal-900"
                : "border-gray-200 bg-gray-50 text-gray-700"
            }`}
          >
            {val}
          </div>
        ))}
      </div>
      <p className="mb-4 text-center text-sm text-gray-600">{step.label}</p>
      <div className="flex items-center justify-center gap-3">
        <button
          onClick={() => setCurrent(Math.max(0, current - 1))}
          disabled={current === 0}
          className="rounded border px-3 py-1 text-sm disabled:opacity-30"
        >
          ← Prev
        </button>
        <span className="text-xs text-gray-400">
          {current + 1}/{steps.length}
        </span>
        <button
          onClick={() => setCurrent(Math.min(steps.length - 1, current + 1))}
          disabled={current === steps.length - 1}
          className="rounded border px-3 py-1 text-sm disabled:opacity-30"
        >
          Next →
        </button>
      </div>
    </div>
  );
}
