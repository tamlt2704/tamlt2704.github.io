# Chapter 69: Engineering Manager Skills — Lead Developers, Deliver Results

## What you'll learn

- The transition: individual contributor → tech lead → engineering manager
- 1:1 meetings: the most important tool you have (and how most managers waste them)
- Giving feedback: direct, kind, actionable (not sandwich nonsense)
- Delegation: what to keep, what to hand off, how to let go
- Hiring: interviewing, evaluating, building diverse teams
- Delivery: shipping consistently without burning people out
- Growing people: career development, promotions, performance management
- Handling conflict, underperformers, and difficult conversations
- Shielding: protecting your team from chaos without hiding information

---

## PART 1: The Mindset Shift

## 69.1 IC vs Manager (what changes)

```
INDIVIDUAL CONTRIBUTOR:              ENGINEERING MANAGER:
  Your output = YOUR code              Your output = TEAM's output
  Success = you shipped it             Success = THEY shipped it (without you)
  Rewarded for: solving problems       Rewarded for: enabling others to solve problems
  Focus: depth (one thing deeply)      Focus: breadth (many things at surface)
  Feedback: from code reviews          Feedback: from people (delayed, ambiguous)
  Bad day: code doesn't compile        Bad day: someone is unhappy/struggling
  Good day: elegant solution           Good day: someone grew, team shipped
  Control: high (you decide how)       Control: low (they decide how, you set direction)

THE HARDEST PART:
  Your value is no longer measured by YOUR code.
  If you wrote the best code but your team can't ship → you failed.
  If you wrote zero code but your team ships consistently → you succeeded.
```

## 69.2 The 5 jobs of an engineering manager

```
1. PEOPLE: Grow your team members (career, skills, satisfaction)
2. DELIVERY: Ship the right things at a sustainable pace
3. QUALITY: Maintain technical standards and system health
4. PROCESS: Create systems that reduce friction
5. CONTEXT: Connect team's work to business goals (WHY are we building this?)

TIME SPLIT (rough):
  40% People (1:1s, feedback, coaching, hiring)
  30% Delivery (planning, unblocking, coordination)
  15% Process (retros, improving workflows, docs)
  15% Technical (architecture decisions, code review, quality)
```

---

## PART 2: 1:1 Meetings

## 69.3 The most powerful tool you have

```
1:1 = 30 minutes, weekly, with each direct report. NON-NEGOTIABLE.

This is THEIR meeting, not yours.
Purpose: build trust, uncover problems early, develop their career.

NOT FOR: status updates (use standup/Slack for that)
FOR: feelings, frustrations, career, growth, feedback, ideas, concerns
```

## 69.4 The 1:1 structure

```
FIRST 5 MIN — Check in (human, not work):
  "How's your week going?"
  "How are you feeling about things?"
  "Anything on your mind before we start?"
  → Listen. Don't jump to solving. Just listen.

NEXT 15 MIN — Their agenda (THEY bring topics, not you):
  Let them drive. Common topics:
  • "I'm frustrated with X"
  • "I'd like feedback on Y"
  • "I'm interested in doing more of Z"
  • "I'm struggling with W"
  • "I have an idea about..."
  
  YOUR JOB: Ask questions. Coach. Don't just give answers.
  "What have you tried?"
  "What would you do if I weren't here?"
  "What does success look like for you?"

LAST 10 MIN — Your agenda (if needed):
  • Feedback (positive or constructive)
  • Context (company updates, project changes)
  • Career check-in (quarterly: "Are you growing? Happy? Stuck?")

END: "Anything else? Anything I can unblock for you?"
```

## 69.5 1:1 questions that unlock real conversations

```
BUILDING TRUST (early in relationship):
  "What does your ideal manager do? And not do?"
  "How do you prefer to receive feedback?"
  "What's your communication style? (Slack vs meeting, fast vs detailed)"
  "What energises you at work? What drains you?"

UNCOVERING PROBLEMS (they won't say "I'm unhappy" directly):
  "On a scale of 1-10, how happy are you this week? What would make it +1?"
  "What's the most frustrating part of your work right now?"
  "If you could change one thing about how we work, what would it be?"
  "Is there anything I should know but might not?"

GROWTH & CAREER:
  "Where do you want to be in 1-2 years?"
  "What skills do you want to develop?"
  "Are you getting enough of the work you find interesting?"
  "What would make you feel ready for the next level?"

FEEDBACK (giving):
  "I noticed [specific behaviour]. The impact was [specific effect]. 
   Going forward, I'd love to see [specific alternative]."

FEEDBACK (receiving — ask regularly!):
  "What's one thing I could do better as your manager?"
  "Is there anything I'm doing that's not helpful?"
```

---

## PART 3: Giving Feedback

## 69.6 The SBI model (Situation, Behaviour, Impact)

```
❌ VAGUE: "You need to communicate better."
❌ PERSONAL: "You're not a team player."
❌ SANDWICH: "You're great! But... (criticism). But you're great though!"

✅ SBI:
  SITUATION: "In yesterday's standup..."
  BEHAVIOUR: "...you mentioned being blocked for 3 days without telling anyone."
  IMPACT: "That delayed the release by 2 days because we could have unblocked you Monday."
  REQUEST: "In future, could you flag blockers within 24 hours? Slack me or bring it to standup."

EXAMPLES:

POSITIVE:
  "In the code review yesterday (situation), you explained WHY you suggested
  the change, not just what to change (behaviour). That helped the junior
  developer understand the principle, not just the fix (impact). Keep doing that."

CONSTRUCTIVE:
  "In the meeting with the product team (situation), you said their timeline
  was 'impossible' without offering alternatives (behaviour). That shut down
  the conversation and they left frustrated (impact). Next time, could you
  say 'that's tight — here's what we could deliver in that time, or here's
  what the full scope would take'? (request)"
```

## 69.7 Feedback rules

```
1. TIMELY: Give feedback within 48 hours. Not 3 months later in a review.
2. SPECIFIC: Exact situation + exact behaviour (not "generally" or "sometimes")
3. ABOUT BEHAVIOUR, NOT CHARACTER: "You did X" not "You ARE X"
4. PRIVATE for constructive, PUBLIC for praise
5. REGULAR: Don't save it all for review season. Weekly small feedback > quarterly big feedback.
6. BALANCED: If you only give negative feedback → they'll dread talking to you.
              Aim for 5:1 positive to constructive (genuine, not forced).
7. TWO-WAY: After giving feedback, ask: "What do you think? Does this land?"
```

---

## PART 4: Delegation

## 69.8 The delegation decision

```
                    YOU SHOULD DO IT         THEY SHOULD DO IT
                    ─────────────────        ────────────────────
  Only you can:     Yes                      —
  Only they can:    —                        Yes
  Teaching moment:  —                        Yes (with coaching)
  Grows them:       —                        Yes
  You enjoy it:     Maybe (but is it the best use of YOUR time?)
  Urgent + critical: Maybe (if nobody else can NOW)

  THE TRAP: Doing things because "it's faster if I do it myself."
  Yes, it's faster TODAY. But if you always do it:
    → They never learn
    → You're the bottleneck
    → You can't take vacation
    → You burn out

  RULE: If someone on your team COULD do it with guidance,
        delegate it even if it takes them 2× longer the first time.
        Investment now = capacity later.
```

## 69.9 How to delegate effectively

```
LEVEL 1 — TELL: "Do exactly this. Here's how."
  (New team member, first time doing this task, critical and time-sensitive)

LEVEL 2 — TEACH: "Here's the goal. I'll show you how, then you do it."
  (Building skill, has foundation but needs guidance)

LEVEL 3 — TRUST: "Here's the goal. Figure out how. Ask if stuck."
  (Experienced, proven on similar tasks — give autonomy)

LEVEL 4 — EMPOWER: "Here's the problem. You own it entirely — decide and do."
  (Senior, proven, doesn't need check-ins — just inform me of outcome)

THE FORMULA:
  "I'd like you to [what].
   The goal is [why — what success looks like].
   You have [resources, timeline, authority].
   Check in with me [when — weekly? only if blocked?].
   Questions?"
```

---

## PART 5: Delivery — Shipping Consistently

## 69.10 Your job: remove blockers, not assign tasks

```
COMMON MISTAKE:
  Manager assigns tasks → team follows orders → feels micromanaged.

BETTER MODEL:
  Manager sets GOALS + CONTEXT → team decides HOW → manager removes obstacles.

  "The goal is: users can check out with Apple Pay by March 1.
   You figure out the technical approach. I'll handle:
   - Getting the Stripe contract signed
   - Coordinating with the iOS team
   - Shielding you from other requests this sprint"

  Your job is CLEARING THE PATH, not DRIVING THE CAR.
```

## 69.11 Sprint planning that works

```
1. START WITH THE GOAL (not tasks):
   "By end of sprint, a user can complete the full checkout flow in staging."
   Not: "Do ticket A, B, C, D, E, F" (that's a task list, not a goal)

2. LET THE TEAM BREAK IT DOWN:
   They know the code. They estimate. They commit.
   You facilitate, not dictate.

3. PROTECT CAPACITY:
   Interrupt buffer: 20% of sprint (bugs, urgent requests, meetings)
   Don't plan 100% capacity — you WILL get pulled into fires.

4. DAILY STANDUP (5 min, not 30):
   "What's blocking you?" (not "What did you do yesterday?")
   If not blocked → standup is fast. If blocked → solve IMMEDIATELY after standup.

5. END WITH DEMO:
   Show working software to stakeholders.
   Visible progress → trust → less micromanagement → more autonomy.
```

## 69.12 When the team is behind

```
SIGNALS:
  • Sprint goals missed 2+ sprints in a row
  • Team members working evenings/weekends
  • Quality dropping (more bugs, less testing)
  • Morale falling (quiet in retros, complaints in 1:1s)

ACTIONS (in order):
  1. REDUCE SCOPE (first response — always):
     "What can we cut or delay?"
     Ship 80% on time > 100% late + burned out.

  2. REMOVE DISTRACTIONS:
     Shield from new requests. Cancel unnecessary meetings. 
     Say "no" to stakeholders on their behalf.

  3. ADD CAPACITY (last resort — slow and risky):
     New hire won't help for 2-3 months (onboarding).
     Borrowed engineer from another team = fastest but disruptive.

  NEVER: Ask people to "just work harder." That's not management — that's denial.
```

---

## PART 6: Growing People

## 69.13 Career development

```
QUARTERLY CAREER CONVERSATION (separate from 1:1 — dedicated time):

  "Where do you want to be in 12-18 months?"
  "What does the next level look like for you?"
  "What skills gap exists between where you are and where you want to be?"
  "What projects/experiences would help you grow in that direction?"
  "How can I help? (Stretch assignments? Mentorship? Conferences? Training budget?)"

THEN: Create a plan together. Write it down. Check in monthly.

GROWTH DOESN'T MEAN PROMOTION:
  Horizontal: new tech stack, different domain, cross-team project
  Depth: become THE expert in one area
  Breadth: learn architecture, design, leadership
  Impact: bigger scope, more responsibility
  
  Some people want to stay senior IC forever. THAT'S FINE. 
  Don't force the management track.
```

## 69.14 Performance management (when someone is struggling)

```
STEP 1: EARLY CONVERSATION (informal, in 1:1):
  "I've noticed [specific behaviour/output change] in the last 2 weeks.
   Is everything OK? Is there anything I can help with?"
  → Often: personal issue, burnout, unclear expectations. FIX IT HERE.

STEP 2: CLEAR EXPECTATIONS (if it continues):
  "I need to be direct with you. In the last month, [specific examples].
   The expectation for your level is [specific standard].
   Here's what I need to see in the next 2-4 weeks: [measurable goals].
   How can I support you in getting there?"
  → Write it down. Both agree. Check in weekly.

STEP 3: FORMAL PIP / EXIT (last resort):
  If improvement doesn't happen after genuine support and clear expectations:
  → Work with HR on formal performance improvement plan (PIP)
  → Be honest: "If we don't see improvement by [date], we'll need to discuss
     whether this role is the right fit."
  → This is hard. But keeping an underperformer hurts the whole team.

THE MISTAKE MANAGERS MAKE:
  Skip step 1-2, then suddenly fire someone.
  → Person is shocked ("no one told me!"), team loses trust.
  
THE RIGHT APPROACH:
  Feedback early + clear expectations + support + time to improve = fair.
  If they still can't meet the bar → everyone (including them) knows it's not working.
```

---

## PART 7: Difficult Situations

## 69.15 Two team members in conflict

```
1. LISTEN TO BOTH SEPARATELY (1:1, not together):
   "Tell me what's happening from your perspective."
   Don't take sides yet. Just understand both views.

2. IDENTIFY THE REAL ISSUE:
   Usually it's not what they say it is.
   "They write bad code" often means "They don't follow our agreed practices."
   "They're not a team player" often means "Communication style mismatch."

3. MEDIATE (bring them together only after you understand both sides):
   "I've spoken to both of you. I think the core issue is [X].
    Let's agree on [specific behaviour change] going forward.
    [Person A], can you commit to [X]? [Person B], can you commit to [Y]?"

4. FOLLOW UP (don't assume it's fixed):
   Check in 1-2 weeks later: "How's it going with [Person]?"
```

## 69.16 Shielding your team (without hiding information)

```
SHIELD FROM:
  • Context-free urgent requests ("Drop everything and do X")
    → You: "I'll evaluate priority and get back to you by EOD."
  • Unnecessary meetings ("Can your whole team attend...?")
    → You: "I'll attend and share relevant info with the team."
  • Panic from leadership ("Everything is on fire!")
    → You: filter signal from noise. Share facts, not anxiety.

DON'T SHIELD FROM:
  • Business context (why are we building this? How does the company make money?)
  • Bad news (layoffs, pivot, failed quarter — they'll hear anyway; hear it from you)
  • Technical reality checks (deadline is impossible → tell stakeholders, WITH the team)

THE BALANCE:
  Filter the NOISE, transmit the SIGNAL.
  Your team should know: goals, priorities, why things changed.
  Your team should NOT know: every Slack argument between VPs at 10pm.
```

## 69.17 Having hard conversations

```
TEMPLATE (any difficult topic):

"I need to talk to you about something that might be uncomfortable,
but I'm bringing it up because I care about your growth / our team / this project.

[Specific observation — facts, not interpretation]
[Impact on team/project/person]
[What I'd like to see change — specific, measurable]
[Offer of support]
[Ask for their perspective]"

EXAMPLE:
"I need to bring up something I've noticed. In the last two sprints,
your PRs have had 3-4 bugs caught in review that are basic issues —
null checks, missing edge cases. That's unusual for you.

The impact: it's slowing down reviews and the team is starting to hesitate
before merging your code.

I'd like to see the bug count back to where it was (maybe 0-1 per PR).
Is something going on? Are you stretched too thin? Let's figure this out together."
```

---

## Quick Reference: Manager's Weekly Rhythm

```
MONDAY:
  □ Review team's sprint goals (on track? blocked?)
  □ Check 1:1 prep (any pending feedback to give?)
  □ Sync with PM: priorities still correct?

DAILY:
  □ Standup (listen for blockers → unblock same day)
  □ Be available (Slack response within hours)
  □ One spontaneous check-in ("How's it going?")

1:1s (2-4 per week):
  □ Listen more than talk
  □ Give one piece of feedback per week (positive or constructive)
  □ Ask: "What can I do better for you?"

FRIDAY:
  □ Celebrate wins (even small ones — public recognition)
  □ Review: did we ship what we planned?
  □ Prep next week: priorities, blockers to pre-solve, people to support
```

---

## Summary

✅ Mindset shift: your output = team's output (not your code)
✅ 1:1s: weekly, THEIR agenda, ask questions > give answers, build trust
✅ Feedback: SBI model (Situation + Behaviour + Impact), timely, specific, behaviour-based
✅ Delegation: 4 levels (tell → teach → trust → empower), delegate even if slower initially
✅ Delivery: set goals not tasks, remove blockers, protect capacity, reduce scope before crunch
✅ Growing people: quarterly career conversations, stretch assignments, not everyone wants management
✅ Performance: early feedback → clear expectations → support → PIP only as last resort
✅ Conflict: listen separately → identify real issue → mediate → follow up
✅ Shielding: filter noise (panic, meetings), transmit signal (context, priorities, changes)
✅ Hard conversations: facts + impact + request + support + ask their perspective

## Key takeaways

**The best managers make themselves unnecessary.** If your team can't function without you, you've failed. If they ship perfectly while you're on vacation for 2 weeks, you've succeeded. Your job is to build a team that doesn't need you for day-to-day decisions.

**Listen more, talk less.** In 1:1s, aim for them talking 70%+. Ask questions, then shut up. The silence after a question is where the real answers come from. Don't fill it.

**Feedback is a gift, not a punishment.** People can't fix what they don't know is broken. Direct, specific, timely feedback — even when uncomfortable — is the most caring thing you can do for someone's career.

**Reduce scope before adding crunch.** The answer to "we're behind" is NEVER "work weekends." It's: cut scope, extend timeline, or get help. Sustainable pace > heroic sprints that burn people out.

---

→ [Back to Chapter 68: English for Developers](./68-ENGLISH-FOR-DEVELOPERS.md)
