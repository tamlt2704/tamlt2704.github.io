'use client'
import HanziWriter from 'hanzi-writer'
import { useEffect, useRef, useState } from 'react';

export default function Home() {
  const woRef = useRef<HTMLDivElement>(null)
  const [writer, setWriter] = useState<HanziWriter | null>(null);

  useEffect(() => {
    const writer = HanziWriter.create(woRef.current, '我', {
      width: 250,
      height: 250,
      padding: 5,
      strokeColor: '#EE00FF' // pink
    })
    setWriter(writer)
  }, [])

  function handleClick(event: MouseEvent<HTMLButtonElement, MouseEvent>): void {
    writer.animateCharacter()
  }

  return (
    <div>
      Hello World
      <div ref={woRef}> </div>
      <button onClick={handleClick}> Animate </button>
    </div>
  );
}
