# Chapter 67: Reading Skills — Read Faster, Remember More, Learn Anything

## What you'll learn

- Why most people read inefficiently (and the 3 habits slowing you down)
- 4 reading modes: skim, scan, study, deep — when to use each
- Speed reading techniques that ACTUALLY work (not gimmicks)
- How to retain what you read (without re-reading 5 times)
- Reading technical documentation effectively (docs, papers, code)
- Building a knowledge system (notes, connections, recall)
- A practical reading habit that fits a developer's schedule

---

## PART 1: Why Developers Need Better Reading Skills

## 67.1 How much you actually read daily

```
AS A DEVELOPER, YOU READ:
  • Documentation (APIs, libraries, frameworks)       — 30-60 min/day
  • Code (other people's, your own old code)          — 60-120 min/day
  • Slack/email (messages, threads, decisions)         — 30-60 min/day
  • Technical articles/blogs                          — 15-30 min/day
  • Error messages + Stack Overflow                   — 15-30 min/day
  • Books (if you make time)                          — 0-30 min/day

  TOTAL: 2.5-5+ hours of READING per day.
  A 20% improvement = 30-60 extra minutes of productive time.
  That's 2.5-5 extra hours per WEEK from better reading alone.
```

## 67.2 The 3 habits slowing you down

```
1. SUBVOCALISATION (saying words in your head):
   You "hear" every word internally → limits you to speech speed (~200 wpm)
   Your eyes can process text at 400-800 wpm — the voice is the bottleneck.
   
   FIX: Don't eliminate it entirely (needed for complex text).
         Reduce it for easy content: focus on MEANING, not individual words.
         Practice: try to "see" groups of words as images, not sounds.

2. REGRESSION (re-reading the same line):
   Eyes jump backwards 15-20% of reading time (you don't realise it).
   Usually from poor focus, not actual confusion.
   
   FIX: Use a pointer (finger, pen, cursor) to guide your eyes forward.
         Forces linear movement. Feels weird for 2 days, then becomes natural.
         Regression drops by 80% immediately.

3. READING EVERYTHING AT THE SAME SPEED:
   You read a novel, documentation, and a headline at the same pace.
   Not all text deserves equal attention.
   
   FIX: Use different MODES for different content (see Part 2).
```

---

## PART 2: The 4 Reading Modes

## 67.3 Mode 1: SKIM (get the shape — 1-2 min per article)

```
PURPOSE: Decide if this is worth reading fully. Get the main idea.
SPEED:  1000+ wpm (you're NOT reading every word)
USE FOR: news, blog posts, documentation overview, emails, Slack threads

HOW:
  1. Read the title and subtitle
  2. Read the first paragraph (usually contains the main point)
  3. Read headings/subheadings (the outline)
  4. Read the first sentence of each paragraph
  5. Read the conclusion/summary
  6. Look at images, diagrams, code blocks, bold text

AFTER SKIMMING, DECIDE:
  → "Not relevant" → move on (saved 10 minutes!)
  → "Interesting, need details" → switch to Study mode
  → "Need one specific thing" → switch to Scan mode

DEVELOPER EXAMPLES:
  • Skim a new library's README: get the idea, decide if it's worth trying
  • Skim a 20-message Slack thread: understand the decision without reading every message
  • Skim a blog post: "Is this relevant to my problem?"
```

## 67.4 Mode 2: SCAN (find specific info — 30 sec to 2 min)

```
PURPOSE: Find a specific fact, code snippet, or answer.
SPEED:  Very fast (you're searching, not reading)
USE FOR: documentation lookup, finding a function signature, Ctrl+F behaviour

HOW:
  1. Know what you're looking for BEFORE you start
  2. Scan visually for: keywords, code blocks, headings that match
  3. Jump (don't read linearly) — eyes dart around the page
  4. When found: read ONLY that section in detail
  5. Ignore everything else

DEVELOPER EXAMPLES:
  • API docs: "What's the return type of this function?"
  • Stack Overflow: scan answers for your error message
  • Long config file: find the specific setting you need
  • Codebase: find where a variable is defined
```

## 67.5 Mode 3: STUDY (learn and retain — focused, medium speed)

```
PURPOSE: Understand new concepts, learn a skill, absorb technical content.
SPEED:  150-300 wpm (slower than casual, but not painfully slow)
USE FOR: textbooks, tutorials, technical deep-dives, learning new frameworks

HOW:
  1. PREVIEW: skim first (2 min) to get the structure
  2. READ actively:
     - Ask questions as you go ("Why? How? What if?")
     - Highlight or mark KEY ideas (max 10-20% of text)
     - Pause after each section: "Can I explain this in one sentence?"
  3. SUMMARISE: after each chapter/article, write 3-5 bullet points from memory
  4. CONNECT: "How does this relate to what I already know?"
  5. APPLY: try it immediately (write code, do the exercise, build something)

THE KEY: You read slower, but you RETAIN 3-5× more.
Reading once with study mode > reading three times passively.

DEVELOPER EXAMPLES:
  • Learning a new language feature
  • Reading a system design article
  • Studying for interviews (algorithms, concepts)
  • Reading a book on architecture
```

## 67.6 Mode 4: DEEP (critical analysis — slow, complete)

```
PURPOSE: Full comprehension, find flaws, extract maximum value.
SPEED:  50-150 wpm (very slow, with pauses for thinking)
USE FOR: research papers, architecture decisions, contracts, complex code review

HOW:
  1. Read EVERYTHING (including footnotes, caveats, edge cases)
  2. Question every claim: "Is this true? What's the evidence? What's missing?"
  3. Annotate heavily: notes in margins, questions, disagreements
  4. Re-read difficult sections 2-3 times (this is the one mode where re-reading is OK)
  5. Discuss with others or write about it (teaching = deepest understanding)

DEVELOPER EXAMPLES:
  • Reviewing a critical code change (security, architecture)
  • Reading an RFC or technical specification
  • Reading a research paper for implementation
  • Contract/legal text (terms of service, licence agreements)
```

## 67.7 Choosing the right mode

```
"What's the time investment vs value?"

┌─────────────────────────────────────────────────────────────────┐
│  Content type              │ Default mode │ Time   │ Retention  │
├────────────────────────────┼──────────────┼────────┼────────────┤
│  News/social/headlines     │ SKIM         │ 1 min  │ 10-20%     │
│  Slack threads/emails      │ SKIM → SCAN  │ 1-3 min│ Key points │
│  API documentation         │ SCAN         │ 30 sec │ The answer │
│  Blog posts/tutorials      │ SKIM → STUDY │ 5-15 min│ 60-80%    │
│  Technical books           │ STUDY        │ 30-60 min/ch │ 70% │
│  Research papers           │ DEEP         │ 1-3 hours │ 90%     │
│  Code review (critical)    │ DEEP         │ Varies │ 95%        │
│  Error messages            │ SCAN         │ 10 sec │ The fix    │
│  README / Getting Started  │ SKIM → STUDY │ 5-10 min│ Enough    │
└─────────────────────────────────────────────────────────────────┘

MOST PEOPLE: use Study mode for everything (too slow for easy content)
           or Skim mode for everything (miss important details)
OPTIMAL:    match the mode to the material.
```

---

## PART 3: Speed Techniques That Work

## 67.8 The pointer method (easiest, biggest impact)

```
USE YOUR FINGER (or cursor) to guide your eyes:

  ┌─────────────────────────────────────────────┐
  │  Your finger moves steadily under the line  │
  │              ☝️─────────────────►            │
  │  Eyes follow the finger instead of jumping  │
  │              ☝️─────────────────►            │
  │  Gradually increase speed of finger         │
  │              ☝️─────────────────────►        │
  └─────────────────────────────────────────────┘

WHY IT WORKS:
  • Prevents regression (eyes can't jump back while following finger)
  • Sets a pace (you can gradually increase speed)
  • Improves focus (gives your brain something to follow)
  • Immediate 20-50% speed boost for most people

PRACTICE: Start at comfortable speed. Every 3 minutes, move the pointer
slightly faster. Your comprehension adjusts within seconds.
```

## 67.9 Chunking (read word groups, not individual words)

```
SLOW (word-by-word):
  "The | quick | brown | fox | jumps | over | the | lazy | dog"
  9 eye fixations = slow

FAST (chunking):
  "The quick brown | fox jumps over | the lazy dog"
  3 eye fixations = 3× faster!

PRACTICE:
  Widen your peripheral vision. Instead of focusing on one word,
  try to see 3-4 words in a single fixation.
  
  Start with newspaper columns (narrow = easy to chunk entire lines).
  Gradually apply to wider text.

TIP: Focus on the CENTER of each chunk. Your peripheral vision
picks up the surrounding words without a separate fixation.
```

## 67.10 Speed benchmarks

```
AVERAGE READER:     200-250 wpm
GOOD READER:        300-400 wpm (most people can reach this with practice)
FAST READER:        500-700 wpm (skimming + selective deep reading)
"SPEED READERS":    1000+ wpm (but comprehension drops below 50% — questionable value)

REALISTIC GOAL: 350-500 wpm with 70%+ comprehension
This is 1.5-2× your current speed — achievable in 2-4 weeks of practice.

FOR DEVELOPERS specifically:
  Code: 50-100 wpm (slow by nature — every character matters)
  Documentation: 300-500 wpm (skim structure, slow on details)
  Blog posts: 400-600 wpm (skim, slow on code blocks)
  Slack/email: 600+ wpm (skim, scan for your name/keywords)
```

---

## PART 4: Retention — Remember What You Read

## 67.11 Why you forget (and how to fix it)

```
THE FORGETTING CURVE (Ebbinghaus):
  After reading something:
    20 min later: remember 60%
    1 hour later: remember 45%
    1 day later:  remember 35%
    1 week later: remember 25%
    1 month later: remember 20%

  → Without review, you lose 80% within a month.

HOW TO BEAT IT:
  1. ACTIVE READING (engage with the material, don't passively consume)
  2. IMMEDIATE SUMMARY (write 3 bullet points right after reading)
  3. SPACED REVIEW (revisit at: 1 day, 3 days, 7 days, 30 days)
  4. TEACH/EXPLAIN (explaining forces deeper processing)
  5. CONNECT (link new info to existing knowledge — "this is like X")
  6. APPLY (use it immediately — write code, solve a problem)
```

## 67.12 The "3-2-1" method (after EVERY article/chapter)

```
After finishing any reading session, WITHOUT looking back:

Write:
  3 key ideas (the most important takeaways)
  2 things you want to remember (facts, techniques, quotes)
  1 action item (what you'll DO with this information)

EXAMPLE (after reading about database indexing):
  3 ideas:
    - B-tree indexes give O(log n) lookup
    - Composite index order matters (leftmost prefix rule)
    - EXPLAIN shows if index is used

  2 remember:
    - Index costs: slower writes, more storage
    - Partial indexes save space for filtered queries

  1 action:
    - Run EXPLAIN on our slowest production query tomorrow

TIME: 2 minutes. IMPACT: 3-5× better retention vs just reading and moving on.
```

## 67.13 Progressive summarisation

```
LAYER 1: Read + highlight key passages (10-15% of text)
LAYER 2: Bold the most important highlights (3-5% of text)
LAYER 3: Write a 1-paragraph summary in your own words
LAYER 4: Remix into your own notes/system

Each time you revisit a note, you deepen ONE layer.
Most notes stop at Layer 1-2. Only the most important reach Layer 4.

FOR DEVELOPERS:
  Layer 1: Bookmark article, highlight code snippets
  Layer 2: Copy the 3 most useful code snippets to your notes
  Layer 3: Write a "cheat sheet" version in your own words
  Layer 4: Integrate into your project (actually use it)
```

---

## PART 5: Reading Technical Content

## 67.14 Reading documentation efficiently

```
FRAMEWORK: SQ3R for docs

S — SURVEY (30 seconds):
  Look at: table of contents, API reference structure, sidebar navigation
  Goal: "What does this library DO? How is it organized?"

Q — QUESTION (form questions BEFORE reading):
  "How do I authenticate?"
  "What's the rate limit?"
  "How do I handle errors?"
  → Now you're SCANNING for answers (much faster than reading everything)

R — READ (only what answers your questions)
R — RECITE (close the docs, write the code from memory/understanding)
R — REVIEW (check your code against the docs — did you miss anything?)

THE MISTAKE:
  Reading docs start-to-finish like a novel.
  → Takes 2 hours, remember 10%.

THE FIX:
  Ask specific questions, scan for answers, apply immediately.
  → Takes 15 minutes, remember 80% (of what you actually need).
```

## 67.15 Reading code (other people's)

```
CODE IS THE HARDEST THING TO READ. Strategies:

1. START WITH THE TESTS:
   Tests tell you WHAT the code does (expected inputs → outputs)
   Read test names: "test_user_can_login_with_valid_credentials"
   → Now you know the intent before reading implementation.

2. START AT THE ENTRY POINT:
   Find main(), the API handler, the event listener.
   Follow the call chain: handler → service → repository → database.
   Don't start from a random utility file in the middle.

3. READ TOP-DOWN (structure first, details later):
   Pass 1: class names, method signatures, file structure
   Pass 2: method bodies of the most important functions
   Pass 3: edge cases, error handling, helper functions

4. ASK: "WHAT'S THE DATA FLOW?"
   What goes IN? What comes OUT? What's transformed in between?
   Trace one request through the entire system.

5. USE THE IDE:
   • Go to definition (jump to any function)
   • Find usages (where is this called?)
   • Call hierarchy (what calls what?)
   → Let the IDE navigate; you focus on understanding.
```

## 67.16 Reading books (non-fiction / technical)

```
DON'T READ LINEARLY. Use the "textbook method":

BEFORE READING A CHAPTER:
  1. Read the chapter title + section headings (2 min)
  2. Read the summary/conclusion at the END (2 min)
  3. Now you KNOW what the chapter says → reading fills in details

WHILE READING:
  • Skip sections you already know (no guilt!)
  • Slow down on unfamiliar concepts (don't force constant speed)
  • Mark max 3 ideas per chapter (force yourself to prioritise)
  • After each section: close book → explain it in one sentence

AFTER THE BOOK:
  Write a one-page summary (from memory, not by copying highlights)
  Share it (blog post, team Slack, friend) — teaching = retention

THE PERMISSION:
  • It's OK to abandon a book that isn't useful
  • It's OK to read chapters out of order
  • It's OK to skim 60% and deeply read 40%
  • Most non-fiction books have ONE big idea + 200 pages of examples
    → Once you have the idea, you can move on
```

---

## PART 6: Building a Reading Habit

## 67.17 The developer's reading routine

```
DAILY (15-30 min total):
  Morning (commute/coffee):
    • 1 technical article (Study mode, 10 min)
    • Write 3-2-1 summary (2 min)

  Lunch break:
    • Skim HackerNews/Dev.to/RSS feed (5 min, Skim mode)
    • Save 1-2 "read later" articles (don't read now — you're eating)

  End of work:
    • Review saved articles (Scan: is this still relevant? Most won't be.)
    • Read 1 that IS relevant (Study mode, 10 min)

WEEKLY (1-2 hours):
  • One longer piece: book chapter, research paper, or deep tutorial
  • Review your week's 3-2-1 notes (5 min — spaced repetition)

MONTHLY:
  • Finish one book (or meaningful portion)
  • Write a short review/summary for your blog or notes
```

## 67.18 Reading speed practice (5 min/day → 2× speed in 4 weeks)

```
DAILY EXERCISE (pick one):

Week 1: POINTER PRACTICE
  Read with your finger for 5 minutes. Push slightly faster than comfortable.
  Do this every day. By end of week: 20-30% faster.

Week 2: CHUNKING
  Take a newspaper column. Try to read each line in 2 fixations (not 5-6).
  Widen your gaze. See word groups, not individual words.

Week 3: TIMED READING
  Set a 3-minute timer. Count words in a page. Read it.
  Calculate WPM: (words read / 3 minutes). Track daily.
  Compete against yourself (yesterday's score).

Week 4: MODE SWITCHING
  Practice using the RIGHT mode for each piece of content.
  Skim email in 30 seconds. Study documentation deeply.
  The speed gain comes from NOT over-reading easy content.
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│        READING PRODUCTIVITY CHEAT SHEET             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  MODE SELECTION:                                    │
│    Easy/familiar → SKIM (1000+ wpm)                │
│    Looking for specific info → SCAN                 │
│    Learning something new → STUDY (200-400 wpm)    │
│    Critical/complex → DEEP (50-150 wpm)            │
│                                                     │
│  SPEED TRICKS:                                      │
│    □ Use a pointer (finger/cursor)                  │
│    □ Read word groups, not single words             │
│    □ Don't subvocalise easy content                 │
│    □ Never read docs start-to-finish                │
│                                                     │
│  RETENTION:                                         │
│    □ 3-2-1 after every article (3 ideas, 2 facts,  │
│      1 action)                                      │
│    □ Write from MEMORY, not by re-reading           │
│    □ Apply immediately (write code, build thing)    │
│    □ Review notes at 1 day, 1 week, 1 month        │
│                                                     │
│  TECHNICAL READING:                                 │
│    □ Docs: question first, scan for answers         │
│    □ Code: tests → entry point → data flow          │
│    □ Books: read conclusion first, then details     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Summary

✅ 3 bad habits killing your speed: subvocalisation, regression, single-speed reading
✅ 4 modes: Skim (shape), Scan (find), Study (learn), Deep (analyse) — match to content
✅ Speed techniques: pointer method (+30% immediately), chunking (read word groups), timed practice
✅ Retention: 3-2-1 method, progressive summarisation, teach/explain, apply immediately
✅ Technical reading: docs (question-first), code (tests → entry → data flow), books (conclusion first)
✅ Daily habit: 15-30 min structured reading + 2-min summary = compounds over months
✅ Realistic goal: 350-500 wpm with 70%+ comprehension (achievable in 4 weeks)

## Key takeaways

**Mode selection is 80% of the win.** Most people read everything at the same speed. The moment you start skimming emails (30 seconds) and deeply studying tutorials (15 minutes), your effective information throughput doubles. Not from reading faster — from reading SMARTER.

**The 3-2-1 method is 2 minutes that 10× your retention.** Without it, you forget 80% in a week. With it, the act of writing from memory forces your brain to consolidate. Two minutes after reading is worth more than two hours of passive re-reading later.

**Use a pointer. Yes, really.** It feels silly. It looks childish. It immediately stops regression and increases speed by 20-30%. Every speed reading expert uses one. Try it for 3 days before dismissing it.

**Apply > accumulate.** Reading 10 articles and applying 0 = waste. Reading 1 article and building something with it = growth. The goal isn't to read more — it's to LEARN more per minute spent reading.

---

→ [Back to Chapter 66: MongoDB](./66-MONGODB.md)
