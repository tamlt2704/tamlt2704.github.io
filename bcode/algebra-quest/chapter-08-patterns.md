# Chapter 8: Patterns and Functions — "The Pattern Machine"

[← Chapter 7: The Hungry Alligator](chapter-07-inequalities.md) | [Chapter 9: Ancient Scrolls →](chapter-09-word-problems.md)

---

## The Quest

You discover the **Dragon's Lair Observatory** — a tower where scholars track the movements of Numeria's dragons. The dragons fly in patterns, and if you can figure out the pattern, you can predict where they'll go next.

> "Dragons are creatures of habit," Professor Zap explains, adjusting his telescope. "They follow rules. If you can find the rule, you can predict their next move. In math, we call these rules **functions**. Think of them as pattern machines!"

## Function Machines

A **function** is like a machine: you put a number IN, it follows a rule, and a number comes OUT.

```
    INPUT          RULE           OUTPUT
    ┌───┐      ┌────────┐       ┌───┐
    │ 3 │ ───→ │  × 2   │ ───→ │ 6 │
    └───┘      └────────┘       └───┘

    ┌───┐      ┌────────┐       ┌───┐
    │ 5 │ ───→ │  × 2   │ ───→ │10 │
    └───┘      └────────┘       └───┘

    ┌───┐      ┌────────┐       ┌───┐
    │ 7 │ ───→ │  × 2   │ ───→ │14 │
    └───┘      └────────┘       └───┘
```

The rule here is "multiply by 2." We can write it as: **y = 2x**

- x = the input (what goes in)
- y = the output (what comes out)
- The rule connects them

## Finding the Pattern

Look at this table. Can you spot the rule?

| Input (x) | Output (y) |
|---|---|
| 1 | 5 |
| 2 | 7 |
| 3 | 9 |
| 4 | 11 |
| 5 | ? |

**Step 1:** Look at how y changes each time x goes up by 1:
- 5 → 7 (went up by 2)
- 7 → 9 (went up by 2)
- 9 → 11 (went up by 2)

The output goes up by 2 each time! So the rule involves "× 2."

**Step 2:** Check if y = 2x works:
- When x = 1: 2(1) = 2... but y should be 5. Not quite!

**Step 3:** There's a shift. y is always 3 more than 2x:
- When x = 1: 2(1) + 3 = 5 ✓
- When x = 2: 2(2) + 3 = 7 ✓
- When x = 3: 2(3) + 3 = 9 ✓

**The rule is: y = 2x + 3**

So when x = 5: y = 2(5) + 3 = **13**

## How to Find Any Rule

> "Here's my secret method," Professor Zap whispers:
>
> 1. Find how much y changes when x goes up by 1 — that's your **multiplier**
> 2. Check: does (multiplier × x) give you y? If yes, done!
> 3. If not, figure out what you need to add or subtract to make it work

**Example:** Find the rule:

| x | y |
|---|---|
| 1 | 4 |
| 2 | 7 |
| 3 | 10 |
| 4 | 13 |

- y goes up by 3 each time → multiplier is 3
- Does 3x work? 3(1) = 3, but y = 4. Off by 1.
- Rule: **y = 3x + 1** ✓

Check: 3(4) + 1 = 13 ✓

## Graphing Points

You can plot function values on a **coordinate grid**. Each pair (x, y) is a point:

For y = 2x + 1:

| x | y | Point |
|---|---|---|
| 0 | 1 | (0, 1) |
| 1 | 3 | (1, 3) |
| 2 | 5 | (2, 5) |
| 3 | 7 | (3, 7) |

```
    y
    8 ┤
    7 ┤              ●  (3, 7)
    6 ┤            /
    5 ┤          ●  (2, 5)
    4 ┤        /
    3 ┤      ●  (1, 3)
    2 ┤    /
    1 ┤  ●  (0, 1)
    0 ┼──┼──┼──┼──┼── x
       0  1  2  3  4
```

Notice: the points form a straight line! That's because our rule is **linear** (it makes a line). All rules in the form y = mx + b make straight lines.

## Reading a Graph

You can also go backwards — read a graph to find values. If you see points at (0,4), (1,6), (2,8), (3,10):
- Goes up by 2 each time → multiplier is 2
- Starts at 4 when x = 0
- Rule: **y = 2x + 4**

## Try It! 🎯

**Find the rule for each table:**

1.
| x | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| y | 3 | 6 | 9 | 12 |

2.
| x | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| y | 5 | 8 | 11 | 14 |

3.
| x | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| y | 4 | 5 | 6 | 7 |

**What's the next output?**

4. Rule: y = 4x - 1. If x = 6, what is y?
5. Rule: y = x + 10. If x = 25, what is y?

<details>
<summary>Check Your Answers</summary>

1. y goes up by 3, and 3(1) = 3 ✓ → **y = 3x**
2. y goes up by 3, and 3(1) = 3, but y = 5 (off by 2) → **y = 3x + 2**
3. y goes up by 1, and starts at 4 → **y = x + 4**
4. y = 4(6) - 1 = 24 - 1 = **23**
5. y = 25 + 10 = **35**

</details>

## The Dragon Prediction Quest 🐉

The observatory has been tracking a dragon's flight path:

```
╔══════════════════════════════════════════════╗
║  DRAGON FLIGHT LOG                           ║
║                                              ║
║  Hour 1: Dragon is at height 10             ║
║  Hour 2: Dragon is at height 15             ║
║  Hour 3: Dragon is at height 20             ║
║  Hour 4: Dragon is at height 25             ║
║  Hour 5: Dragon is at height ???            ║
║                                              ║
║  Questions:                                  ║
║  1. What's the rule? (height = ?)            ║
║  2. What height at hour 5?                   ║
║  3. At what hour will it reach height 50?    ║
╚══════════════════════════════════════════════╝
```

<details>
<summary>Solution</summary>

Finding the rule:
- Height goes up by 5 each hour → multiplier is 5
- At hour 1: 5(1) = 5, but height = 10 (off by 5)
- Rule: **height = 5x + 5** (where x = hour number)

Check: 5(4) + 5 = 25 ✓

**Question 1:** height = 5x + 5

**Question 2:** At hour 5: 5(5) + 5 = **30**

**Question 3:** When does height = 50?
- 5x + 5 = 50
- 5x = 45
- x = 9
- The dragon reaches height 50 at **hour 9**!

Professor Zap scribbles in his notebook: "Alert the village — dragon overhead at hour 9!"

</details>

## Level Up! 📈

What you learned:
- A **function** is a rule that turns inputs into outputs
- You can find the rule by looking at how y changes when x goes up by 1
- Rules like y = 2x + 3 are called **linear functions** (they make lines)
- You can represent functions as tables, rules, or graphs
- Functions let you **predict** values you haven't seen yet

## Did You Know? 🌟

Weather forecasters use functions to predict temperature! If the temperature has been rising 2 degrees per hour, they can write a function and predict what it'll be in 3 hours. Sports analysts do the same thing — if a basketball player scores about 5 points per quarter, they can predict the final score. Pattern-finding is a superpower!

---

**Next up:** [Chapter 9: Translating the Ancient Scrolls →](chapter-09-word-problems.md)
