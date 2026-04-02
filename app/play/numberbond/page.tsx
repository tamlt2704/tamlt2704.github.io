"use client";

import { Box, Text, Button, HStack, VStack } from "@chakra-ui/react";
import { useState, useRef, useCallback, useEffect } from "react";
import { animate } from "animejs";
import Navbar from "@/app/components/Navbar";

function randInt(min: number, max: number) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// --- Web Audio sounds ---
let audioCtx: AudioContext | null = null;
function getCtx() {
    if (!audioCtx) audioCtx = new AudioContext();
    return audioCtx;
}
function playTone(freq: number, dur: number, type: OscillatorType = "sine", vol = 0.15) {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(vol, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
    osc.connect(gain).connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + dur);
}
function sfxCorrect() {
    playTone(523, 0.12, "sine", 0.18);
    setTimeout(() => playTone(659, 0.12, "sine", 0.18), 100);
    setTimeout(() => playTone(784, 0.2, "sine", 0.18), 200);
}
function sfxWrong() {
    playTone(200, 0.25, "square", 0.1);
    setTimeout(() => playTone(160, 0.3, "square", 0.1), 150);
}
function sfxPop(pitch: number) {
    playTone(600 + pitch * 40, 0.08, "sine", 0.1);
}
function sfxDone() {
    playTone(523, 0.1, "triangle", 0.15);
    setTimeout(() => playTone(784, 0.15, "triangle", 0.15), 80);
    setTimeout(() => playTone(1047, 0.25, "triangle", 0.15), 160);
}

type Mode = "add" | "sub" | "mix";
type Bond = { whole: number; partA: number; partB: number; missing: "whole" | "partA" | "partB" };

function genBond(mode: Mode): Bond {
    const partA = randInt(1, 9);
    const partB = randInt(1, 9);
    const whole = partA + partB;
    if (mode === "add") return { whole, partA, partB, missing: "whole" };
    if (mode === "sub") return { whole, partA, partB, missing: Math.random() > 0.5 ? "partA" : "partB" };
    const r = Math.random();
    if (r < 0.33) return { whole, partA, partB, missing: "whole" };
    if (r < 0.66) return { whole, partA, partB, missing: "partA" };
    return { whole, partA, partB, missing: "partB" };
}

function getAnswer(bond: Bond) {
    if (bond.missing === "whole") return bond.whole;
    if (bond.missing === "partA") return bond.partA;
    return bond.partB;
}

function genChoices(answer: number): number[] {
    const set = new Set([answer]);
    while (set.size < 4) {
        const v = answer + randInt(-3, 3);
        if (v >= 0 && v <= 18 && v !== answer) set.add(v);
    }
    return [...set].sort(() => Math.random() - 0.5);
}

const CIRCLE = 72;
const DOT = 12;
const DOT_GAP = 4;
const ROW_MAX = 5;
const COLOR_A = "#7C3AED";
const COLOR_B = "#2563EB";

const BOND_CIRCLE_STYLE = {
    width: CIRCLE, height: CIRCLE, borderRadius: "50%", display: "flex",
    alignItems: "center", justifyContent: "center", fontWeight: "bold" as const,
    fontSize: "28px", border: "3px solid #7C3AED",
};

type VisPhase = "hidden" | "expand" | "fly" | "done";

export default function NumberBondPage() {
    const [mode, setMode] = useState<Mode>("add");
    const [bond, setBond] = useState<Bond | null>(null);
    const [choices, setChoices] = useState<number[]>([]);
    const [feedback, setFeedback] = useState("");
    const [score, setScore] = useState(0);
    const [streak, setStreak] = useState(0);
    const [showVis, setShowVis] = useState(true);
    const [visPhase, setVisPhase] = useState<VisPhase>("hidden");
    const [speed, setSpeed] = useState(1); // 1=slowest, 4=fastest
    const speedRef = useRef(1);
    useEffect(() => { speedRef.current = speed; }, [speed]);

    const diagramRef = useRef<HTMLDivElement>(null);
    const feedbackRef = useRef<HTMLDivElement>(null);
    const phaseTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
    const flyTimers = useRef<ReturnType<typeof setTimeout>[]>([]);

    const clearTimers = () => {
        if (phaseTimer.current) clearTimeout(phaseTimer.current);
        flyTimers.current.forEach(t => clearTimeout(t));
        flyTimers.current = [];
    };

    const newRound = useCallback((m: Mode) => {
        clearTimers();
        setBond(genBond(m));
    }, []);

    useEffect(() => {
        if (!bond) return;
        setChoices(genChoices(getAnswer(bond)));
        setFeedback("");
        setVisPhase("hidden");
    }, [bond]);

    useEffect(() => { newRound(mode); }, [mode, newRound]);
    useEffect(() => () => clearTimers(), []);

    // Pop-in bond circles
    useEffect(() => {
        if (!diagramRef.current || visPhase !== "hidden") return;
        // Only clear animation-related styles, not visual styles like background/border
        diagramRef.current.querySelectorAll("*").forEach(el => {
            (el as HTMLElement).style.removeProperty("transform");
            (el as HTMLElement).style.removeProperty("opacity");
        });
        // Remove any leftover traveler dots
        diagramRef.current.querySelectorAll("div[style*='z-index:10']").forEach(el => el.remove());
        // Restore src-dot and ans-dot styles that were changed during fly
        diagramRef.current.querySelectorAll(".src-dot, .ans-dot, .kn-dot").forEach(el => {
            (el as HTMLElement).style.removeProperty("background");
            (el as HTMLElement).style.removeProperty("border");
        });
        const circles = diagramRef.current.querySelectorAll(".bond-circle");
        circles.forEach(el => {
            (el as HTMLElement).style.opacity = "0";
            (el as HTMLElement).style.transform = "scale(0)";
        });
        animate(circles, {
            opacity: [0, 1], scale: [0, 1],
            delay: (_el, i) => i * 150,
            duration: 400, ease: "outBack",
        });
    }, [bond, visPhase]);

    const isAddition = bond?.missing === "whole";

    // Animation phases
    useEffect(() => {
        if (!diagramRef.current || visPhase === "hidden" || visPhase === "done" || !bond) return;
        const root = diagramRef.current;
        const s = speedRef.current;
        // Speed 1=slow, 4=fast
        const popDur = [500, 350, 250, 150][s - 1];
        const popGap = [200, 140, 90, 50][s - 1];
        const flyDur = [900, 600, 400, 200][s - 1];

        if (visPhase === "expand") {
            const dots = root.querySelectorAll(".src-dot");
            dots.forEach(d => {
                (d as HTMLElement).style.opacity = "0";
                (d as HTMLElement).style.transform = "scale(0)";
            });
            animate(dots, {
                opacity: [0, 1], scale: [0, 1],
                delay: (_el, i) => i * popGap,
                duration: popDur, ease: "outBack",
            });
            const totalTime = dots.length * popGap + popDur + 200;
            phaseTimer.current = setTimeout(() => setVisPhase("fly"), totalTime);
        }

        // Helper: create a traveling dot that moves from one element to another along a path
        const launchTraveler = (color: string, fromEl: Element, toEl: Element, dur: number, onDone: () => void) => {
            const rootRect = root.getBoundingClientRect();
            const fromRect = fromEl.getBoundingClientRect();
            const toRect = toEl.getBoundingClientRect();
            const startX = fromRect.left + fromRect.width / 2 - rootRect.left;
            const startY = fromRect.top + fromRect.height / 2 - rootRect.top;
            const endX = toRect.left + toRect.width / 2 - rootRect.left;
            const endY = toRect.top + toRect.height / 2 - rootRect.top;

            const traveler = document.createElement("div");
            traveler.style.cssText = `
                position:absolute; width:${DOT}px; height:${DOT}px; border-radius:50%;
                background:${color}; left:${startX - DOT / 2}px; top:${startY - DOT / 2}px;
                z-index:10; pointer-events:none; box-shadow: 0 0 6px ${color}80;
            `;
            root.appendChild(traveler);

            animate(traveler, {
                left: `${endX - DOT / 2}px`,
                top: `${endY - DOT / 2}px`,
                duration: dur, ease: "inOutQuad",
                onComplete: () => {
                    traveler.remove();
                    onDone();
                },
            });
        };

        if (visPhase === "fly" && isAddition) {
            // ADDITION: traveling dot from part circle → whole circle, one by one
            const targetCircle = root.querySelector(".bond-target");
            const targetCounter = root.querySelector(".target-counter");
            const targetDotsContainer = root.querySelector(".target-dots");
            const circleA = root.querySelector(".circle-a");
            const circleB = root.querySelector(".circle-b");
            if (!targetCircle || !targetDotsContainer || !circleA || !circleB) return;

            if (targetCounter) (targetCounter as HTMLElement).textContent = "?";
            const srcDots = root.querySelectorAll(".src-dot");
            const tgtDots = targetDotsContainer.querySelectorAll(".tgt-dot");
            tgtDots.forEach(d => { (d as HTMLElement).style.opacity = "0"; });

            let cumDelay = 0;
            srcDots.forEach((srcDot, i) => {
                const startAt = cumDelay;
                const isA = i < bond.partA;
                const fromCircle = isA ? circleA : circleB;
                const color = (srcDot as HTMLElement).dataset.color || "#999";

                const t = setTimeout(() => {
                    // Ghost source dot
                    const el = srcDot as HTMLElement;
                    el.style.background = "transparent";
                    el.style.border = `2px dotted ${color}`;
                    el.style.opacity = "0.35";

                    // Launch traveler along the line
                    launchTraveler(color, fromCircle, targetCircle, flyDur, () => {
                        if (tgtDots[i]) {
                            const td = tgtDots[i] as HTMLElement;
                            td.style.opacity = "1";
                            animate(td, { scale: [0, 1], opacity: [0, 1], duration: 200, ease: "outBack" });
                        }
                        if (targetCounter) (targetCounter as HTMLElement).textContent = String(i + 1);
                        sfxPop(i);
                        animate(targetCircle, { scale: [1, 1.08, 1], duration: 200, ease: "outQuad" });
                    });
                }, startAt);
                flyTimers.current.push(t);
                cumDelay += flyDur + 80; // wait for traveler to arrive + small gap
            });

            const tDone = setTimeout(() => {
                sfxDone();
                animate(targetCircle, { scale: [1, 1.25, 1], duration: 500, ease: "outElastic(1, .4)" });
            }, cumDelay);
            flyTimers.current.push(tDone);
            phaseTimer.current = setTimeout(() => setVisPhase("done"), cumDelay + 400);
        }

        if (visPhase === "fly" && !isAddition) {
            // SUBTRACTION: whole dots next to whole. Ghost out known part from end,
            // counter counts down. Then remaining src dots ghost one-by-one,
            // each popping an answer dot next to the answer circle.
            const wholeCircle = root.querySelector(".bond-target");
            const wholeCounter = root.querySelector(".target-counter");
            const answerCircle = bond.missing === "partA"
                ? root.querySelector(".circle-a") : root.querySelector(".circle-b");
            const answerDotsContainer = root.querySelector(".answer-dots");
            if (!wholeCircle || !wholeCounter) return;

            (wholeCounter as HTMLElement).textContent = String(bond.whole);

            const srcDots = root.querySelectorAll(".src-dot");
            const knownCount = bond.missing === "partA" ? bond.partB : bond.partA;
            const answerCount = getAnswer(bond);
            const step = flyDur * 0.4;

            // Get the known part's circle and its dot container
            const knownCircle = bond.missing === "partA"
                ? root.querySelector(".circle-b") : root.querySelector(".circle-a");
            const knownDotsContainer = root.querySelector(".known-dots");
            const knDots = knownDotsContainer?.querySelectorAll(".kn-dot");
            if (knDots) knDots.forEach(d => { (d as HTMLElement).style.opacity = "0"; });

            // Phase 1: Traveling dots from whole → known circle, ghost src from end
            let cumDelay = 0;
            for (let k = 0; k < knownCount; k++) {
                const idx = srcDots.length - 1 - k;
                const startAt = cumDelay;
                const tGhost = setTimeout(() => {
                    if (srcDots[idx]) {
                        const el = srcDots[idx] as HTMLElement;
                        const color = el.dataset.color || "#999";
                        el.style.background = "transparent";
                        el.style.border = `2px dotted ${color}`;
                        el.style.opacity = "0.35";

                        launchTraveler(color, wholeCircle, knownCircle!, flyDur, () => {
                            // Pop a dot next to the known circle
                            if (knDots && knDots[k]) {
                                const td = knDots[k] as HTMLElement;
                                td.style.opacity = "1";
                                animate(td, { scale: [0, 1], opacity: [0, 1], duration: 200, ease: "outBack" });
                            }
                            sfxPop(k);
                            if (knownCircle) animate(knownCircle, { scale: [1, 1.08, 1], duration: 200, ease: "outQuad" });
                        });
                    }
                }, startAt);
                flyTimers.current.push(tGhost);
                cumDelay += flyDur + 80;
            }

            cumDelay += 300;

            const answerCounter = root.querySelector(".answer-counter");

            // Phase 2: Traveling dots from whole → answer circle, ghost remaining src
            const ansDots = answerDotsContainer?.querySelectorAll(".ans-dot");
            if (ansDots) {
                ansDots.forEach(d => { (d as HTMLElement).style.opacity = "0"; });
            }

            for (let k = 0; k < answerCount; k++) {
                const srcIdx = k;
                const startAt = cumDelay;

                const t = setTimeout(() => {
                    if (srcDots[srcIdx]) {
                        const el = srcDots[srcIdx] as HTMLElement;
                        const color = el.dataset.color || "#999";
                        el.style.background = "transparent";
                        el.style.border = `2px dotted ${color}`;
                        el.style.opacity = "0.35";

                        launchTraveler(color, wholeCircle, answerCircle!, flyDur, () => {
                            if (ansDots && ansDots[k]) {
                                const td = ansDots[k] as HTMLElement;
                                td.style.opacity = "1";
                                animate(td, { scale: [0, 1], opacity: [0, 1], duration: 200, ease: "outBack" });
                            }
                            if (answerCounter) (answerCounter as HTMLElement).textContent = String(k + 1);
                            sfxPop(knownCount + k);
                            if (answerCircle) animate(answerCircle, { scale: [1, 1.08, 1], duration: 200, ease: "outQuad" });
                        });
                    }
                }, startAt);
                flyTimers.current.push(t);
                cumDelay += flyDur + 80;
            }

            const tDone = setTimeout(() => {
                sfxDone();
                if (answerCircle) {
                    animate(answerCircle, { scale: [1, 1.25, 1], duration: 500, ease: "outElastic(1, .4)" });
                }
            }, cumDelay);
            flyTimers.current.push(tDone);
            phaseTimer.current = setTimeout(() => setVisPhase("done"), cumDelay + 400);
        }
    }, [visPhase, bond, isAddition]);

    const handleAnswer = (val: number) => {
        if (!bond || feedback || visPhase !== "hidden") return;
        if (val === getAnswer(bond)) {
            setFeedback("🎉 Correct!");
            setScore(s => s + 1);
            setStreak(s => s + 1);
            sfxCorrect();
            if (diagramRef.current) {
                animate(diagramRef.current, {
                    scale: [1, 1.15, 1], duration: 500, ease: "outElastic(1, .4)",
                });
            }
            if (showVis) {
                phaseTimer.current = setTimeout(() => setVisPhase("expand"), 600);
            }
        } else {
            setFeedback("❌ Try again!");
            setStreak(0);
            sfxWrong();
            if (feedbackRef.current) {
                animate(feedbackRef.current, {
                    translateX: [0, -10, 10, -6, 6, 0], duration: 400, ease: "inOutQuad",
                });
            }
            setTimeout(() => setFeedback(""), 800);
        }
    };

    // Horizontal dot row, grouped by ROW_MAX per row, with per-dot color support
    const renderDotRow = (count: number, color: string, cls: string) => {
        const rows: number[] = [];
        let remaining = count;
        while (remaining > 0) {
            rows.push(Math.min(remaining, ROW_MAX));
            remaining -= ROW_MAX;
        }
        return (
            <Box display="flex" flexDirection="column" gap={`${DOT_GAP}px`}>
                {rows.map((n, r) => (
                    <HStack key={r} gap={`${DOT_GAP}px`}>
                        {Array.from({ length: n }, (_, i) => (
                            <Box key={`${r}-${i}`} className={cls} data-color={color}
                                w={`${DOT}px`} h={`${DOT}px`} borderRadius="50%"
                                bg={color} flexShrink={0} />
                        ))}
                    </HStack>
                ))}
            </Box>
        );
    };

    // Combined dot row for target: partA color then partB color, grouped by ROW_MAX
    const renderTargetDots = (a: number, b: number, cls: string) => {
        const total = a + b;
        const rows: number[] = [];
        let remaining = total;
        while (remaining > 0) {
            rows.push(Math.min(remaining, ROW_MAX));
            remaining -= ROW_MAX;
        }
        let idx = 0;
        return (
            <Box display="flex" flexDirection="column" gap={`${DOT_GAP}px`}>
                {rows.map((n, r) => {
                    const dots = Array.from({ length: n }, () => {
                        const color = idx < a ? COLOR_A : COLOR_B;
                        const dot = (
                            <Box key={idx} className={cls} data-color={color}
                                w={`${DOT}px`} h={`${DOT}px`} borderRadius="50%"
                                bg={color} flexShrink={0} />
                        );
                        idx++;
                        return dot;
                    });
                    return <HStack key={r} gap={`${DOT_GAP}px`}>{dots}</HStack>;
                })}
            </Box>
        );
    };

    const srcDotsVisible = showVis && (visPhase === "expand" || visPhase === "fly" || visPhase === "done");
    const tgtDotsVisible = showVis && (visPhase === "fly" || visPhase === "done");
    const knownDotsVisible = showVis && !isAddition && (visPhase === "fly" || visPhase === "done");
    const ansDotsVisible = showVis && !isAddition && (visPhase === "fly" || visPhase === "done");

    const hint = bond
        ? bond.missing === "whole"
            ? `${bond.partA} + ${bond.partB} = ?`
            : bond.missing === "partA"
                ? `${bond.whole} − ${bond.partB} = ?`
                : `${bond.whole} − ${bond.partA} = ?`
        : "";

    return (
        <Box minH="100vh" bg="linear-gradient(135deg, #E0F7FA 0%, #F3E5F5 50%, #FFF9C4 100%)">
            <Navbar />
            <VStack gap={5} p={6} maxW={520} mx="auto">
                <Text fontSize="4xl" fontWeight="bold" color="#5B21B6">🔗 Number Bonds</Text>

                <HStack gap={2}>
                    {([["add", "➕ Addition"], ["sub", "➖ Subtraction"], ["mix", "🔀 Mix"]] as const).map(([m, label]) => (
                        <Button key={m} onClick={() => setMode(m)}
                            bg={mode === m ? "#7C3AED" : "white"} color={mode === m ? "white" : "#7C3AED"}
                            border="2px solid #7C3AED" borderRadius="xl" fontSize="md" fontWeight="bold"
                            _hover={{ bg: mode === m ? "#6D28D9" : "#EDE9FE" }}>
                            {label}
                        </Button>
                    ))}
                </HStack>

                <HStack gap={4} flexWrap="wrap" justifyContent="center">
                    <Text fontSize="lg" fontWeight="bold" color="#059669">⭐ Score: {score}</Text>
                    <Text fontSize="lg" fontWeight="bold" color="#D97706">🔥 Streak: {streak}</Text>
                    <Button size="sm" onClick={() => setShowVis(v => !v)}
                        bg={showVis ? "#7C3AED" : "white"} color={showVis ? "white" : "#7C3AED"}
                        border="2px solid #7C3AED" borderRadius="lg" fontSize="sm"
                        _hover={{ bg: showVis ? "#6D28D9" : "#EDE9FE" }}>
                        {showVis ? "👁 Visual ON" : "👁🗨 Visual OFF"}
                    </Button>
                </HStack>

                {showVis && (
                    <HStack gap={2} alignItems="center">
                        <Text fontSize="sm" fontWeight="bold" color="#5B21B6">🐢</Text>
                        {[1, 2, 3, 4].map(s => (
                            <Button key={s} size="sm" onClick={() => setSpeed(s)}
                                w="36px" h="36px" fontSize="md" fontWeight="bold"
                                bg={speed === s ? "#7C3AED" : "white"}
                                color={speed === s ? "white" : "#7C3AED"}
                                border="2px solid #7C3AED" borderRadius="full"
                                _hover={{ bg: speed === s ? "#6D28D9" : "#EDE9FE" }}>
                                {s}
                            </Button>
                        ))}
                        <Text fontSize="sm" fontWeight="bold" color="#5B21B6">🐇</Text>
                    </HStack>
                )}

                {bond && (
                    <Box bg="white" borderRadius="2xl" p={6} boxShadow="lg" border="3px solid #C084FC" w="full"
                        overflow="visible">
                        <VStack ref={diagramRef} gap={0} mb={4} position="relative">
                            {/* Whole circle centered on top */}
                            <Box position="relative">
                                <Box className="bond-circle bond-target"
                                    style={{ ...BOND_CIRCLE_STYLE,
                                        background: bond.missing === "whole" ? "#FEF3C7" : "#EDE9FE",
                                        color: "#5B21B6" }}
                                    opacity={0}>
                                    <span className="target-counter">
                                        {visPhase === "done" ? bond.whole : bond.missing === "whole" ? "?" : bond.whole}
                                    </span>
                                </Box>
                                {/* Addition: target dots to the right of whole */}
                                {isAddition && (
                                    <Box className="target-dots" position="absolute" left={`${CIRCLE + 8}px`} top="50%"
                                        style={{ transform: "translateY(-50%)" }}
                                        visibility={tgtDotsVisible ? "visible" : "hidden"}>
                                        {renderTargetDots(bond.partA, bond.partB, "tgt-dot")}
                                    </Box>
                                )}
                                {/* Subtraction: src dots to the right of whole */}
                                {!isAddition && (
                                    <Box position="absolute" left={`${CIRCLE + 8}px`} top="50%"
                                        style={{ transform: "translateY(-50%)" }}
                                        visibility={srcDotsVisible ? "visible" : "hidden"}>
                                        {renderTargetDots(bond.missing === "partA" ? bond.partA : bond.partB,
                                            bond.missing === "partA" ? bond.partB : bond.partA, "src-dot")}
                                    </Box>
                                )}
                            </Box>

                            {/* V-lines */}
                            <svg width="200" height="40" style={{ margin: "-6px 0" }}>
                                <line x1="100" y1="0" x2="50" y2="40" stroke="#7C3AED" strokeWidth="3" />
                                <line x1="100" y1="0" x2="150" y2="40" stroke="#7C3AED" strokeWidth="3" />
                            </svg>

                            {/* Part circles side by side */}
                            <HStack gap={10} justifyContent="center">
                                {/* Part A — dots to the left */}
                                <Box position="relative">
                                    <Box className="bond-circle circle-a"
                                        style={{ ...BOND_CIRCLE_STYLE,
                                            background: bond.missing === "partA" ? "#FEF3C7" : "#DBEAFE",
                                            color: "#1E40AF" }}
                                        opacity={0}>
                                        <span className={bond.missing === "partA" ? "answer-counter" : "known-counter"}>
                                            {bond.missing === "partA"
                                                ? (visPhase === "done" ? bond.partA : "?")
                                                : bond.partA}
                                        </span>
                                    </Box>
                                    {/* Addition: src dots left of partA */}
                                    {isAddition && (
                                        <Box position="absolute" right={`${CIRCLE + 8}px`} top="50%"
                                            style={{ transform: "translateY(-50%)" }}
                                            visibility={srcDotsVisible ? "visible" : "hidden"}>
                                            {renderDotRow(bond.partA, COLOR_A, "src-dot")}
                                        </Box>
                                    )}
                                    {/* Subtraction: answer dots left of partA (if partA is missing) */}
                                    {bond.missing === "partA" && (
                                        <Box className="answer-dots" position="absolute" right={`${CIRCLE + 8}px`} top="50%"
                                            style={{ transform: "translateY(-50%)" }}
                                            visibility={ansDotsVisible ? "visible" : "hidden"}>
                                            {renderDotRow(bond.partA, COLOR_A, "ans-dot")}
                                        </Box>
                                    )}
                                    {/* Subtraction: known dots left of partA (if partB is missing, partA is known) */}
                                    {bond.missing === "partB" && (
                                        <Box className="known-dots" position="absolute" right={`${CIRCLE + 8}px`} top="50%"
                                            style={{ transform: "translateY(-50%)" }}
                                            visibility={knownDotsVisible ? "visible" : "hidden"}>
                                            {renderDotRow(bond.partA, COLOR_A, "kn-dot")}
                                        </Box>
                                    )}
                                </Box>
                                {/* Part B — dots to the right */}
                                <Box position="relative">
                                    <Box className="bond-circle circle-b"
                                        style={{ ...BOND_CIRCLE_STYLE,
                                            background: bond.missing === "partB" ? "#FEF3C7" : "#DBEAFE",
                                            color: "#1E40AF" }}
                                        opacity={0}>
                                        <span className={bond.missing === "partB" ? "answer-counter" : "known-counter"}>
                                            {bond.missing === "partB"
                                                ? (visPhase === "done" ? bond.partB : "?")
                                                : bond.partB}
                                        </span>
                                    </Box>
                                    {/* Addition: src dots right of partB */}
                                    {isAddition && (
                                        <Box position="absolute" left={`${CIRCLE + 8}px`} top="50%"
                                            style={{ transform: "translateY(-50%)" }}
                                            visibility={srcDotsVisible ? "visible" : "hidden"}>
                                            {renderDotRow(bond.partB, COLOR_B, "src-dot")}
                                        </Box>
                                    )}
                                    {/* Subtraction: answer dots right of partB (if partB is missing) */}
                                    {bond.missing === "partB" && (
                                        <Box className="answer-dots" position="absolute" left={`${CIRCLE + 8}px`} top="50%"
                                            style={{ transform: "translateY(-50%)" }}
                                            visibility={ansDotsVisible ? "visible" : "hidden"}>
                                            {renderDotRow(bond.partB, COLOR_B, "ans-dot")}
                                        </Box>
                                    )}
                                    {/* Subtraction: known dots right of partB (if partA is missing, partB is known) */}
                                    {bond.missing === "partA" && (
                                        <Box className="known-dots" position="absolute" left={`${CIRCLE + 8}px`} top="50%"
                                            style={{ transform: "translateY(-50%)" }}
                                            visibility={knownDotsVisible ? "visible" : "hidden"}>
                                            {renderDotRow(bond.partB, COLOR_B, "kn-dot")}
                                        </Box>
                                    )}
                                </Box>
                            </HStack>
                        </VStack>

                        {/* Hint equation */}
                        <Text fontSize="2xl" fontWeight="bold" textAlign="center" color="#1E293B" mb={3}>
                            {visPhase === "done"
                                ? (isAddition
                                    ? `${bond.partA} + ${bond.partB} = ${bond.whole}`
                                    : bond.missing === "partA"
                                        ? `${bond.whole} − ${bond.partB} = ${bond.partA}`
                                        : `${bond.whole} − ${bond.partA} = ${bond.partB}`)
                                : hint}
                        </Text>

                        {/* Choices */}
                        {visPhase === "hidden" && (
                            <HStack gap={3} justifyContent="center" flexWrap="wrap">
                                {choices.map(c => (
                                    <Button key={c} onClick={() => handleAnswer(c)}
                                        w="64px" h="64px" fontSize="2xl" fontWeight="bold"
                                        bg="#FEF3C7" color="#92400E" border="3px solid #FBBF24" borderRadius="xl"
                                        _hover={{ bg: "#FDE68A", transform: "scale(1.1)" }} transition="all 0.15s">
                                        {c}
                                    </Button>
                                ))}
                            </HStack>
                        )}

                        {/* Feedback */}
                        <Box ref={feedbackRef} mt={4} minH="40px">
                            {feedback && (
                                <Text fontSize="2xl" fontWeight="bold" textAlign="center"
                                    color={feedback.includes("🎉") ? "#059669" : "#DC2626"}>
                                    {feedback}
                                </Text>
                            )}
                        </Box>

                        {/* Next button */}
                        {(visPhase === "done" || (feedback.includes("🎉") && !showVis)) && (
                            <Box mt={4} textAlign="center">
                                <Button onClick={() => newRound(mode)}
                                    bg="#059669" color="white" fontSize="lg" fontWeight="bold"
                                    borderRadius="xl" px={8} py={6}
                                    _hover={{ bg: "#047857", transform: "scale(1.05)" }} transition="all 0.15s">
                                    Next ➜
                                </Button>
                            </Box>
                        )}
                    </Box>
                )}
            </VStack>
        </Box>
    );
}
