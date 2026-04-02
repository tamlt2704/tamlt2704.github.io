"use client";

import { Box, Text, Button, HStack, VStack } from "@chakra-ui/react";
import { useState, useRef, useEffect, useCallback } from "react";
import HanziWriterLib from "hanzi-writer";
import Navbar from "@/app/components/Navbar";
import categories, { Word } from "./words";

function speak(text: string) {
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "zh-CN";
    u.rate = 0.8;
    speechSynthesis.speak(u);
}

function isChinese(ch: string) {
    return /[\u4e00-\u9fff]/.test(ch);
}

function HanziPanel({ text }: { text: string }) {
    const containerRef = useRef<HTMLDivElement>(null);
    const writersRef = useRef<HanziWriterLib[]>([]);
    const chars = [...text].filter(isChinese);

    useEffect(() => {
        if (!containerRef.current) return;
        containerRef.current.innerHTML = "";
        writersRef.current = [];
        chars.forEach(ch => {
            const div = document.createElement("div");
            div.style.display = "inline-block";
            div.style.margin = "4px";
            div.style.border = "2px solid #E9D5FF";
            div.style.borderRadius = "12px";
            div.style.background = "#FAF5FF";
            containerRef.current!.appendChild(div);
            const w = HanziWriterLib.create(div, ch, {
                width: 100, height: 100, padding: 5,
                showOutline: true, strokeColor: "#7C3AED", outlineColor: "#DDD",
                strokeAnimationSpeed: 1, delayBetweenStrokes: 200,
            });
            writersRef.current.push(w);
        });
    }, [text]);

    const animateAll = useCallback(() => {
        writersRef.current.reduce(
            (p, w) => p.then(() => new Promise<void>(resolve => {
                w.animateCharacter({ onComplete: () => resolve() });
            })),
            Promise.resolve()
        );
    }, [text]);

    if (chars.length === 0) return null;

    return (
        <VStack gap={3} alignItems="center">
            <Text fontSize="lg" fontWeight="bold" color="#5B21B6">✍️ Stroke Order</Text>
            <Box ref={containerRef} display="flex" flexWrap="wrap" justifyContent="center" />
            <Button onClick={animateAll} bg="#7C3AED" color="white" borderRadius="xl" fontSize="md"
                _hover={{ bg: "#6D28D9", transform: "scale(1.05)" }}>
                ▶️ Animate
            </Button>
        </VStack>
    );
}

function WordCard({ word, isSelected, onSelect }: { word: Word; isSelected: boolean; onSelect: () => void }) {
    const [flipped, setFlipped] = useState(false);

    return (
        <Box
            bg={isSelected ? "#F5F3FF" : "white"} borderRadius="xl" p={4}
            border={isSelected ? "3px solid #7C3AED" : "2px solid #E9D5FF"}
            boxShadow={isSelected ? "md" : "sm"} cursor="pointer" transition="all 0.2s"
            _hover={{ boxShadow: "md", borderColor: "#C084FC", transform: "translateY(-2px)" }}
            onClick={() => { setFlipped(f => !f); onSelect(); }}
        >
            <HStack justifyContent="space-between" alignItems="flex-start">
                <VStack alignItems="flex-start" gap={1} flex={1}>
                    <Text fontSize="2xl" color="#1E293B" fontWeight="bold">{word.cn}</Text>
                    <Text fontSize="md" color="#7C3AED">{word.py}</Text>
                    {flipped
                        ? <Text fontSize="md" color="#059669" mt={1}>{word.en}</Text>
                        : <Text fontSize="sm" color="#aaa" mt={1}>tap to reveal</Text>
                    }
                </VStack>
                <Button
                    onClick={(e) => { e.stopPropagation(); speak(word.cn); }}
                    bg="#F5F3FF" color="#7C3AED" borderRadius="full"
                    minW="40px" h="40px" fontSize="xl" p={0}
                    _hover={{ bg: "#EDE9FE", transform: "scale(1.1)" }}>
                    🔊
                </Button>
            </HStack>
        </Box>
    );
}

export default function ChinesePage() {
    const [catIdx, setCatIdx] = useState(0);
    const [selectedWord, setSelectedWord] = useState(0);
    const cat = categories[catIdx];

    useEffect(() => { setSelectedWord(0); }, [catIdx]);

    return (
        <Box minH="100vh" bg="linear-gradient(135deg, #FFF9C4 0%, #BBDEFB 50%, #F8BBD0 100%)">
            <Navbar />
            <VStack gap={5} p={6}>
                <Text fontSize="4xl" fontWeight="bold" color="#5B21B6">🗣 Chinese Starters</Text>
                <Text fontSize="md" color="#7C3AED">Common words & phrases to start a conversation</Text>

                {/* Category tabs */}
                <HStack gap={2} flexWrap="wrap" justifyContent="center" maxW={900}>
                    {categories.map((c, i) => (
                        <Button key={i} onClick={() => setCatIdx(i)} size="sm"
                            bg={catIdx === i ? "#7C3AED" : "white"}
                            color={catIdx === i ? "white" : "#7C3AED"}
                            border="2px solid #7C3AED" borderRadius="xl" fontSize="sm" fontWeight="bold"
                            _hover={{ bg: catIdx === i ? "#6D28D9" : "#EDE9FE" }}>
                            {c.emoji} {c.name}
                        </Button>
                    ))}
                </HStack>

                {/* Two-column layout */}
                <HStack alignItems="flex-start" gap={6} w="full" maxW={900} flexWrap="wrap" justifyContent="center">
                    {/* Left: word cards */}
                    <VStack gap={3} flex={1} minW={300} maxW={480}>
                        <Text fontSize="xl" fontWeight="bold" color="#5B21B6">
                            {cat.emoji} {cat.name}
                        </Text>
                        {cat.words.map((w, i) => (
                            <Box key={`${catIdx}-${i}`} w="full">
                                <WordCard word={w} isSelected={selectedWord === i}
                                    onSelect={() => setSelectedWord(i)} />
                            </Box>
                        ))}
                    </VStack>

                    {/* Right: hanzi writer */}
                    <Box position="sticky" top="80px" minW={200} flexShrink={0}
                        bg="white" borderRadius="2xl" p={5} boxShadow="lg" border="3px solid #C084FC">
                        <VStack gap={3}>
                            <Text fontSize="2xl" fontWeight="bold" color="#1E293B">
                                {cat.words[selectedWord]?.cn}
                            </Text>
                            <Text fontSize="md" color="#7C3AED">
                                {cat.words[selectedWord]?.py}
                            </Text>
                            <Text fontSize="sm" color="#059669">
                                {cat.words[selectedWord]?.en}
                            </Text>
                            <HanziPanel key={`${catIdx}-${selectedWord}`} text={cat.words[selectedWord]?.cn || ""} />
                        </VStack>
                    </Box>
                </HStack>
            </VStack>
        </Box>
    );
}
