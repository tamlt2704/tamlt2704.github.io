"use client";

import { Box, Text, Button, HStack, VStack } from "@chakra-ui/react";
import { useState, useRef, useCallback, useEffect } from "react";
import { animate } from "animejs";
import Navbar from "@/app/components/Navbar";

const EMOJIS = ["🍎", "⭐", "🐱", "🌸", "🐶", "🍕", "🎈", "🐸"];

function randInt(min: number, max: number) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pickEmoji() {
    return EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
}

type Problem = { a: number; b: number; op: "+" | "−"; answer: number; emoji: string };

function genProblem(mode: "+" | "−" | "mix"): Problem {
    const op = mode === "mix" ? (Math.random() > 0.5 ? "+" : "−") : mode;
    let a: number, b: number;
    if (op === "+") {
        a = randInt(1, 9);
        b = randInt(1, 9 - a);
    } else {
        a = randInt(2, 9);
        b = randInt(1, a - 1);
    }
    return { a, b, op, answer: op === "+" ? a + b : a - b, emoji: pickEmoji() };
}

function genChoices(answer: number): number[] {
    const set = new Set([answer]);
    while (set.size < 4) {
        const off = randInt(-3, 3);
        const v = answer + off;
        if (v >= 0 && v <= 18 && v !== answer) set.add(v);
    }
    return [...set].sort(() => Math.random() - 0.5);
}

export default function MathPage() {
    const [mode, setMode] = useState<"+" | "−" | "mix">("+");
    const [problem, setProblem] = useState<Problem | null>(null);
    const [choices, setChoices] = useState<number[]>([]);
    const [feedback, setFeedback] = useState("");
    const [score, setScore] = useState(0);
    const [streak, setStreak] = useState(0);
    const itemsRef = useRef<HTMLDivElement>(null);
    const resultRef = useRef<HTMLDivElement>(null);
    const feedbackRef = useRef<HTMLDivElement>(null);

    const newRound = useCallback((m: "+" | "−" | "mix") => {
        const p = genProblem(m);
        setProblem(p);
        setChoices(genChoices(p.answer));
        setFeedback("");
    }, []);

    useEffect(() => { newRound(mode); }, [mode, newRound]);

    // Animate items when problem changes
    useEffect(() => {
        if (!itemsRef.current || !problem) return;
        const items = itemsRef.current.querySelectorAll(".math-item");
        if (items.length === 0) return;
        // Reset
        items.forEach(el => {
            (el as HTMLElement).style.opacity = "0";
            (el as HTMLElement).style.transform = "scale(0) translateY(30px)";
        });
        animate(items, {
            opacity: [0, 1],
            scale: [0, 1],
            translateY: [30, 0],
            delay: (_el: Element, i: number) => i * 80,
            duration: 400,
            ease: "outBack",
        });
    }, [problem]);

    const handleAnswer = (val: number) => {
        if (!problem || feedback) return;
        if (val === problem.answer) {
            setFeedback("🎉 Correct!");
            setScore(s => s + 1);
            setStreak(s => s + 1);
            // Celebration animation
            if (resultRef.current) {
                animate(resultRef.current, {
                    scale: [1, 1.4, 1],
                    rotate: [0, 10, -10, 0],
                    duration: 600,
                    ease: "outElastic(1, .4)",
                });
            }
            if (feedbackRef.current) {
                animate(feedbackRef.current, {
                    scale: [0, 1.2, 1],
                    opacity: [0, 1],
                    duration: 500,
                    ease: "outBack",
                });
            }
            setTimeout(() => newRound(mode), 1200);
        } else {
            setFeedback("❌ Try again!");
            setStreak(0);
            // Shake animation
            if (feedbackRef.current) {
                animate(feedbackRef.current, {
                    translateX: [0, -12, 12, -8, 8, 0],
                    duration: 400,
                    ease: "inOutQuad",
                });
            }
            setTimeout(() => setFeedback(""), 800);
        }
    };

    // Build visual items: group A | operator | group B
    const renderItems = () => {
        if (!problem) return null;
        const { a, b, op, emoji } = problem;
        const groupA = Array.from({ length: a }, (_, i) => (
            <Box key={`a${i}`} className="math-item" fontSize="3xl" opacity={0}>{emoji}</Box>
        ));
        const groupB = Array.from({ length: b }, (_, i) => (
            <Box key={`b${i}`} className="math-item" fontSize="3xl" opacity={0}>{emoji}</Box>
        ));
        return (
            <HStack gap={2} flexWrap="wrap" justifyContent="center">
                {groupA}
                <Text className="math-item" fontSize="3xl" fontWeight="bold" color="#7C3AED" opacity={0} mx={2}>
                    {op}
                </Text>
                {groupB}
            </HStack>
        );
    };

    return (
        <Box minH="100vh" bg="linear-gradient(135deg, #E0F7FA 0%, #F3E5F5 50%, #FFF9C4 100%)">
            <Navbar />
            <VStack gap={5} p={6} maxW={500} mx="auto">
                <Text fontSize="4xl" fontWeight="bold" color="#5B21B6">🧮 Math Fun! 🎉</Text>

                {/* Mode selector */}
                <HStack gap={2}>
                    {(["+", "−", "mix"] as const).map(m => (
                        <Button
                            key={m}
                            onClick={() => setMode(m)}
                            bg={mode === m ? "#7C3AED" : "white"}
                            color={mode === m ? "white" : "#7C3AED"}
                            border="2px solid #7C3AED"
                            borderRadius="xl"
                            fontSize="lg"
                            fontWeight="bold"
                            _hover={{ bg: mode === m ? "#6D28D9" : "#EDE9FE" }}
                        >
                            {m === "mix" ? "➕➖ Mix" : m === "+" ? "➕ Add" : "➖ Subtract"}
                        </Button>
                    ))}
                </HStack>

                {/* Score */}
                <HStack gap={4}>
                    <Text fontSize="lg" fontWeight="bold" color="#059669">⭐ Score: {score}</Text>
                    <Text fontSize="lg" fontWeight="bold" color="#D97706">🔥 Streak: {streak}</Text>
                </HStack>

                {problem && (
                    <Box bg="white" borderRadius="2xl" p={6} boxShadow="lg" border="3px solid #C084FC" w="full">
                        {/* Visual items */}
                        <Box ref={itemsRef} mb={4}>
                            {renderItems()}
                        </Box>

                        {/* Equation */}
                        <Box ref={resultRef}>
                            <Text fontSize="4xl" fontWeight="bold" textAlign="center" color="#1E293B">
                                {problem.a} {problem.op} {problem.b} = ?
                            </Text>
                        </Box>

                        {/* Choices */}
                        <HStack gap={3} justifyContent="center" mt={5} flexWrap="wrap">
                            {choices.map(c => (
                                <Button
                                    key={c}
                                    onClick={() => handleAnswer(c)}
                                    w="64px" h="64px"
                                    fontSize="2xl"
                                    fontWeight="bold"
                                    bg="#FEF3C7"
                                    color="#92400E"
                                    border="3px solid #FBBF24"
                                    borderRadius="xl"
                                    _hover={{ bg: "#FDE68A", transform: "scale(1.1)" }}
                                    transition="all 0.15s"
                                >
                                    {c}
                                </Button>
                            ))}
                        </HStack>

                        {/* Feedback */}
                        <Box ref={feedbackRef} mt={4} minH="40px">
                            {feedback && (
                                <Text fontSize="2xl" fontWeight="bold" textAlign="center"
                                    color={feedback.includes("🎉") ? "#059669" : "#DC2626"}>
                                    {feedback}
                                </Text>
                            )}
                        </Box>
                    </Box>
                )}
            </VStack>
        </Box>
    );
}
