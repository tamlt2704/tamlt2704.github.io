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

  const handleSelect = (index: number) => {
    if (revealed) return;
    setSelected(index);
    setRevealed(true);
  };

  const isCorrect = selected === answer;

  return (
    <div className="my-8 rounded-lg border border-gray-200 bg-gray-50 p-6">
      <p className="mb-4 font-semibold text-gray-900">{question}</p>

      {/* space-y-2 = 8px gap between each button */}
      <div className="space-y-2">
        {options.map((option, i) => {
          const style = "border-gray-200 bg-white hover:border-teal-400";
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
          {isCorrect ? "Correct!" : `Not quite. The answer is ${String.fromCharCode(65 + answer)}.`}
          {explanation && <p className="mt-1 text-gray-700">{explanation}</p>}
        </div>
      )}
    </div>
  );
}
