# Chapter 33: Chess — From Zero to Intermediate

## What you'll learn

- The board, pieces, and how they move
- Special moves: castling, en passant, promotion
- Algebraic notation (reading and writing chess moves)
- Opening principles (the first 10 moves)
- Tactics: forks, pins, skewers, discovered attacks
- Basic endgames: King + Queen, King + Rook, King + Pawn
- Strategy: piece activity, pawn structure, king safety
- How to study and improve (resources, puzzles, analysis)

---

## PART 1: The Basics

## 33.1 The board

```
    a   b   c   d   e   f   g   h
  ┌───┬───┬───┬───┬───┬───┬───┬───┐
8 │ ♜ │ ♞ │ ♝ │ ♛ │ ♚ │ ♝ │ ♞ │ ♜ │  8   Black
  ├───┼───┼───┼───┼───┼───┼───┼───┤
7 │ ♟ │ ♟ │ ♟ │ ♟ │ ♟ │ ♟ │ ♟ │ ♟ │  7
  ├───┼───┼───┼───┼───┼───┼───┼───┤
6 │   │   │   │   │   │   │   │   │  6
  ├───┼───┼───┼───┼───┼───┼───┼───┤
5 │   │   │   │   │   │   │   │   │  5
  ├───┼───┼───┼───┼───┼───┼───┼───┤
4 │   │   │   │   │   │   │   │   │  4
  ├───┼───┼───┼───┼───┼───┼───┼───┤
3 │   │   │   │   │   │   │   │   │  3
  ├───┼───┼───┼───┼───┼───┼───┼───┤
2 │ ♙ │ ♙ │ ♙ │ ♙ │ ♙ │ ♙ │ ♙ │ ♙ │  2
  ├───┼───┼───┼───┼───┼───┼───┼───┤
1 │ ♖ │ ♘ │ ♗ │ ♕ │ ♔ │ ♗ │ ♘ │ ♖ │  1   White
  └───┴───┴───┴───┴───┴───┴───┴───┘
    a   b   c   d   e   f   g   h
```

- 8×8 grid, alternating light/dark squares
- Columns = **files** (a through h, left to right)
- Rows = **ranks** (1 through 8, bottom to top from White's view)
- Every square has a coordinate: `e4`, `d7`, `a1`
- White always starts at ranks 1-2, Black at ranks 7-8
- The board is set up so a **light square is in each player's right corner**

## 33.2 The pieces and how they move

| Piece | Symbol | Value | Movement |
|-------|--------|-------|----------|
| **King** ♔♚ | K | ∞ (game over if captured) | 1 square in any direction |
| **Queen** ♕♛ | Q | 9 | Any direction, any distance (rook + bishop) |
| **Rook** ♖♜ | R | 5 | Straight lines (horizontal or vertical), any distance |
| **Bishop** ♗♝ | B | 3 | Diagonal lines, any distance |
| **Knight** ♘♞ | N | 3 | "L-shape": 2+1 squares, JUMPS over pieces |
| **Pawn** ♙♟ | (none) | 1 | Forward 1 (or 2 from starting position), captures diagonally |

**Piece values** are approximate guides for trading. Losing a Queen (9) for a Bishop (3) is bad. Trading a Knight (3) for a Bishop (3) is usually equal.

### King ♔
```
  . . . . .
  . x x x .
  . x K x .
  . x x x .
  . . . . .
```
Moves 1 square in any direction. Can never move INTO check (where it would be attacked).

### Queen ♕
```
  x . . x . . x
  . x . x . x .
  . . x x x . .
  x x x Q x x x
  . . x x x . .
  . x . x . x .
  x . . x . . x
```
Combines rook + bishop. Most powerful piece.

### Rook ♖
```
  . . . x . . .
  . . . x . . .
  . . . x . . .
  x x x R x x x
  . . . x . . .
  . . . x . . .
  . . . x . . .
```
Straight lines only (horizontal + vertical).

### Bishop ♗
```
  x . . . . . x
  . x . . . x .
  . . x . x . .
  . . . B . . .
  . . x . x . .
  . x . . . x .
  x . . . . . x
```
Diagonals only. Stays on its starting colour forever (light-squared bishop vs dark-squared bishop).

### Knight ♘
```
  . x . x .
  x . . . x
  . . N . .
  x . . . x
  . x . x .
```
L-shape: 2 squares in one direction, then 1 square perpendicular (or vice versa). The ONLY piece that jumps over others.

### Pawn ♙
```
  Moves:        Captures:
  . x .         . . .
  . x .         . x .   (only diagonal,
  . P .         . P .    only forward)
```
- Moves forward 1 square (never backward)
- First move: can go forward 2 squares
- Captures diagonally forward (1 square)
- Reaches the last rank → **promotes** to Queen, Rook, Bishop, or Knight (usually Queen)

## 33.3 Special moves

### Castling

King moves 2 squares toward a rook; rook jumps over the king. One move, moves two pieces.

```
Before (kingside):    After:
♖ . . . ♔ . . ♖     ♖ . . . . ♖ ♔ .
                       (Rook on f1, King on g1)

Before (queenside):   After:
♖ . . . ♔ . . ♖     . . ♔ ♖ . . . ♖
                       (King on c1, Rook on d1)
```

**Conditions (ALL must be true):**
- King has never moved
- That rook has never moved
- No pieces between king and rook
- King is not in check
- King doesn't pass through or land on an attacked square

**Why castle?** Tucks the king safely into the corner AND activates the rook. Do it early (usually by move 10).

### En passant

A special pawn capture that only exists to prevent pawns from "sneaking past":

```
Before:          Black plays d7-d5:    White captures en passant:
. . . . .        . . . . .             . . . . .
. . . p .        . . . . .             . . . P .  (White pawn on d6)
. . . . .        . . . p .             . . . . .  (Black pawn removed)
. . P . .        . . P p .             . . . . .
```

**Rule:** If a pawn moves 2 squares forward and lands beside an enemy pawn, the enemy can capture it "in passing" — as if it had only moved 1 square. Must be done IMMEDIATELY (next move only).

### Pawn promotion

When a pawn reaches the opposite end of the board (rank 8 for White, rank 1 for Black), it MUST promote to a Queen, Rook, Bishop, or Knight. Almost always choose Queen.

## 33.4 Check, checkmate, and draws

- **Check** — the king is under attack. You MUST escape (move king, block, or capture attacker).
- **Checkmate** — the king is in check and CANNOT escape. Game over. The attacking side wins.
- **Stalemate** — it's your turn, you're NOT in check, but you have NO legal moves. **Draw** (not a win!).

**Other draws:**
- Agreement (both players agree)
- Threefold repetition (same position 3 times)
- 50-move rule (50 moves with no pawn move or capture)
- Insufficient material (e.g., King vs King + Bishop — can't force checkmate)

## 33.5 Algebraic notation

Every move is written as: **Piece + destination square** (+ special symbols)

```
e4      — pawn to e4
Nf3     — Knight to f3
Bb5     — Bishop to b5
O-O     — kingside castling
O-O-O   — queenside castling
Qxd7    — Queen captures on d7 (x = captures)
Nbd2    — Knight from b-file to d2 (disambiguate when 2 knights can go there)
e8=Q    — pawn promotes to Queen on e8
Rf1+    — Rook to f1, gives check (+)
Qh7#    — Queen to h7, checkmate (#)
```

**Reading a game:**
```
1. e4 e5       (White pawn e4, Black pawn e5)
2. Nf3 Nc6    (White knight f3, Black knight c6)
3. Bb5 a6     (White bishop b5 — "Ruy Lopez", Black a6)
4. Ba4 Nf6    (Bishop retreats a4, Black knight f6)
```

---

## PART 2: Opening Principles

## 33.6 The first 10 moves — what matters

You don't need to memorize opening theory. Follow these principles:

**1. Control the centre (d4, d5, e4, e5)**
```
  . . . . . . . .
  . . . . . . . .
  . . . . . . . .
  . . . x x . . .     ← control these 4 squares
  . . . x x . . .
  . . . . . . . .
  . . . . . . . .
```
Pieces in the centre control more squares and have more options.

**2. Develop your pieces (get them off the back rank)**
- Knights before bishops (they have fewer good squares)
- Don't move the same piece twice (waste of tempo)
- Don't bring the queen out too early (gets chased by weaker pieces)

**3. Castle early (by move 8-10)**
- King safety first
- Connects the rooks

**4. Connect your rooks (no pieces between them)**
- Once castled and pieces developed, rooks can support each other

**Common beginner mistake order:**
```
❌ 1. Move same piece 3 times
❌ 2. Move queen out early
❌ 3. Move only edge pawns
❌ 4. Forget to castle

✅ 1. Centre pawn (e4 or d4)
✅ 2. Develop knight (Nf3)
✅ 3. Develop bishop (Bb5, Bc4, or Be2)
✅ 4. Castle (O-O)
✅ 5. Develop other knight/bishop
✅ 6. Connect rooks
```

## 33.7 Common openings (just know the names and ideas)

| Opening | Moves | Key idea |
|---------|-------|----------|
| **Italian Game** | 1.e4 e5 2.Nf3 Nc6 3.Bc4 | Target f7 (weakest square) |
| **Ruy Lopez** | 1.e4 e5 2.Nf3 Nc6 3.Bb5 | Pressure on e5 via the knight |
| **Queen's Gambit** | 1.d4 d5 2.c4 | Offer pawn to open centre |
| **Sicilian Defence** | 1.e4 c5 | Black fights for centre asymmetrically |
| **French Defence** | 1.e4 e6 | Solid, but locked-in bishop |
| **London System** | 1.d4 + 2.Bf4 | Simple setup, hard to mess up |

For beginners: play **1.e4** as White (open game, easier tactics) and the **Italian Game** or **London System** until you're comfortable.

---

## PART 3: Tactics

## 33.8 The building blocks of winning

> **80% of chess improvement below 2000 rating comes from tactics.** See a pattern, calculate, execute. No amount of strategy helps if you miss a free piece.

### Fork (one piece attacks two)

```
  . . . . . . . .
  . . . . . . . .
  . . ♜ . . . . .     Knight forks King AND Rook
  . . . . . . . .     Black must save King → loses Rook
  . . . ♘ . . . .
  . . . . . . . .
  . ♚ . . . . . .
  . . . . . . . .
```

Knights are the best forkers (jump over pieces, hard to see coming).

### Pin (piece can't move because it would expose a more valuable piece)

```
  . . . . . . . .
  . . . . ♚ . . .     Bishop pins the Knight to the King
  . . . . . . . .     If Knight moves → King is in check (illegal)
  . . . ♞ . . . .     Knight is "pinned"
  . . ♗ . . . . .
  . . . . . . . .
```

**Absolute pin:** pinned to King (piece literally CAN'T move — illegal).
**Relative pin:** pinned to Queen/Rook (piece CAN move but loses material).

### Skewer (like a pin in reverse — more valuable piece is in front)

```
  . . . . . . . .
  . . . . ♚ . . .     Bishop attacks King
  . . . . . . . .     King MUST move
  . . . . . . . .     → Bishop captures Rook behind it
  . . . . . . . .
  . . ♗ . . . . .
  . . . . . . . .
  . . . . ♜ . . .     (Rook exposed after King moves)
```

### Discovered attack (moving one piece reveals an attack from another)

```
Before:                   After Knight moves (with check!):
  . . . . . . . .         . . . . . . . .
  . . . . ♚ . . .         . . . ♘ ♚ . . .   ← Knight gives check
  . . . . . . . .         . . . . . . . .
  . . . ♘ . . . .         . . . . . . . .
  . . . . . . . .         . . . . . . . .     AND Rook attacks Queen
  . . . . . . . .         . . . . . . . .
  ♖ . . . . . ♛ .         ♖ . . . . . ♛ .   ← Rook now attacks Queen
```

### Back rank mate

```
  ♜ . . . . . ♔ .     Rook delivers checkmate on back rank
  ♙ ♙ ♙ . . ♙ ♙ ♙    King is trapped by its own pawns!
```

**Prevention:** Give your king a "luft" (escape square) — push h3 or g3.

## 33.9 How to train tactics

- **Chess.com Puzzles** — daily puzzles, rated progression
- **Lichess Puzzles** — free, unlimited, rated
- **Tempo**: solve 10-20 puzzles daily (consistency > volume)
- **Pattern**: don't calculate from scratch — recognise the theme first (is it a fork? pin? back rank?)
- **If stuck**: ask "what would I do if their piece wasn't there?" (reveals discovered attacks)

---

## PART 4: Endgames

## 33.10 Essential endgames to know

### King + Queen vs King

Always a win. Use the queen to push the enemy king to the edge, then bring your king close for checkmate.

```
Method: "Restrict → Approach → Checkmate"
1. Use Queen to cut off ranks/files (restrict king to smaller area)
2. Bring your King closer (need King + Queen together for mate)
3. Deliver checkmate on the edge

⚠️ Don't stalemate! Leave the enemy king at least 1 move.
```

### King + Rook vs King

Always a win. Push enemy king to the edge with the rook.

```
Method: "Cut off → Push → Checkmate"
1. Rook cuts off a rank (enemy king can't cross back)
2. Your King approaches
3. Keep cutting off, pushing king to edge
4. Checkmate with King + Rook on the edge

Example checkmate position:
  . . . ♚ . . . .     King on edge
  . . . ♖ . . . .     Rook cuts off
  . . . . . . . .
  . . . ♔ . . . .     Your King supports
```

### King + Pawn vs King

Win if:
- Your king is in front of the pawn
- The pawn hasn't reached the 5th/6th rank with the enemy king blocking

```
Key concept: "Opposition"
  . ♚ .       Kings face each other, one square apart
  . . .       The side NOT to move has "the opposition" (advantage)
  . ♔ .       Because the other must step aside

  . . ♚       White to move: Kd5! (seizes opposition)
  . . .       Now Black must step aside, and White's king
  . ♔ .       escorts the pawn to promotion
  . ♙ .
```

**Rule of thumb:** If your king is on the 6th rank in front of your pawn — you win (regardless of whose move it is).

---

## PART 5: Strategy

## 33.11 Positional thinking

Once you stop losing pieces to tactics, strategy matters:

**Piece activity** — every piece should have a job. A knight on the rim is grim (fewer squares). A bishop blocked by its own pawns is "bad."

**Pawn structure** — pawns can't go backward. Every pawn move is permanent.
- **Doubled pawns** (same file) — weak, hard to advance
- **Isolated pawn** — no neighbouring pawns to protect it
- **Passed pawn** — no enemy pawns can block/capture it (very strong in endgames)
- **Pawn chain** — diagonal line of pawns supporting each other

**King safety** — keep your king castled with pawns in front. Don't push the pawns in front of your castled king unless necessary.

**Open files** — files with no pawns belong to rooks. Get your rooks on open files.

**Outposts** — squares in the enemy camp that can't be attacked by pawns. Knights love outposts.

## 33.12 Planning

Every move should have a purpose. Ask yourself:
1. **What is my opponent's threat?** (Always check this FIRST)
2. **Are any of my pieces inactive?** (Improve your worst piece)
3. **Can I create a threat?** (Attack a weakness, pin, fork opportunity)
4. **Is there a pawn break?** (Can I open the position for my pieces?)

---

## PART 6: How to Improve

## 33.13 Study plan by rating

| Rating | Focus | Time split |
|--------|-------|-----------|
| Beginner (0-800) | Don't hang pieces, basic checkmates, complete development | 70% puzzles, 20% games, 10% endgames |
| Improving (800-1200) | Tactics (fork, pin, skewer), basic endgames, opening principles | 50% puzzles, 30% games, 20% endgames |
| Intermediate (1200-1600) | Deeper tactics, pawn structure, piece activity, opening repertoire | 40% puzzles, 30% games, 20% analysis, 10% openings |
| Advanced (1600-2000) | Positional play, complex endgames, opening theory, game analysis | 30% puzzles, 30% games, 20% analysis, 20% openings |

## 33.14 Resources

| Resource | Best for | Cost |
|----------|----------|------|
| **Lichess.org** | Playing, puzzles, analysis, courses | Free |
| **Chess.com** | Playing, puzzles, lessons, bots | Free (premium: $) |
| **"Play Winning Chess" (Seirawan)** | Absolute beginners | Book |
| **"How to Reassess Your Chess" (Silman)** | Intermediate strategy | Book |
| **Hanging Pawns (YouTube)** | Opening repertoire | Free |
| **GothamChess (YouTube)** | Entertainment + learning | Free |
| **Chessable** | Opening courses with spaced repetition | Free + paid |

## 33.15 The improvement loop

```
1. PLAY a game (10+0 or 15+10 time control — not bullet)
2. ANALYSE it afterward (use Lichess/Chess.com analysis board)
   - Find your mistakes (the computer shows blunders)
   - Ask: "What should I have done?"
   - Was it a tactical miss? Positional error? Opening mistake?
3. TRAIN the weakness
   - Missed a fork? → Do fork puzzles
   - Lost a won endgame? → Study that endgame
   - Got crushed in the opening? → Learn 5 moves deeper
4. REPEAT
```

> **The biggest mistake:** Playing hundreds of bullet games without analysing. You reinforce bad habits. One analysed game is worth ten unanalysed ones.

---

## Summary

✅ Board setup, piece movement, and point values
✅ Special moves: castling (king safety + rook activation), en passant, promotion
✅ Algebraic notation: read and write any chess game
✅ Opening principles: centre, develop, castle, connect rooks
✅ Tactics: fork, pin, skewer, discovered attack, back rank mate
✅ Essential endgames: K+Q vs K, K+R vs K, K+P vs K, opposition
✅ Strategy: piece activity, pawn structure, king safety, open files
✅ Improvement plan: puzzles daily, analyse games, study weaknesses

## Key takeaways

**Tactics win games, strategy guides you toward tactics.** Below 1600, almost every game is decided by a tactical blunder. Train pattern recognition (puzzles) relentlessly.

**Every move needs a reason.** "What is my opponent threatening? What's my worst-placed piece? Where can I create pressure?" If you can't answer these, you're moving randomly.

**Analyse your losses.** Not to feel bad — to find the moment where the game turned. Was it a missed tactic? A positional misjudgement? That's your next training target.

**Chess is infinite, but principles are finite.** Control the centre, develop pieces, castle early, don't hang material. These 4 rules will carry you to 1200+ without any theory.

---

→ [Back to Chapter 32: Kubernetes](./32-KUBERNETES.md)
