"use client";

import { useEffect, useRef } from "react";

export function Mermaid({ chart }: { chart: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    import("mermaid").then((m) => {
      m.default.initialize({ startOnLoad: false, theme: "dark" });
      m.default.render(`mermaid-${Date.now()}`, chart).then(({ svg }) => {
        if (ref.current) ref.current.innerHTML = svg;
      });
    });
  }, [chart]);

  return <div ref={ref} className="my-4 flex justify-center overflow-x-auto" />;
}
