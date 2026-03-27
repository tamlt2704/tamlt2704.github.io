"use client";

import { Input, Button, HStack, Box, Text, VStack } from "@chakra-ui/react";
import { useState, useRef, useEffect } from "react";
import HanziWriterLib, { CharacterJson } from "hanzi-writer";
import { jsPDF } from "jspdf";
import { pinyin } from "pinyin-pro";
import dict from "./dict";
import phrases from "./phrases";
import Navbar from "@/app/components/Navbar";

export default function HanziWriter() {
    const [value, setValue] = useState("我");
    const [inputText, setInputText] = useState("我");
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [currentPinyin, setCurrentPinyin] = useState("");
    const [currentMeaning, setCurrentMeaning] = useState("");
    const [quizMsg, setQuizMsg] = useState("");
    const [totalStrokes, setTotalStrokes] = useState(0);
    const [strokesLeft, setStrokesLeft] = useState(0);
    const [mistakes, setMistakes] = useState(0);
    const writerRef = useRef<HanziWriterLib | null>(null);
    const quizRef = useRef<HanziWriterLib | null>(null);
    const targetRef = useRef<HTMLDivElement>(null);
    const quizTargetRef = useRef<HTMLDivElement>(null);
    const fanTargetRef = useRef<HTMLDivElement>(null);

    const downloadPDF = async () => {
        const char = value || "我";
        const charData = await HanziWriterLib.loadCharacterData(char) as CharacterJson;
        if (!charData) return;
        const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
        const cellSize = 30;
        const cols = 5;
        const margin = 15;
        const gap = 4;

        pdf.setFontSize(20);
        pdf.text(`Stroke Breakdown: ${char}`, margin, 15);

        // Draw each stroke step
        for (let i = 0; i < charData.strokes.length; i++) {
            const col = i % cols;
            const row = Math.floor(i / cols);
            const x = margin + col * (cellSize + gap);
            const y = 25 + row * (cellSize + gap);

            // Grid cell
            pdf.setDrawColor(200);
            pdf.setLineWidth(0.3);
            pdf.rect(x, y, cellSize, cellSize);
            // Cross lines
            pdf.setLineDashPattern([1, 1], 0);
            pdf.line(x + cellSize / 2, y, x + cellSize / 2, y + cellSize);
            pdf.line(x, y + cellSize / 2, x + cellSize, y + cellSize / 2);
            pdf.line(x, y, x + cellSize, y + cellSize);
            pdf.line(x + cellSize, y, x, y + cellSize);
            pdf.setLineDashPattern([], 0);

            // Render strokes as SVG then to canvas then to PDF
            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
            svg.setAttribute("width", "200");
            svg.setAttribute("height", "200");
            const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
            const t = HanziWriterLib.getScalingTransform(200, 200);
            g.setAttributeNS(null, "transform", t.transform);
            svg.appendChild(g);
            charData.strokes.slice(0, i + 1).forEach((sp, j) => {
                const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
                path.setAttributeNS(null, "d", sp);
                path.setAttribute("fill", j === i ? "#8B5CF6" : "#999");
                g.appendChild(path);
            });

            const svgData = new XMLSerializer().serializeToString(svg);
            const img = new Image();
            await new Promise<void>((resolve) => {
                img.onload = () => resolve();
                img.src = "data:image/svg+xml;base64," + btoa(svgData);
            });
            const canvas = document.createElement("canvas");
            canvas.width = 200;
            canvas.height = 200;
            canvas.getContext("2d")!.drawImage(img, 0, 0);
            pdf.addImage(canvas.toDataURL("image/png"), "PNG", x + 1, y + 1, cellSize - 2, cellSize - 2);
        }

        // Practice rows
        const practiceY = 25 + (Math.ceil(charData.strokes.length / cols)) * (cellSize + gap) + 10;
        pdf.setFontSize(16);
        pdf.text("Practice:", margin, practiceY);
        const practiceRows = 4;
        const practiceCols = 6;
        for (let r = 0; r < practiceRows; r++) {
            for (let c = 0; c < practiceCols; c++) {
                const x = margin + c * (cellSize + gap);
                const y = practiceY + 5 + r * (cellSize + gap);
                pdf.setDrawColor(200);
                pdf.setLineWidth(0.3);
                pdf.rect(x, y, cellSize, cellSize);
                pdf.setLineDashPattern([1, 1], 0);
                pdf.line(x + cellSize / 2, y, x + cellSize / 2, y + cellSize);
                pdf.line(x, y + cellSize / 2, x + cellSize, y + cellSize / 2);
                pdf.line(x, y, x + cellSize, y + cellSize);
                pdf.line(x + cellSize, y, x, y + cellSize);
                pdf.setLineDashPattern([], 0);
                // Light outline of character in first column
                if (c === 0) {
                    const svg2 = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                    svg2.setAttribute("xmlns", "http://www.w3.org/2000/svg");
                    svg2.setAttribute("width", "200");
                    svg2.setAttribute("height", "200");
                    const g2 = document.createElementNS("http://www.w3.org/2000/svg", "g");
                    const t2 = HanziWriterLib.getScalingTransform(200, 200);
                    g2.setAttributeNS(null, "transform", t2.transform);
                    svg2.appendChild(g2);
                    charData.strokes.forEach((sp) => {
                        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
                        path.setAttributeNS(null, "d", sp);
                        path.setAttribute("fill", "#DDD");
                        g2.appendChild(path);
                    });
                    const svgData2 = new XMLSerializer().serializeToString(svg2);
                    const img2 = new Image();
                    await new Promise<void>((resolve) => {
                        img2.onload = () => resolve();
                        img2.src = "data:image/svg+xml;base64," + btoa(svgData2);
                    });
                    const canvas2 = document.createElement("canvas");
                    canvas2.width = 200;
                    canvas2.height = 200;
                    canvas2.getContext("2d")!.drawImage(img2, 0, 0);
                    pdf.addImage(canvas2.toDataURL("image/png"), "PNG", x + 1, y + 1, cellSize - 2, cellSize - 2);
                }
            }
        }

        pdf.save(`hanzi-${char}.pdf`);
    };

    useEffect(() => {
        if (!targetRef.current) return;
        targetRef.current.innerHTML = "";
        const char = value || "我";
        writerRef.current = HanziWriterLib.create(targetRef.current, char, {
            width: 200, height: 200, padding: 5, showOutline: true,
            strokeColor: "#4A90D9",
            outlineColor: "#DDD",
        });
        setCurrentPinyin(pinyin(char));
        setCurrentMeaning(dict[char] || "");
    }, [value]);

    useEffect(() => {
        if (!fanTargetRef.current) return;
        fanTargetRef.current.innerHTML = "";
        HanziWriterLib.loadCharacterData(value || "我").then((charData) => {
            if (!charData) return;
            if (!fanTargetRef.current) return;
            fanTargetRef.current.innerHTML = "";
            for (let i = 0; i < charData.strokes.length; i++) {
                const size = 120;
                const half = size / 2;
                const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                svg.style.width = size + "px";
                svg.style.height = size + "px";
                svg.style.border = "2px solid #E9D5FF";
                svg.style.borderRadius = "12px";
                svg.style.marginRight = "8px";
                svg.style.marginBottom = "8px";
                svg.style.background = "#FAF5FF";
                fanTargetRef.current.appendChild(svg);
                // Grid lines (田字格)
                const gridColor = "#E9D5FF";
                [[half, 0, half, size], [0, half, size, half], [0, 0, size, size], [size, 0, 0, size]].forEach(([x1, y1, x2, y2]) => {
                    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                    line.setAttribute("x1", String(x1));
                    line.setAttribute("y1", String(y1));
                    line.setAttribute("x2", String(x2));
                    line.setAttribute("y2", String(y2));
                    line.setAttribute("stroke", gridColor);
                    line.setAttribute("stroke-width", "1");
                    line.setAttribute("stroke-dasharray", "3,3");
                    svg.appendChild(line);
                });
                const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
                const transformData = HanziWriterLib.getScalingTransform(size, size);
                group.setAttributeNS(null, "transform", transformData.transform);
                svg.appendChild(group);
                charData.strokes.slice(0, i + 1).forEach((strokePath, j) => {
                    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
                    path.setAttributeNS(null, "d", strokePath);
                    path.style.fill = j === i ? "#8B5CF6" : "#CBD5E1";
                    group.appendChild(path);
                });
            }
        });
    }, [value]);

    useEffect(() => {
        if (!quizTargetRef.current) return;
        quizTargetRef.current.innerHTML = "";
        setQuizMsg("");
        setTotalStrokes(0);
        setStrokesLeft(0);
        setMistakes(0);
        quizRef.current = HanziWriterLib.create(quizTargetRef.current, value || "我", {
            width: 200, height: 200, padding: 5, showCharacter: false,
            highlightColor: "#4ADE80",
            drawingColor: "#F472B6",
            outlineColor: "#DDD",
        });
    }, [value]);

    const startQuiz = () => {
        setQuizMsg("✏️ Draw the character!");
        setMistakes(0);
        quizRef.current?.quiz({
            onMistake: (strokeData) => {
                const total = strokeData.strokeNum + strokeData.strokesRemaining + 1;
                setTotalStrokes(total);
                setStrokesLeft(strokeData.strokesRemaining);
                setMistakes(strokeData.totalMistakes);
                setQuizMsg("❌ Oops! Try again!");
            },
            onCorrectStroke: (strokeData) => {
                const total = strokeData.strokeNum + strokeData.strokesRemaining + 1;
                setTotalStrokes(total);
                setStrokesLeft(strokeData.strokesRemaining);
                setMistakes(strokeData.totalMistakes);
                setQuizMsg("⭐ Great job!");
            },
            onComplete: (summaryData) => {
                setStrokesLeft(0);
                setMistakes(summaryData.totalMistakes);
                setQuizMsg(summaryData.totalMistakes === 0
                    ? "🎉🎉🎉 Perfect! You're amazing! 🎉🎉🎉"
                    : `🎊 Well done! You finished with ${summaryData.totalMistakes} oopsie(s)!`);
            },
        });
    };

    return (
        <Box minH="100vh" bg="linear-gradient(135deg, #FFF9C4 0%, #BBDEFB 50%, #F8BBD0 100%)">
            <Navbar />
            <VStack gap={6} p={6}>
                {/* Title */}
                <Text fontSize="4xl" fontWeight="bold" color="#5B21B6">
                    ✨ Hanzi Playground ✨
                </Text>
                <Text fontSize="lg" color="#7C3AED">Learn to write Chinese characters! 🐼</Text>

                {/* Input */}
                <Box position="relative">
                    <HStack>
                    <Input
                        placeholder="Type pinyin or hanzi 🀄"
                        maxW={280}
                        value={inputText}
                        onChange={(e) => {
                            const text = e.target.value;
                            setInputText(text);
                            if (/[\u4e00-\u9fff]/.test(text)) {
                                setValue(text.slice(-1));
                                setSuggestions([]);
                                setShowSuggestions(false);
                            } else if (text.length > 0) {
                                const common = "的一是不了人我在有他这中大来上个国为以子到说们生会自着去之过家学对可她里后小么心多天而要好都然没成日行于起也与事其写还用道活好过子就中从时会合要也地出就年对开展到理行能作区然起事可于商五果实学进种现它前些所多日已经月长知民世最手明方报电全定己花用看外开处四力结山百回果孩万少直意夜比阶连车重便斗马哪化太指变社似士者干石满得式居批次亲头火步问喜让相解立水无建号新带列死尾张难术言员特名真论走义各入几口认条平系气题英床检师息引快德慢深海七女任件感准团屋离色脸片科倒睛利刚且由送切星导晚表够整响雪流未场该并底刻伟忙提确近亮轻讲农古黑告界拉呀土清阳照办史改历转画造嘴此治北必服雨穿内识验传业菜爬睡兴形量咱观苦体众通冲破友度饭公旁房极南枪读沙岁线野坚空收算至政城劳落钱围弟胸乎尼持西括志反尖须飞关核驾军工物广村声纸哈元周父母企";
                                const input = text.toLowerCase();
                                const chars = [...new Set([...common])]
                                    .filter(c => pinyin(c, { toneType: "none" }) === input)
                                    .slice(0, 10);
                                setSuggestions(chars);
                                setShowSuggestions(chars.length > 0);
                            } else {
                                setSuggestions([]);
                                setShowSuggestions(false);
                            }
                        }}
                        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                        onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                        bg="white"
                        borderColor="#C084FC"
                        borderWidth={2}
                        borderRadius="xl"
                        fontSize="xl"
                        textAlign="center"
                        _focus={{ borderColor: "#8B5CF6", boxShadow: "0 0 0 2px #C084FC" }}
                    />
                    <Button
                        onClick={() => {
                            const u = new SpeechSynthesisUtterance(value);
                            u.lang = "zh-CN";
                            speechSynthesis.speak(u);
                        }}
                        bg="#A78BFA"
                        color="white"
                        borderRadius="xl"
                        fontSize="2xl"
                        minW="48px"
                        h="48px"
                        _hover={{ bg: "#8B5CF6", transform: "scale(1.1)" }}
                        title="Pronounce"
                    >
                        🔊
                    </Button>
                    </HStack>
                    {showSuggestions && (
                        <HStack
                            position="absolute"
                            top="100%"
                            left={0}
                            mt={1}
                            bg="white"
                            borderRadius="xl"
                            boxShadow="lg"
                            border="1px solid #ccc"
                            p={2}
                            gap={1}
                            zIndex={10}
                            flexWrap="wrap"
                        >
                            {suggestions.map((char) => (
                                <Button
                                    key={char}
                                    size="sm"
                                    fontSize="2xl"
                                    color="black"
                                    bg="white"
                                    border="1px solid #ddd"
                                    borderRadius="md"
                                    _hover={{ bg: "#eee" }}
                                    onClick={() => {
                                        setValue(char);
                                        setInputText(char);
                                        setShowSuggestions(false);
                                    }}
                                >
                                    {char}
                                </Button>
                            ))}
                        </HStack>
                    )}
                    {currentPinyin && (
                        <Text fontSize="sm" color="#7C3AED" textAlign="center" mt={1}>
                            {currentPinyin}{currentMeaning ? ` — ${currentMeaning}` : ""}
                        </Text>
                    )}
                </Box>

                {/* Watch & Phrases Section */}
                <Box bg="white" borderRadius="2xl" p={5} boxShadow="lg" border="3px solid #93C5FD" w="full" maxW={500}>
                    <Text fontSize="xl" fontWeight="bold" color="#2563EB" mb={3} textAlign="center">
                        👀 Watch & Learn
                    </Text>
                    <Box ref={targetRef} display="flex" justifyContent="center" />
                    <Button
                        onClick={() => writerRef.current?.animateCharacter()}
                        mt={3}
                        w="full"
                        bg="#3B82F6"
                        color="white"
                        borderRadius="xl"
                        fontSize="lg"
                        _hover={{ bg: "#2563EB", transform: "scale(1.05)" }}
                    >
                        ▶️ Play Animation
                    </Button>
                    {phrases[value] && (
                        <VStack gap={3} alignItems="stretch" mt={5} pt={5} borderTop="2px dashed #93C5FD">
                            <Text fontSize="xl" fontWeight="bold" color="#B45309" textAlign="center">
                                📝 Sample Phrases
                            </Text>
                            {phrases[value].map((p, i) => (
                                <Box key={i} bg="#FFFBEB" borderRadius="lg" p={4} border="1px solid #FDE68A">
                                    <Text fontSize="2xl" color="black">{p.cn}</Text>
                                    <Text fontSize="md" color="#92400E">{p.py}</Text>
                                    <Text fontSize="md" color="#666">{p.en}</Text>
                                </Box>
                            ))}
                        </VStack>
                    )}
                </Box>

                {/* Quiz Section */}
                <Box bg="white" borderRadius="2xl" p={5} boxShadow="lg" border="3px solid #F9A8D4">
                    <Text fontSize="xl" fontWeight="bold" color="#DB2777" mb={3} textAlign="center">
                        🎮 Quiz Time!
                    </Text>
                    <HStack alignItems="flex-start" gap={4} justifyContent="center">
                        <Box>
                            <Box
                                ref={quizTargetRef}
                                border="2px dashed #F9A8D4"
                                borderRadius="xl"
                                display="flex"
                                justifyContent="center"
                            />
                            <Button
                                onClick={startQuiz}
                                mt={3}
                                w="full"
                                bg="#EC4899"
                                color="white"
                                borderRadius="xl"
                                fontSize="lg"
                                _hover={{ bg: "#DB2777", transform: "scale(1.05)" }}
                            >
                                🚀 Start Quiz
                            </Button>
                        </Box>
                        <VStack alignItems="flex-start" gap={2} minW={120}>
                            <Text fontSize="sm" fontWeight="bold" color="#059669">✅ Strokes</Text>
                            <HStack gap={1} flexWrap="wrap">
                                {Array.from({ length: totalStrokes }).map((_, i) => (
                                    <Box
                                        key={i}
                                        w="24px" h="24px"
                                        bg={i < totalStrokes - strokesLeft ? "#4ADE80" : "#D1FAE5"}
                                        borderRadius="md"
                                        border="2px solid"
                                        borderColor={i < totalStrokes - strokesLeft ? "#16A34A" : "#A7F3D0"}
                                        transition="all 0.3s"
                                    />
                                ))}
                            </HStack>
                            <Text fontSize="sm" fontWeight="bold" color="#DC2626" mt={1}>💔 Oopsies</Text>
                            <HStack gap={1} flexWrap="wrap">
                                {Array.from({ length: mistakes }).map((_, i) => (
                                    <Box
                                        key={i}
                                        w="24px" h="24px"
                                        bg="#FCA5A5"
                                        borderRadius="md"
                                        border="2px solid #EF4444"
                                        transition="all 0.3s"
                                    />
                                ))}
                            </HStack>
                        </VStack>
                    </HStack>
                    {quizMsg && (
                        <Text
                            mt={4}
                            textAlign="center"
                            fontSize="xl"
                            fontWeight="bold"
                            color={quizMsg.includes("❌") ? "#DC2626" : "#7C3AED"}
                        >
                            {quizMsg}
                        </Text>
                    )}
                </Box>

                {/* Fan Out Section */}
                <Box bg="white" borderRadius="2xl" p={5} boxShadow="lg" border="3px solid #C084FC">
                    <Text fontSize="xl" fontWeight="bold" color="#7C3AED" mb={3} textAlign="center">
                        🪭 Stroke Breakdown
                    </Text>
                    <HStack ref={fanTargetRef} flexWrap="wrap" justifyContent="center" />
                    <Button
                        onClick={downloadPDF}
                        mt={4}
                        w="full"
                        bg="#7C3AED"
                        color="white"
                        borderRadius="xl"
                        fontSize="lg"
                        _hover={{ bg: "#6D28D9", transform: "scale(1.05)" }}
                    >
                        📄 Download PDF
                    </Button>
                </Box>
            </VStack>
        </Box>
    );
}
