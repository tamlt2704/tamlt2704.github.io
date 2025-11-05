'use client';

import React, {useRef, useEffect} from "react";
import dynamic from "next/dynamic";

const P5Sketch: React.FC = () => {
    const sketchRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        import('p5').then((p5) => {
            const sketch = (p: any) => {
                p.setup = () => {
                    p.createCanvas(400, 400);
                }

                p.draw = () => {
                    p.background(220);
                    p.ellipse(p.width/2, p.height/2, 50, 50);
                }
            }

            const myp5 = new p5.default(sketch, sketchRef.current!);
            return () => {
                myp5.remove();
            }
        });
    }, []);

    return <div ref={sketchRef}> </div>
}

const DynamicP5Sketch = dynamic(() => Promise.resolve(P5Sketch), {
    ssr: false
});

const NatureOfCodePage: React.FC = () => {
    return <div>
        <DynamicP5Sketch/>
    </div>
}

export default NatureOfCodePage;