"use client";

import { useState } from "react";

interface QuizProps {
  question: string;
  options: string[];
  answer: number;
  explanation?: string;
}

export function Quiz({ question, options, answer, explanation }: QuizProps) {
  const [selected, setSelected] = useState<number | null>(null);
  const [revealed, setRevealed] = useState(false);

  // MDX passes array props as raw strings e.g. '["a","b"]' — parse them
  const normalizedOptions: string[] = Array.isArray(options)
    ? options
    : (() => {
        const str = String(options);
        try {
          const parsed = JSON.parse(str.replace(/'/g, '"'));
          if (Array.isArray(parsed)) return parsed;
        } catch {}
        // fallback: comma-separated string
        if (str.includes(",")) return str.split(",").map((s) => s.trim());
        return [];
      })();
  const normalizedAnswer = typeof answer === "string" ? parseInt(answer, 10) : answer;

  const handleSelect = (index: number) => {
    if (revealed) return;
    setSelected(index);
    setRevealed(true);
  };

  const isCorrect = selected === normalizedAnswer;

  return (
    <div className="not-prose my-8 rounded-lg border border-gray-200 bg-gray-50 p-6">
      <p className="mb-4 font-semibold text-gray-900">{question}</p>

      <div className="space-y-2">
        {normalizedOptions.map((option, i) => {
          let style = "border-gray-200 bg-white hover:border-teal-400";
          if (revealed) {
            if (i === normalizedAnswer) style = "border-green-500 bg-green-50";
            else if (i === selected) style = "border-red-400 bg-red-50";
            else style = "border-gray-200 bg-white opacity-60";
          }
          return (
            <button
              key={i}
              onClick={() => handleSelect(i)}
              disabled={revealed}
              className={`w-full rounded-md border px-4 py-3 text-left text-sm transition ${style}`}
            >
              {/* String.fromCharCode(65) = "A", 66 = "B", etc. */}
              <span className="mr-3 font-mono text-gray-400">{String.fromCharCode(65 + i)}.</span>
              {option}
            </button>
          );
        })}
      </div>

      {/* Only show result after user has answered */}
      {revealed && (
        <div
          className={`mt-4 rounded p-3 text-sm ${isCorrect ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
        >
          {isCorrect
            ? "Correct!"
            : `Not quite. The answer is ${String.fromCharCode(65 + normalizedAnswer)}.`}
          {explanation && <p className="mt-1 text-gray-700">{explanation}</p>}
        </div>
      )}
    </div>
  );
}
