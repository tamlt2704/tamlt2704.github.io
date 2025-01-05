'use client'

import HanziWriter from "hanzi-writer";
import { useEffect, useRef, useState } from "react"

// https://raw.githubusercontent.com/skishore/makemeahanzi/refs/heads/master/dictionary.txt

export default function HanZiWriter() {
    const [hanziData,  setHanziData] = useState([]);
    const [selectedChar, setSelectedChar] = useState();
    const hanziRef = useRef()

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
            console.log('here');
            hanziRef.current.replaceChildren();
            const writer = HanziWriter.create(hanziRef.current, selectedChar, {
                width: 250, 
                height: 250,
                padding: 5
            })
        }
    }, [selectedChar])

    function selectedCharacterChange(e) {
        console.log('selected', e.target.value);
        setSelectedChar(e.target.value)
    }

    return (
        <div>
            <label htmlFor="character">Choose a car:</label>
            <select id="character" name="character" onChange={selectedCharacterChange}>
                {hanziData.map((r) => {
                    return <option 
                        key={r.character} 
                        value={r.character}
                        
                    > {r.character} - {r.definition}</option>
                })}
            </select>

            <div ref={hanziRef}>

            </div>
        </div>
    )
}