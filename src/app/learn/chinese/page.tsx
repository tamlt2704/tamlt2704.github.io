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
                src={`/fruits/${src}.png`}
                alt={''}
                fill
                />
            <audio ref={audioRef} src={`/fruits/sounds/${src}.mp3`} />
        </div>
    );
}

export default function LearnChinesPage() {
    return (
        <>
            <div className={styles.gridContainer}>
                {
                    Array.from(new Set([
                        "apple", // ping2 guo3
                        "banana", // xiang1 jiao1
                        "chery", // ying1 tao2
                        "date", // zao3
                        "fig", // wu2 hua1 guo3  "fruit without flowers"
                        "grape", // pu2 tao5
                        "kiwi", // mi2 hou2 tao2.
                        // 猕猴 (mí hóu) means "monkey," as kiwis are sometimes associated with monkey food.
                        // 桃 (táo) means "peach," referring to its fuzzy, peach-like skin.
                        "lemon", // ning2 meng2             ffmpeg -i "concat:ning2.mp3|meng2.mp3" -acodec copy lemon.mp3
                        "mango", //mang2 quo3                ffmpeg -i "concat:mang2.mp3|guo3.mp3" -acodec copy mango.mp3
                        "orange", // cheng2 zhi1            ffmpeg -i "concat:cheng2.mp3|zhi1.mp3" -acodec copy orange.mp3
                        //橙 (chéng) specifically refers to the sweet orange.
                        // 子 (zi) is a suffix often added to indicate a fruit.
                        "pear", //li2
                        "plum", //li3 zi5       ffmpeg -i "concat:li3.mp3|zi5.mp3" -acodec copy plum.mp3
                        "quince", // wen1 po5   ffmpeg -i "concat:wen1.mp3|po5.mp3" -acodec copy quince.mp3
                        "raspberry", // fu4 pen2 zi3    ffmpeg -i "concat:fu4.mp3|pen2.mp3|zi3.mp3" -acodec copy raspberry.mp3
                        "strawberry", //cao3 mei2       ffmpeg -i "concat:cao3.mp3|mei2.mp3" -acodec copy strawberry.mp3
                        "blueberry", //lan2 mei2 //(lán) means "blue." ffmpeg -i "concat:lan2.mp3|mei2.mp3" -acodec copy blueberry.mp3
                        "blackberry",//hei1 mei2 //(lán) means "blue." ffmpeg -i "concat:hei1.mp3|mei2.mp3" -acodec copy blackberry.mp3
                        "pineapple", // bo1 lou2        ffmpeg -i "concat:bo1.mp3|lou2.mp3" -acodec copy pineapple.mp3
                        "papaya", //mu4 gua1        ffmpeg -i "concat:mu4.mp3|gua1.mp3" -acodec copy papaya.mp3
                        "peach", // tao2 zi5        ffmpeg -i "concat:tao2.mp3|zi5.mp3" -acodec copy peach.mp3
                        "watermelon", //xi1 gua1    ffmpeg -i "concat:xi1.mp3|gua1.mp3" -acodec copy watermelon.mp3
                        "passionfruit", // bai3 xiang1 guo3     ffmpeg -i "concat:bai3.mp3|xiang1.mp3|guo3.mp3" -acodec copy passionfruit.mp3
                        "lychee",//li4 zhi1         ffmpeg -i "concat:li4.mp3|zhi1.mp3" -acodec copy lychee.mp3
                        "dragonfruit", //huo3 long2 guo3    ffmpeg -i "concat:huo3.mp3|long2.mp3|guo3.mp3" -acodec copy dragonfruit.mp3
                        "jackfruit",//bo1 luo2 mi4  ffmpeg -i "concat:bo1.mp3|luo2.mp3|mi4.mp3" -acodec copy jackfruit.mp3
                        "durian",//liu2 lian2   ffmpeg -i "concat:liu2.mp3|lian2.mp3" -acodec copy durian.mp3
                        "persimmon",//shi4 zi5  ffmpeg -i "concat:shi4.mp3|zi5.mp3" -acodec copy persimmon.mp3
                        "guava",//fan1 shi2 liu5    ffmpeg -i "concat:fan1.mp3|shi2.mp3|liu5.mp3" -acodec copy guava.mp3
                        //番 (fān) means "foreign" or "overseas," often used for fruits that are not native to China.
                        // 石榴 (shí liú) refers to the pomegranate, but in this case, it forms part of the name for guava.
                        "starfruit",//yang2 tao2    ffmpeg -i "concat:yang2.mp3|tao2.mp3" -acodec copy starfruit.mp3
                        "mulberry",//sang1 shen4    ffmpeg -i "concat:sang1.mp3|shen4.mp3" -acodec copy mulberry.mp3
                        "rambutan",//hong2 mao2 dan1    ffmpeg -i "concat:hong2.mp3|mao2.mp3|dan1.mp3" -acodec copy rambutan.mp3
                        //红 (hóng) means "red," referring to the fruit's bright color.
                        // 毛 (máo) means "hair" or "fur," which describes the spiky, hairy appearance of the rambutan.
                        // 丹 (dān) refers to the fruit, often used in naming tropical fruits.
                    ])).map((x, i) => (
                        <GridItem key={i} src={x} />
                    ))
                }
            </div>
        </>
    );
}