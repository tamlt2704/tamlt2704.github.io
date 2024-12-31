'use client'

import { Canvas } from "@react-three/fiber"
import styles from './styles.module.css'

export default function AnimationPage() {
    return (
        <div className={styles.canvasContainer}>
                <Canvas camera={{position: [2,2,2]}}>
                    <mesh>
                        <boxGeometry args={[2,3,2]} />
                        <meshPhongMaterial color={0x00bfff}/>
                    </mesh>
                    <directionalLight position={[2,5,1]} />
                </Canvas>
        </div>
    )
}