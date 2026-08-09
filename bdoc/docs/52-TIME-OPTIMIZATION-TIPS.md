# Chapter 52: Time Optimization Tips & Tricks — The Developer's Tactical Playbook

## What you'll learn

- 50+ concrete, immediately actionable tips
- IDE shortcuts that save hours per week
- Automation: scripts, aliases, templates that eliminate repetitive work
- Communication hacks: fewer meetings, faster decisions, less back-and-forth
- Workflow patterns: how top developers structure their actual workday
- Mental tricks: reduce decision fatigue, enter flow faster, stay focused longer

---

## 🔥 HIGH-IMPACT (Each saves 30+ minutes/week)

### 1. Learn your IDE's top 20 shortcuts

```
Investment: 1 hour to memorize
Return: 30-60 min saved EVERY DAY

The shortcuts that matter most (VS Code / IntelliJ):
├── Multi-cursor (edit 10 lines at once, not one by one)
├── Go to file by name (Cmd+P / Ctrl+Shift+N)
├── Go to symbol/function (Cmd+Shift+O / Ctrl+Alt+Shift+N)
├── Rename all occurrences (F2 / Shift+F6)
├── Find and replace in project (Cmd+Shift+F / Ctrl+Shift+R)
├── Move line up/down (Alt+↑/↓)
├── Duplicate line (Shift+Alt+↓)
├── Toggle comment (Cmd+/)
├── Quick fix / auto-import (Cmd+. / Alt+Enter)
└── Open terminal in project (Ctrl+`)

RULE: If you do something with a mouse more than 3× per day,
      find the keyboard shortcut. Print a cheat sheet. Force yourself
      to use it for 3 days. Then it's automatic forever.
```

### 2. Git aliases (type less, commit faster)

```bash
# ~/.gitconfig or run each with: git config --global alias.<name> "<command>"

[alias]
    s = status -sb
    co = checkout
    cb = checkout -b
    cm = commit -m
    ca = commit --amend --no-edit
    p = push
    pl = pull --rebase
    lg = log --oneline --graph --decorate -20
    d = diff --stat
    unstage = reset HEAD --
    undo = reset --soft HEAD~1
    wip = !git add -A && git commit -m 'WIP'
    nuke = !git clean -fd && git checkout .

# Usage:
git s          # instead of: git status
git cb feature # instead of: git checkout -b feature
git cm "fix"   # instead of: git commit -m "fix"
git lg         # pretty log
git wip        # save everything quickly (clean up later)
git undo       # undo last commit (keep changes)
```

### 3. Shell aliases for common commands

```bash
# ~/.zshrc or ~/.bashrc
alias c="code ."
alias gd="cd ~/dev"
alias dc="docker compose"
alias dcu="docker compose up -d"
alias dcd="docker compose down"
alias dcl="docker compose logs -f"
alias nr="npm run"
alias nrd="npm run dev"
alias nrb="npm run build"
alias nrt="npm run test"
alias gw="./gradlew"
alias gwb="./gradlew build"
alias gwr="./gradlew bootRun"
alias k="kubectl"
alias kp="kubectl get pods"
alias kl="kubectl logs -f"
alias py="python3"
alias tf="terraform"
alias ..="cd .."
alias ...="cd ../.."
alias ll="ls -la"
alias ports="lsof -i -P | grep LISTEN"
alias myip="curl -s ifconfig.me"
```

**Saved time:** 5-10 seconds per command × 50+ commands/day = 5-10 min/day = 30-60 min/week.

### 4. Snippet libraries (don't retype boilerplate)

```
Configure snippets in your IDE for patterns you write daily:

Trigger     → Expands to
───────────────────────────────────────────────────
"rfc"       → React functional component with types
"useState"  → const [x, setX] = useState<Type>(initial)
"uf"        → useEffect(() => { ... return () => {} }, [])
"tryCatch"  → try { } catch (e) { logger.error(e) }
"test"      → describe('', () => { it('should', () => { ... }) })
"api"       → Full REST controller method with annotations
"entity"    → JPA entity with ID, timestamps, constructors
"dto"       → Record class with validation annotations
"docker"    → Dockerfile multi-stage build template

Investment: 30 min setting up 20 snippets
Return: 2-5 min saved per snippet use × multiple times daily
```

### 5. Template repositories (don't start from scratch)

```
Create starter repos you clone for new projects:

• next-starter: Next.js + Tailwind + shadcn + auth + MDX + deployed
• spring-starter: Spring Boot + JPA + security + Docker + CI/CD + tests
• expo-starter: React Native + navigation + theme + common components

Instead of spending 2 hours on setup every new project:
  git clone my-starter new-project → ready in 5 minutes

ALSO: Save common config files:
• .github/workflows/ci.yml (pre-written CI)
• Dockerfile (production multi-stage)
• docker-compose.yml (local dev stack)
• .eslintrc / prettier config
• tsconfig.json with strict settings
```

---

## ⚡ COMMUNICATION HACKS (Fewer Messages, Faster Decisions)

### 6. Write complete messages (save 3 round-trips)

```
❌ Costs 4 messages + 30 min waiting:
  You: "Hey, are you free?"
  Them: "Yeah what's up?" (15 min later)
  You: "I have a question about the auth flow"
  Them: "Sure, go ahead" (10 min later)
  You: *actual question*

✅ Costs 1 message + 1 reply:
  You: "Question about auth flow: should the refresh token cookie be SameSite=Strict
  or Lax? Strict blocks it on cross-site navigations from email links (our users
  click links from email). I'm leaning Lax. Thoughts? No rush — EOD is fine."
```

### 7. The "propose and confirm" pattern

```
❌ Open-ended (requires thinking from the recipient):
  "When should we deploy?"

✅ Propose + confirm (recipient just says yes/no):
  "I'll deploy Thursday 2pm. Any objections? If I don't hear by Wed EOD, I'll proceed."

❌ "What approach should we take?"
✅ "I propose approach A because [reason]. B is the alternative but [tradeoff].
    I'll go with A unless you have concerns. Let me know by Tuesday."

WHY: Reduces their cognitive load. They don't have to think from scratch —
just evaluate your proposal. Decisions happen 3× faster.
```

### 8. Async video messages (replace 30-min meetings)

```
TOOL: Loom, Screen.studio, or just QuickTime screen record

WHEN: You need to explain something visual (UI bug, architecture, demo)
      but a meeting is overkill (only needs 3-5 min of explanation).

RECORD: 3-5 min video showing your screen + talking through the issue.
SEND: In Slack/email. They watch on their time at 1.5× speed.

Result: You saved 30 min of scheduling + meeting + small talk.
They saved 30 min too. And there's a recording if anyone else needs it later.
```

### 9. Decision documents (stop re-discussing)

```
When a decision keeps getting revisited:

Write a one-page decision doc:
  ## Decision: Use PostgreSQL (not MongoDB)
  
  ### Context
  We need a database for the order service. Options considered: PostgreSQL, MongoDB.
  
  ### Decision
  PostgreSQL.
  
  ### Reasoning
  - We need ACID transactions (orders/payments)
  - Team has PostgreSQL experience
  - JOINs needed for reporting
  
  ### Tradeoffs
  - MongoDB would be simpler for the product catalog (denormalized)
  - We'll use PostgreSQL's JSONB for flexible product attributes
  
  ### Status: DECIDED (2024-08-01, agreed by: Alice, Bob, Carol)

Link it whenever someone asks "why did we choose X?"
Stops the same discussion from happening 5 times.
```

### 10. Meetings: always have a visible timer

```
TRICK: Share your screen with a countdown timer during meetings.

WHY: Without a timer, 30-min meetings become 45-min meetings.
With a visible countdown, people self-organise to finish on time.

ALSO:
• Start meetings with: "We have 25 min. Goal: decide X. Let's go."
• At 5 min left: "We have 5 min. What's the decision? Who owns next step?"
• End ON TIME even if not "finished" — schedule a follow-up if needed.
  This trains people to come prepared.
```

---

## 🧠 FOCUS & MENTAL TRICKS

### 11. The "parking lot" notebook

```
While in deep work, thoughts will pop up:
  "Oh I need to reply to that Slack message"
  "I should update that ticket"
  "What about that edge case in the other feature?"

DON'T context-switch. Write it in a notebook/sticky note. Continue working.
Review the parking lot during your next shallow work block.

This captures the thought (so you don't worry about forgetting)
without breaking flow (so you don't lose 20 minutes).
```

### 12. "Yesterday's incomplete" → today's first task

```
End of day: you're mid-way through a function. STOP mid-sentence.
Don't finish the easy bit. Leave it half-done.

Next morning: your brain IMMEDIATELY knows where to continue.
No "where was I?" No cold-start. You drop into flow in 2 minutes
because the half-finished code is staring at you.

Hemingway used this: always stop writing mid-sentence.
Next day he knew exactly where to pick up.
```

### 13. Reduce decision fatigue

```
DECISIONS COST ENERGY. Every trivial decision drains the same mental resource
as important decisions. Eliminate trivial decisions:

• Same breakfast every day (or rotate 3 options — no thinking)
• Same coffee order
• Coding playlist: ONE playlist you always use (don't browse music)
• Clothes: limited wardrobe, minimal choices
• Lunch: meal prep (decided on Sunday, not daily)
• Text editor theme: pick one, stop changing it
• Work start time: same every day (no "should I start early or late?")

ALSO FOR CODE DECISIONS:
• Team style guide (no debates about tabs vs spaces — it's decided)
• Auto-formatter (Prettier/Spotless — no manual formatting decisions)
• Lint rules committed (no "should I use const or let here?")
• ADRs (Architecture Decision Records — decide once, reference forever)
```

### 14. The "two-minute startup" ritual

```
Every morning, BEFORE opening Slack/email/browser:

1. Open your todo list or yesterday's parking lot (30 sec)
2. Write today's 3 MITs (60 sec)
3. Open your editor to MIT #1's file (30 sec)
4. Start working (immediately — don't check anything else first)

TOTAL: 2 minutes between sitting down and productive work.

WITHOUT THIS RITUAL: sit down → open browser → check email → check Slack →
read news → someone asks you something → 45 min gone before you write a single line.
```

### 15. Timeboxing decisions

```
DEVELOPERS OVER-RESEARCH. We love exploring all options.

"Should I use Redis or Memcached?" → 3 hours reading comparisons
"Which testing library?" → 2 hours comparing Jest vs Vitest vs Mocha
"How should I structure this folder?" → 1 hour analysis paralysis

TIMEBOX IT:
"I'll spend 15 minutes evaluating. Then I pick the best option with available info.
If it's wrong, I can change later. The cost of 15 more minutes of research
is rarely worth more than the cost of shipping 15 minutes later."

MOST DECISIONS ARE REVERSIBLE. Make them fast. Move on.
Only agonise over truly irreversible decisions (database choice at scale,
public API contracts, team hires).
```

---

## 🛠️ WORKFLOW AUTOMATION

### 16. Pre-commit hooks (catch problems before PR)

```bash
# .husky/pre-commit (or lefthook)
npm run lint
npm run typecheck
npm run test -- --changed

# SAVES: back-and-forth on PRs ("fix this lint error", "add types here")
# Everything caught BEFORE you even push.
```

### 17. PR templates (consistent, no missing info)

```markdown
<!-- .github/pull_request_template.md -->
## What
Brief description of the change.

## Why
Link to ticket or context for why this matters.

## How to test
1. Steps to verify this works

## Checklist
- [ ] Tests added/updated
- [ ] No console.log / debug code
- [ ] Documentation updated (if API changed)
```

### 18. Scaffold scripts (generate boilerplate)

```bash
#!/bin/bash
# scripts/new-feature.sh — scaffolds a new feature module
NAME=$1

mkdir -p "src/features/$NAME"
cat > "src/features/$NAME/index.ts" << EOF
export * from './$NAME.service';
export * from './$NAME.controller';
export * from './$NAME.types';
EOF

cat > "src/features/$NAME/$NAME.service.ts" << EOF
export class ${NAME^}Service {
  // TODO: implement
}
EOF

echo "✅ Feature '$NAME' scaffolded at src/features/$NAME/"

# Usage: ./scripts/new-feature.sh payment
# Creates: src/features/payment/index.ts, payment.service.ts, etc.
```

### 19. Keyboard shortcuts for everything outside code

```
BROWSER:
  Ctrl+L  → focus URL bar (don't reach for mouse)
  Ctrl+T  → new tab
  Ctrl+W  → close tab
  Ctrl+Tab → next tab
  Ctrl+1-9 → jump to tab by number

OS (Mac):
  Cmd+Space → Spotlight (launch anything by typing)
  Cmd+Tab   → switch app
  Ctrl+←/→  → switch desktop
  Cmd+`     → switch window within same app

TERMINAL:
  Ctrl+R    → reverse search history (find that command from last week)
  Ctrl+A/E  → jump to start/end of line
  Ctrl+U    → clear line
  !!        → repeat last command
  !$        → last argument of previous command
```

### 20. Notifications: nuclear option

```
DURING DEEP WORK (2-3 hour blocks):

• Phone: Do Not Disturb (allow calls from favourites only)
• Mac: Focus mode (silence all notifications)
• Slack: quit the app entirely (not just close — QUIT)
• Email: close the tab
• Browser: use a "focus" extension that blocks distracting sites

BETWEEN BLOCKS (30 min catch-up):
• Open Slack, respond to everything in batch
• Check email, respond or schedule
• Check PRs, review in batch

THE FEAR: "What if something is urgent?"
THE REALITY: Truly urgent things → someone will call you or walk to your desk.
99% of "urgent" Slack messages can wait 2 hours.
```

---

## 📅 WEEKLY OPTIMIZATION PATTERNS

### 21. Monday: plan the week (30 min)
### 22. Tuesday/Thursday: deepest work days (protect entirely)
### 23. Wednesday: meeting day (batch all meetings here)
### 24. Friday: tie up loose ends, review, prep next week

```
THE IDEAL DEVELOPER WEEK:

Mon:  Plan week → MIT → deep work AM → meetings PM
Tue:  FULL DAY deep work (no meetings allowed)
Wed:  Meeting day (1:1s, retros, planning — all here)
Thu:  FULL DAY deep work (no meetings allowed)
Fri:  Ship → PR reviews → documentation → weekly review → early finish

RESULT: 2 full uninterrupted days + 2 half-days of deep work = 24+ hours of focus.
vs scattered meetings all week = maybe 8 hours of usable focus.
```

### 25. The Friday review (15 min)

```
1. What shipped this week? (Celebrate — small wins compound)
2. What didn't ship? Why? (Learn — don't blame yourself)
3. What wasted my time? (Identify — then eliminate or automate)
4. What should I say NO to next week? (Protect — set boundaries)
5. Top 3 priorities for next week? (Focus — enter Monday with clarity)
```

---

## Summary

✅ IDE shortcuts + snippets: saves 30-60 min/day (learn the top 20 — not all 500)
✅ Git/shell aliases: type less, commit faster (compound savings)
✅ Template repos + scaffolding: don't start from scratch (ever)
✅ Complete messages + "propose and confirm": eliminate round-trips
✅ Async video > meetings (Loom 3 min vs meeting 30 min)
✅ Decision docs: decide once, reference forever
✅ Parking lot notebook: capture thoughts without breaking flow
✅ Stop mid-task for easy morning restart (Hemingway technique)
✅ Timebox decisions: 15 min max for reversible choices
✅ Automation: pre-commit hooks, PR templates, scaffold scripts
✅ Nuclear notifications during deep work, batch-respond between blocks
✅ Ideal week structure: 2 no-meeting days, 1 meeting day, plan Monday, review Friday

## Key takeaway

**Optimization is about eliminating friction, not working harder.** Every tip here removes a few seconds or minutes of waste. Individually, they're trivial. Combined, they give you 1-2 EXTRA HOURS of productive time every day — without working longer. That's the equivalent of an extra workday every week. Compounded over a year, it's the difference between "always busy" and "consistently shipping."

---

→ [Back to Chapter 51: Time Management](./51-TIME-MANAGEMENT.md)
