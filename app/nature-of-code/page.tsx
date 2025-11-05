'use client';

import React, {useRef, useEffect} from "react";
import p5 from "p5";

const P5Sketch: React.FC = () => {
    const sketchRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const sketch = (p: p5) => {
            p.setup = () => {
                p.createCanvas(400, 400);
            }

            p.draw = () => {
                p.background(220);
                p.ellipse(p.width/2, p.height/2, 50, 50);
            }
        }

        const myp5 = new p5(sketch, sketchRef.current!)
        return () => {
            myp5.remove();
        }
    }, []);

    return <div ref={sketchRef}> </div>
}

const NatureOfCodePage: React.FC = () => {

    return <div>
        <P5Sketch/>
    </div>
}


export default NatureOfCodePage;