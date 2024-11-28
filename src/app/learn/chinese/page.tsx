'use client'
import styles from './styles.module.css'
import Image from "next/image";
import {useRef} from "react";

//https://www.mdbg.net/chinese/rsc/audio/voice_pinyin_pz/guo3.mp3
// function WordCategory() {
//     return (
//         <div className={styles.gridItem}> Fruit </div>
//     );
// }

function GridItem({src} : {src: string}) {
    const imgStyle = {
        width: "100%",
        height: "100%",
    }
    const audioRef = useRef(null);


    function playSound(): void {
        if (audioRef.current) {
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-expect-error
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
                    Array.from(new Set([
                        "apple", "banana", "chery", "date", "fig", "grape", "kiwi", "lemon", "mango",
                        "orange", "pear", "plum", "quince", "raspberry", "strawberry", "blueberry",
                        "blackberry", "pineapple", "papaya", "peach", "watermelon", "passionfruit",
                        "lychee", "dragonfruit", "jackfruit", "durian", "persimmon", "guava", "starfruit",
                        "mulberry", "rambutan",
                    ])).map((x, i) => (
                        <GridItem key={i} src={`/fruits/${x}.png`} />
                    ))
                }
            </div>
        </>
    );
}