'use client'
import styles from './styles.module.css'
import Image from "next/image";
import {useRef} from "react";

//https://www.mdbg.net/chinese/rsc/audio/voice_pinyin_pz/guo3.mp3
function WordCategory() {
    return (
        <div className={styles.gridItem}> Fruit </div>
    );
}

function GridItem({src}) {
    const imgStyle = {
        width: "100%",
        height: "100%",
    }
    const audioRef = useRef(null);


    function playSound() {
        if (audioRef.current) {
            audioRef.current.play();
        }
    }

    return (
        <div className={styles.gridItem}>
            <Image onClick={playSound}
                style={imgStyle}
                src={src}
                alt={''}
                fill
                />
            <audio ref={audioRef} src={'/avocado.mp3'} />
        </div>
    );
}

export default function LearnChinesPage() {
    return (
        <>
            <div className={styles.gridContainer}>
                {
                    Array.from(new Set(["avocado", "banana", "chery", "grape","lemon","strawberry","watermelon"])).map((x, i) => (
                        <GridItem key={x} src={`/${x}.png`} />
                    ))
                }
            </div>
        </>
    );
}