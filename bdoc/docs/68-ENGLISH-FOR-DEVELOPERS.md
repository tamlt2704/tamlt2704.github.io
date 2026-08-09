# Chapter 68: English for Developer Communication — Write, Speak, Influence

## What you'll learn

- Writing emails, Slack messages, and PRs that get fast responses
- Speaking in meetings, standups, and presentations with clarity
- Common phrases for: code reviews, disagreements, asking questions, giving updates
- Grammar patterns that make technical writing clear (not "proper English" — effective English)
- Vocabulary: the 100 most useful words/phrases in tech workplaces
- Confidence: non-native speaker strategies (you don't need perfect English — you need CLEAR English)

---

## The Developer English Principle

```
ACADEMIC ENGLISH:   "It would be advisable to consider the implementation
                     of a caching mechanism in order to ameliorate the
                     performance degradation that has been observed."

DEVELOPER ENGLISH:  "We should add caching. The API is slow."

DEVELOPER ENGLISH WINS because it's:
  • Clear (no ambiguity)
  • Concise (respects reader's time)
  • Actionable (people know what to do)

You don't need big vocabulary. You need PRECISE, SHORT, DIRECT communication.
```

---

## PART 1: Slack & Chat Messages

## 68.1 Templates for common situations

### Asking for help

```
❌ Vague:
"Hi, I have a problem. Can you help?"

✅ Complete (gets faster response):
"Hi! I'm getting a NullPointerException in OrderService.java:142
when calling createOrder() with a null userId.

I've tried:
- Adding a null check (still fails at line 156)
- Looking at the test coverage (no test for null input)

Could you point me to where userId validation should happen?
No rush — when you have 5 min. Thanks!"
```

**Formula:** `Context + What I tried + Specific question + Timeline`

### Giving a status update

```
✅ Daily standup (text format):
"Yesterday: Finished auth migration PR (#234) — ready for review.
Today: Starting the notification service refactor.
Blocker: None."

✅ Progress update (project):
"Quick update on the payment integration:
✓ Stripe SDK integrated
✓ Checkout flow working in dev
→ Next: error handling + webhook setup (ETA: Thursday)
⚠️ Risk: Stripe sandbox is slow today — might delay testing by half a day."
```

### Disagreeing politely

```
❌ Blunt (sounds aggressive in text):
"That's wrong. We shouldn't do it that way."

✅ Professional (same message, better received):
"I have a concern about this approach. If we use polling instead of 
WebSocket, we'll hit rate limits at 1000+ users. 

Have we considered WebSocket or SSE? Happy to write up a quick comparison 
if that would help the decision."
```

### Asking for a deadline

```
✅ Clear:
"Could you let me know when you'll have the API spec ready?
I need it to start the frontend work. If it's not ready by Wednesday,
I'll start with mock data and adjust later. Either way works for me."
```

### Saying no / pushing back

```
✅ With alternative:
"I can't take this on this sprint — I'm at capacity with the auth work.
Options:
1. Move it to next sprint (my preference — less context switching)
2. I hand off the auth PR to someone else and pick this up
3. We descope the auth work (drop the OAuth flow, keep basic login)

Which works best for the team?"
```

---

## PART 2: Emails

## 68.2 The 5-line email structure

```
Subject: [Clear topic] — [action needed]
Example: "API spec review — feedback needed by Wednesday"

---

Line 1: What this is about (one sentence)
Line 2: What I need from you (specific action)
Line 3: Key context (only what's necessary)
Line 4: Timeline/deadline
Line 5: Close (thanks + availability for questions)
```

### Examples

```
Subject: Database migration — approval needed before Thursday deploy

Hi team,

We're migrating the orders table to add the new status column.
I need your approval on the migration script before I deploy Thursday 2pm.

The script is here: [link]. It adds one column with a default value 
(no downtime, reversible). Tested in staging — no issues.

Please review by Wednesday EOD. Let me know if you have concerns.

Thanks,
Alice
```

```
Subject: Quick question — Redis cache TTL for user sessions

Hi Bob,

What TTL should I set for the user session cache in Redis?
Current options: 15 min (secure) vs 1 hour (fewer re-logins).

I'm leaning toward 30 min as a middle ground. Any preference 
based on the security requirements?

Thanks!
```

## 68.3 Phrases for emails

| Situation | Phrase |
|-----------|--------|
| Starting | "I'm writing to..." / "Quick question about..." / "Following up on..." |
| Action needed | "Could you..." / "I need your input on..." / "Please review by..." |
| Informing | "Just to let you know..." / "Heads up:" / "FYI:" |
| Apologising | "Sorry for the delay." / "Apologies — I missed this." |
| Uncertain | "I'm not sure about X — could you clarify?" |
| Urgent | "This is blocking deployment. Can you look today?" |
| Not urgent | "No rush — when you get a chance." / "Low priority." |
| Closing | "Let me know if you have questions." / "Happy to discuss." |
| Following up | "Gentle reminder about..." / "Circling back on this..." |

---

## PART 3: Code Reviews

## 68.4 Giving code review feedback

```
CATEGORIES (prefix your comment so author knows severity):

[Must fix]:    "This will cause a bug: the null check is missing here."
[Suggestion]:  "Consider using Optional here — it makes the intent clearer."
[Nit]:         "Nit: typo in variable name (recieve → receive)"
[Question]:    "Why did you choose HashMap over TreeMap here? Curious about the reasoning."
[Praise]:      "Nice refactoring — this is much cleaner than before."
```

### Useful phrases

| Intent | Phrase |
|--------|--------|
| Bug found | "This will break when X happens because..." |
| Better approach | "Have you considered...? It would handle edge case X." |
| Ask reasoning | "What's the reasoning behind...? I might be missing context." |
| Suggest improvement | "This works, but we could simplify by..." |
| Request test | "Could we add a test for the null case here?" |
| Approve with note | "Looks good! One minor suggestion (non-blocking): ..." |
| Performance concern | "This is O(n²) — would be a problem at scale. Consider..." |
| Readability | "I found this section hard to follow. Could we extract a method?" |
| Praise | "Clean solution. I learned something from this approach." |

## 68.5 Responding to code review feedback

| Situation | Response |
|-----------|----------|
| Agree | "Good catch! Fixed." / "Done — thanks for spotting this." |
| Partially agree | "Makes sense. I've done X but kept Y because [reason]." |
| Disagree | "I see your point, but I chose this because [reason]. Happy to discuss." |
| Need clarification | "Could you elaborate? I'm not sure what you mean by..." |
| Will fix later | "Added a TODO — will address in the next PR to keep this one focused." |
| Appreciate praise | "Thanks! I spent extra time on that refactor." |

---

## PART 4: Meetings & Speaking

## 68.6 Standup (30 seconds — be concise!)

```
FORMULA: "Yesterday I [completed]. Today I'm [working on]. [Blocker/no blocker]."

EXAMPLE:
"Yesterday I finished the payment integration and opened PR #234.
Today I'm writing integration tests for the checkout flow.
No blockers."

IF BLOCKED:
"I'm blocked on the API spec — I need the response format for the
order endpoint. Bob, could we sync for 5 minutes after standup?"
```

## 68.7 Explaining a technical decision in a meeting

```
STRUCTURE: Problem → Options → Recommendation → Tradeoff

"The problem is [X].
I looked at two options: [A] and [B].
I recommend [A] because [reason 1] and [reason 2].
The tradeoff is [downside of A], but I think that's acceptable because [mitigation]."

EXAMPLE:
"The problem is our API response time is over 2 seconds on the dashboard page.
I looked at two options: adding Redis caching or optimising the database queries.
I recommend Redis caching because it reduces response time to 50ms and requires
less refactoring. The tradeoff is added infrastructure complexity, but we already
run Redis for sessions, so it's minimal extra work."
```

## 68.8 Asking a question in a meeting (without sounding lost)

```
✅ Good ways to ask:
"Can you go back to the part about X? I want to make sure I understand correctly."
"Just to confirm — are you saying [restate in your own words]?"
"How does this relate to [other thing]? I'm not seeing the connection."
"What would happen if [edge case]?"
"Could you give a concrete example?"

✅ If you don't understand the English (non-native speaker):
"Sorry, could you repeat that last part? I missed it."
"Could you say that in a different way? I want to make sure I got it right."
(Never apologise for your English — just ask for clarity. Everyone does this.)
```

## 68.9 Presenting / demoing

```
OPENING:
"I'll walk you through [what] — it should take about [time].
I'll show [3 things]. Feel free to ask questions as we go."

TRANSITIONS:
"First..." → "Next..." → "Finally..."
"Moving on to..." / "The next thing I want to show is..."
"So that's [what we just covered]. Now let's look at..."

WHEN SOMETHING GOES WRONG (demo gods):
"That's not supposed to happen — let me [fix/skip] and come back to it."
"Looks like the environment is being finicky. Let me show you in the slides instead."
(Stay calm. Everyone has seen demos break. It's not a big deal.)

CLOSING:
"To summarise: we [did X], which means [impact for the team/user]."
"Any questions? ...No? Then I'll send the link to the PR / docs / recording."
```

---

## PART 5: Common Technical Vocabulary

## 68.10 Action words (use these in tickets, PRs, messages)

| Word | Use for | Example |
|------|---------|---------|
| **Implement** | Building something new | "Implement user authentication" |
| **Refactor** | Restructuring without changing behaviour | "Refactor order service into smaller functions" |
| **Fix** | Correcting a bug | "Fix null pointer in payment flow" |
| **Optimise** | Making faster/better | "Optimise database query (reduce from 2s to 50ms)" |
| **Migrate** | Moving from old to new | "Migrate from MySQL to PostgreSQL" |
| **Deprecate** | Mark as outdated (will remove later) | "Deprecate v1 API endpoints" |
| **Integrate** | Connecting with another system | "Integrate Stripe payment gateway" |
| **Deploy** | Putting into production | "Deploy hotfix to production" |
| **Revert** | Undo a change | "Revert last commit (caused 500 errors)" |
| **Investigate** | Looking into a problem | "Investigate high memory usage in worker service" |
| **Scope** | Define what's included | "Scope: only login flow, not registration" |
| **Descope** | Remove from plan | "Descope OAuth for this sprint" |

## 68.11 Status words

| Word | Meaning |
|------|---------|
| **Blocked** | Can't proceed (waiting on someone/something) |
| **In progress** | Actively working on it |
| **Ready for review** | Done, needs someone to check it |
| **Merged** | Code is in the main branch |
| **Deployed** | Live in production |
| **On hold** | Paused (not abandoned — will resume) |
| **At risk** | Might not meet deadline |
| **Shipped** | Complete and released to users |

## 68.12 Discussion phrases

| Situation | Professional phrases |
|-----------|---------------------|
| Agree | "That makes sense." / "I'm on board with that." / "+1" |
| Partially agree | "I agree with X, but I'm not sure about Y." |
| Disagree | "I see it differently." / "My concern is..." / "I have a different take." |
| Unsure | "I'm not sure — let me look into it." / "I'd need to check." |
| Need time | "Can I get back to you on that?" / "Let me think about it." |
| Offer help | "I can take a look at that." / "Happy to pair on it." |
| Delegate | "X would be the best person for this." / "Could you handle Y?" |
| Escalate | "I think we need to involve [person/team] on this." |
| Timebox | "Let's timebox this to 15 minutes." / "Let's decide by Friday." |
| Move on | "Let's take this offline." / "Let's park this and come back to it." |
| Summarise | "So the decision is..." / "To recap..." / "Action items: ..." |

---

## PART 6: Non-Native Speaker Tips

## 68.13 You don't need perfect English

```
THINGS THAT MATTER:
  ✅ Clarity (people understand what you mean)
  ✅ Completeness (you include necessary context)
  ✅ Conciseness (you don't ramble)
  ✅ Confidence (you speak even if imperfect)

THINGS THAT DON'T MATTER:
  ❌ Perfect grammar (native speakers make mistakes too)
  ❌ No accent (accents are normal — over 1 billion non-native English speakers)
  ❌ Knowing every idiom ("let's circle back" — just say "let's discuss later")
  ❌ Speaking fast (speaking clearly at moderate speed > speaking fast unclearly)
```

## 68.14 Strategies

```
1. WRITE MORE THAN YOU SPEAK (initially):
   Writing gives you time to check and edit.
   Good written communication builds your reputation even if you're quiet in meetings.

2. PRE-PREPARE for meetings:
   If you know the agenda, write your points BEFORE the meeting.
   Having notes = confidence. You're not "finding words" — you're reading your own notes.

3. USE TEMPLATES:
   This chapter is full of templates. Copy them. Fill in the blanks.
   Over time, they become natural.

4. DON'T APOLOGISE FOR YOUR ENGLISH:
   ❌ "Sorry, my English is bad, but..."
   ✅ Just say what you need to say. If someone doesn't understand, they'll ask.
   
5. CLARIFY WITHOUT SHAME:
   "Could you repeat that?" is completely professional.
   "Let me rephrase to make sure I understand: you're saying [X]?" — this is a SKILL, not a weakness.

6. SIMPLE > COMPLEX:
   ❌ "We should endeavour to ascertain the root cause of the aforementioned issue"
   ✅ "Let's find out why this is happening"
   Simple language = clearer communication = more respected.
```

## 68.15 Common grammar patterns for tech communication

```
REPORTING STATUS:
  "I've finished X" (completed)
  "I'm working on X" (in progress)
  "I'll start X tomorrow" (planned)
  "X is blocked by Y" (passive — focus on the thing, not the person)

SUGGESTING:
  "We could..." / "What if we..." / "How about..."
  "I suggest we..." / "My recommendation is..."

CONDITIONAL:
  "If we do X, then Y will happen."
  "Unless we fix X, the deploy will fail."

CAUSE/EFFECT:
  "X happened because Y." / "Due to X, we need to Y."
  "This causes..." / "This results in..." / "This leads to..."

TIME:
  "by Friday" (deadline — must be done before Friday)
  "until Friday" (ongoing — continues until Friday)
  "since Monday" (started Monday, still happening)
  "within 2 days" (sometime in the next 2 days)
```

---

## Summary

✅ Slack: complete messages (context + what you tried + specific question + timeline)
✅ Emails: 5-line structure (what + action needed + context + deadline + close)
✅ Code reviews: prefix severity ([Must fix] / [Suggestion] / [Nit] / [Question])
✅ Meetings: standup formula, explain decisions (Problem → Options → Recommendation → Tradeoff)
✅ Vocabulary: action words (implement, refactor, fix, optimise, deploy, revert, scope)
✅ Disagreeing: "I have a concern..." + data/reasoning + alternative + "what do you think?"
✅ Non-native tips: clarity > grammar, prepare before meetings, templates, never apologise for accent

## Key takeaway

**In developer communication, CLARITY is the only thing that matters.** Not vocabulary, not grammar, not accent. If people understand you, take action from your messages, and respect your input — your English is good enough. Focus on being specific, concise, and actionable. Everything else is polish.

---

→ [Back to Chapter 67: Reading Skills](./67-READING-SKILLS.md)
