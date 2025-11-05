'use client';

import React, {useRef, useEffect, useState} from "react";
import dynamic from "next/dynamic";
import { sketches, sketchNames } from './sketches';

interface P5SketchProps {
  sketchKey: string;
}

const P5Sketch: React.FC<P5SketchProps> = ({ sketchKey }) => {
    const sketchRef = useRef<HTMLDivElement>(null);
    const p5Instance = useRef<any>(null);

    useEffect(() => {
        let mounted = true;
        
        import('p5').then((p5) => {
            if (!mounted) return;
            
            if (p5Instance.current) {
                p5Instance.current.remove();
                p5Instance.current = null;
            }
            
            if (sketchRef.current) {
                const sketch = sketches[sketchKey as keyof typeof sketches];
                p5Instance.current = new p5.default(sketch, sketchRef.current);
            }
        });

        return () => {
            mounted = false;
            if (p5Instance.current) {
                p5Instance.current.remove();
                p5Instance.current = null;
            }
        };
    }, [sketchKey]);

    return <div ref={sketchRef}></div>
}

const DynamicP5Sketch = dynamic(() => Promise.resolve(P5Sketch), {
    ssr: false
});

const NatureOfCodePage: React.FC = () => {
    const [activeSketch, setActiveSketch] = useState('basic-circle');

    return (
        <div className="flex h-screen">
            <div className="w-64 bg-gray-100 p-4">
                <h2 className="text-xl font-bold mb-4">Sketches</h2>
                <ul className="space-y-2">
                    {Object.keys(sketches).map((key) => (
                        <li key={key}>
                            <button
                                onClick={() => setActiveSketch(key)}
                                className={`w-full text-left p-2 rounded ${
                                    activeSketch === key 
                                        ? 'bg-blue-500 text-white' 
                                        : 'hover:bg-gray-200'
                                }`}
                            >
                                {sketchNames[key as keyof typeof sketchNames]}
                            </button>
                        </li>
                    ))}
                </ul>
            </div>
            <div className="flex-1 p-4">
                <DynamicP5Sketch sketchKey={activeSketch} />
            </div>
        </div>
    )
}

export default NatureOfCodePage;