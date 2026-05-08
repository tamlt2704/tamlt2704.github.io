# Chapter 7: Greater Than, Less Than — "The Hungry Alligator"

[← Chapter 6: Variables on Both Sides](chapter-06-both-sides.md) | [Chapter 8: Patterns and Functions →](chapter-08-patterns.md)

---

## The Quest

In the Numeria Zoo, there's a mysterious creature behind a locked cage. The sign says:

```
╔══════════════════════════════════════════╗
║  MYSTERY CREATURE                        ║
║  Age: unknown                            ║
║  Clue: Its age is GREATER THAN 5        ║
║  but LESS THAN 12.                       ║
║                                          ║
║  What are all the possible ages?         ║
╚══════════════════════════════════════════╝
```

> "Not everything in math has ONE answer," says Professor Zap. "Sometimes there's a whole RANGE of answers. That's where inequalities come in — they tell you about relationships that aren't perfectly equal."

## Meet the Alligator

The symbols `<` and `>` are like an alligator's mouth. The alligator is hungry and ALWAYS eats the bigger number:

```
    5 < 8       The alligator eats 8 (it's bigger)
      🐊→

    10 > 3      The alligator eats 10 (it's bigger)
      ←🐊
```

**Memory trick:** The alligator's mouth OPENS toward the bigger number. The pointy end points at the smaller number.

| Symbol | Meaning | Example |
|---|---|---|
| < | less than | 3 < 7 (3 is less than 7) |
| > | greater than | 9 > 2 (9 is greater than 2) |
| ≤ | less than or equal to | x ≤ 5 (x is 5 or smaller) |
| ≥ | greater than or equal to | x ≥ 3 (x is 3 or bigger) |

## Inequalities with Variables

An **inequality** is like an equation, but instead of = it uses <, >, ≤, or ≥.

- `x > 5` means "x is any number bigger than 5"
- `x < 10` means "x is any number smaller than 10"
- `x ≥ 3` means "x is 3 or anything bigger"
- `x ≤ 7` means "x is 7 or anything smaller"

The difference from equations: **inequalities have MANY answers!**

If x > 5, then x could be 6, 7, 8, 100, 5.1, 5.001... anything bigger than 5!

## Solving Inequalities

Great news: you solve inequalities the SAME way you solve equations!

**Problem:** x + 3 > 7
```
    x + 3 > 7
    x + 3 - 3 > 7 - 3     ← subtract 3 from both sides
    x > 4
```

Answer: x is any number greater than 4.

**Problem:** x - 2 ≤ 6
```
    x - 2 ≤ 6
    x - 2 + 2 ≤ 6 + 2     ← add 2 to both sides
    x ≤ 8
```

Answer: x is 8 or any number less than 8.

**Problem:** 2x < 10
```
    2x < 10
    2x ÷ 2 < 10 ÷ 2       ← divide both sides by 2
    x < 5
```

Answer: x is any number less than 5.

## Graphing on a Number Line

We can show inequality answers on a number line:

**x > 4** (x is greater than 4, but NOT equal to 4):
```
  ←──┼──┼──┼──┼──┼──○━━━━━━━━━━━━━→
    -1  0  1  2  3  4  5  6  7  8
                    ↑
              open circle = "not including 4"
```

**x ≤ 6** (x is less than or equal to 6):
```
  ←━━━━━━━━━━━━━━━━━━━━●──┼──┼──┼──→
     1  2  3  4  5  6  7  8  9  10
                       ↑
              filled circle = "including 6"
```

**The rule:**
- **Open circle** ○ = NOT including that number (used with < and >)
- **Filled circle** ● = INCLUDING that number (used with ≤ and ≥)

## The Flip Rule ⚠️

There's ONE special rule for inequalities that's different from equations:

> **When you multiply or divide by a NEGATIVE number, FLIP the inequality sign!**

**Example:** -2x > 6
```
    -2x > 6
    -2x ÷ (-2) < 6 ÷ (-2)    ← divide by -2, FLIP the >
    x < -3
```

Why does it flip? Think about it: if you have 5 > 3, and you multiply both by -1, you get -5 and -3. But -5 is NOT greater than -3! It's less than -3. So the sign flips.

```
    5 > 3       ← true
    × (-1)
    -5 < -3     ← still true (sign flipped!)
```

> "This is the ONE tricky rule," says Professor Zap. "Multiplying by a negative flips everything around. Like looking in a mirror — left becomes right!"

## More Examples

**Example 1:** 3x + 1 > 10
```
    3x + 1 > 10
    3x > 9          ← subtract 1
    x > 3           ← divide by 3 (positive, no flip!)
```

**Example 2:** -3x ≥ 12
```
    -3x ≥ 12
    x ≤ -4          ← divide by -3, FLIP the sign!
```

## Try It! 🎯

Solve each inequality:

1. x + 5 > 9
2. x - 3 ≤ 4
3. 2x > 14
4. 3x + 2 < 17
5. -4x ≥ 8

<details>
<summary>Check Your Answers</summary>

1. x > 4
2. x ≤ 7
3. x > 7
4. 3x < 15 → x < 5
5. x ≤ -2 (divided by -4, flipped the sign!)

</details>

## The Mystery Creature Quest 🦎

Back at the zoo, you find more clues about the mystery creature:

```
╔══════════════════════════════════════════════╗
║  MYSTERY CREATURE CLUES                      ║
║                                              ║
║  Clue 1: Its age (a) plus 3 is greater      ║
║          than 8.                             ║
║          → a + 3 > 8                         ║
║                                              ║
║  Clue 2: Twice its age is less than or       ║
║          equal to 22.                        ║
║          → 2a ≤ 22                           ║
║                                              ║
║  Clue 3: Its age is a whole number.          ║
║                                              ║
║  What are ALL possible ages?                 ║
╚══════════════════════════════════════════════╝
```

<details>
<summary>Solution</summary>

Solve each clue:
- Clue 1: a + 3 > 8 → a > 5
- Clue 2: 2a ≤ 22 → a ≤ 11

So a > 5 AND a ≤ 11, and a is a whole number.

Possible ages: **6, 7, 8, 9, 10, 11**

On the number line:
```
  ←──┼──┼──┼──┼──○──●──●──●──●──●──●──┼──→
     0  1  2  3  4  5  6  7  8  9 10 11 12
                  ↑                       ↑
            not included            included
```

The zookeeper nods: "The creature is a Crystal Salamander. They live 6 to 11 years. Well done, adventurer!"

</details>

## Level Up! 📈

What you learned:
- Inequalities use <, >, ≤, ≥ instead of =
- They have MANY possible answers (a range)
- Solve them the same way as equations
- **Special rule:** multiply/divide by a negative → FLIP the sign
- Graph answers on a number line (open circle vs. filled circle)

## Did You Know? 🌟

Inequalities are everywhere in real life! Speed limits (speed ≤ 65 mph), age requirements (age ≥ 13 to sign up), temperature ranges (keep food below 40°F), and even game rules (need > 100 points to win). You use inequality thinking every day without realizing it!

---

**Next up:** [Chapter 8: Patterns and Functions →](chapter-08-patterns.md)
