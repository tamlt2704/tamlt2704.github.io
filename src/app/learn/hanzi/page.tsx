'use client'

import HanziWriter from "hanzi-writer";
import { useEffect, useRef, useState } from "react"

// https://raw.githubusercontent.com/skishore/makemeahanzi/refs/heads/master/dictionary.txt

export default function HanZiWriter() {
    interface Hanzi {
        character: string;
        definition: string;
    }

    const [hanziData,  setHanziData] = useState<Hanzi[]>([]);
    const [selectedChar, setSelectedChar] = useState<string | undefined>(undefined);
    const hanziRef = useRef<HTMLDivElement | null>(null)
    const fanoutRef = useRef<HTMLDivElement | null>(null)
    const [writer, setWriter] = useState<ReturnType<typeof HanziWriter.create> | null>(null);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    function renderFanningStrokes(target: HTMLDivElement | null, strokes: any[]) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.style.width = '75px';
        svg.style.height = '75px';
        svg.style.border = '1px solid #EEE'
        svg.style.marginRight = '3px'
        if (target) {
            target.appendChild(svg);
        }
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      
        // set the transform property on the g element so the character renders at 75x75
        const transformData = HanziWriter.getScalingTransform(75, 75);
        group.setAttributeNS(null, 'transform', transformData.transform);
        svg.appendChild(group);
      
        strokes.forEach(function(strokePath) {
          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          path.setAttributeNS(null, 'd', strokePath);
          // style the character paths
          path.style.fill = '#555';
          group.appendChild(path);
        });
      }
      
      

    useEffect(() => {
        async function fetchData() {
            const res = await fetch('/hanzi/dictionary.json')
            const data = await res.json()
            setHanziData(data.slice(0, 100));
        }
        fetchData();
    }, []);

    useEffect(() => {
        if (selectedChar) {
            if (hanziRef.current) {
                hanziRef.current?.replaceChildren();
                const writer = HanziWriter.create(hanziRef.current, selectedChar, {
                    width: 250, 
                    height: 250,
                    padding: 5,
                    radicalColor: '#168F16' // green
                })
                
                setWriter(writer);

                fanoutRef.current?.replaceChildren();
                HanziWriter.loadCharacterData(selectedChar).then(function(charData) {
                    if (charData) {
                        const target = fanoutRef.current;
                        for (let i = 0; i < charData.strokes.length; i++) {
                            const strokesPortion = charData.strokes.slice(0, i + 1);
                            renderFanningStrokes(target, strokesPortion);
                        }
                    }
                });
            }
        }
    }, [selectedChar])

    function selectedCharacterChange(e: React.ChangeEvent<HTMLSelectElement>) {
        setSelectedChar(e.target.value)
    }

    function animateChar() {
        if (writer) {
            console.log(writer)
            writer.animateCharacter()
        }
    }

    function startQuiz() {
        if (writer) {
            console.log(writer)
            writer.quiz()
        }
    }
    
    return (
        <div>
            <label htmlFor="character">Choose a character:</label>
            <select 
                className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                id="character" 
                name="character" 
                onChange={selectedCharacterChange}>
                {hanziData.map((r) => {
                    return <option 
                        key={r.character} 
                        value={r.character}
                        
                    > {r.character} - {r.definition}</option>
                })}
            </select>

            <div ref={hanziRef} />
            <div
                className="flex flex-row" 
                ref={fanoutRef} 
            />
            <button 
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded p-2 m-2"
                onClick={animateChar}
            > animate </button>

            <button 
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                onClick={startQuiz}
            > Quiz </button>
        </div>
    )
}
