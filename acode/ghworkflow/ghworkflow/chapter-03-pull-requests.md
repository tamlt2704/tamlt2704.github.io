# Chapter 3: The Self-Review — "I Merged a Bug I Could've Caught"

[← Chapter 2: Branches](chapter-02-branches.md) | [Chapter 4: The Robot →](chapter-04-github-actions.md)

---

## The Disaster

Wednesday. You finish `feature/contact-form`. You merge it locally:

```bash
git checkout main
git merge feature/contact-form
git push
npm run deploy
```

The site deploys. You go to bed. Thursday morning you check the live site. The contact form is there. But the submit button does nothing. You open the code:

```tsx
<button onClick={handleSubmit}>Send</button>
```

```tsx
const handleSubmit = () => {
  // TODO: implement
}
```

You shipped a button that does nothing. You merged it without looking. If you'd spent 30 seconds reviewing the diff, you'd have caught it.

"But I'm solo — who am I reviewing for?"

Future You. You're reviewing for Future You.

## Pull Requests for One

A pull request (PR) is a proposal to merge one branch into another. On a team, someone else reviews it. Solo, you review it yourself. The point isn't the reviewer — it's the **pause**. The moment between "I think I'm done" and "I'm sure I'm done."

### Create a PR

Push your branch:

```bash
git push -u origin feature/contact-form
```

Go to your repo on GitHub. Click "Compare & pull request." Fill in:

- **Title**: `Add contact form with email validation`
- **Description**: What changed and why

```markdown
## What
- Contact form component with name, email, message fields
- Client-side validation
- Sends to Formspree endpoint

## Why
Need a way for visitors to reach me.

## Testing
- [x] Form validates empty fields
- [x] Email format check works
- [x] Submission sends to Formspree
- [ ] ← you would've noticed this checkbox is unchecked
```

Click "Create pull request."

### Review Your Own Code

Click the "Files changed" tab. GitHub shows you the diff — every line you added, removed, or modified, highlighted in green and red.

```diff
+ const handleSubmit = () => {
+   // TODO: implement
+ }
```

There it is. Green. Staring at you. A `TODO` you forgot about.

The diff view is a different perspective. When you're coding, you're in "build mode" — focused on making things work. When you're reviewing a diff, you're in "audit mode" — focused on what's wrong. Same brain, different lens.

### What to Look For (Solo Checklist)

When reviewing your own PR, scan for:

- [ ] **TODOs left behind** — the #1 solo developer bug
- [ ] **Console.logs** — you left debug output in production
- [ ] **Commented-out code** — either delete it or uncomment it
- [ ] **Hardcoded values** — URLs, API keys, magic numbers
- [ ] **Missing error handling** — what happens when the API is down?
- [ ] **Unused imports** — clutter
- [ ] **Does the title match the changes?** — scope creep check

You don't need to be thorough. A 30-second scan catches 80% of the dumb mistakes.

### Merge the PR

Once you're satisfied, click "Merge pull request" → "Confirm merge."

GitHub creates a merge commit on `main`. Your branch is merged. Click "Delete branch" to clean up.

```
main:  c1 ── c2 ── c3 ── M (merge commit)
                    \    /
feature/contact:     c4 ─┘
```

## Branch Protection: The Green Lock

You trust yourself. But you also pushed a `TODO` to production. Let's add a safety net.

Go to your repo → Settings → Branches → Add rule.

Branch name pattern: `main`

Check:
- [x] **Require a pull request before merging** — no more `git push` directly to `main`
- [x] **Require status checks to pass** — we'll set this up in Chapter 4

Save.

Now if you try to push directly to `main`:

```bash
git checkout main
git commit -m "quick fix"
git push
# remote: error: GH006: Protected branch update failed
# remote: At least 1 approving review is required
```

Blocked. The Green Lock won't let you. You MUST go through a PR.

"But I'm solo — I can't approve my own PR!"

Yes you can. Under the branch protection rule, **don't** check "Require approvals." Just require the PR itself. The PR forces you to see the diff. That's the value.

```
Settings → Branches → main
├── ✅ Require pull request before merging
│   └── Required approvals: 0     ← set to 0 for solo
├── ✅ Require status checks (Chapter 4)
└── ❌ Require approvals           ← leave unchecked
```

## PR Templates: Automate the Checklist

Tired of writing the same PR description? Create a template.

```bash
mkdir -p .github
```

```markdown
<!-- .github/pull_request_template.md -->
## What changed
<!-- Brief description -->

## Why
<!-- Motivation -->

## Checklist
- [ ] No TODOs left behind
- [ ] No console.logs in production code
- [ ] No hardcoded secrets or API keys
- [ ] Tested locally with `npm run build`
- [ ] Tested locally with `npm run dev`
```

Every new PR auto-fills with this template. You can't forget the checklist because it's already there.

## The Workflow So Far

```
1. git checkout -b feature/thing     # branch off main
2. ... code, commit, code, commit ...
3. git push -u origin feature/thing  # push branch
4. Open PR on GitHub                 # see the diff
5. Review your own changes           # 30-second scan
6. Merge PR                          # merge to main
7. Delete branch                     # clean up
```

Seven steps. Takes 2 minutes longer than pushing directly to `main`. Catches bugs that would take 2 hours to debug in production.

## Squash vs Merge vs Rebase

When you click "Merge pull request," GitHub offers three options:

| Strategy | What It Does | When to Use |
|---|---|---|
| **Create a merge commit** | Preserves all branch commits + adds a merge commit | You want full history |
| **Squash and merge** | Combines all branch commits into one | Clean history, messy branch |
| **Rebase and merge** | Replays branch commits on top of main | Linear history, no merge commits |

For solo work, **squash and merge** is cleanest. Your branch might have 5 commits like:

```
"WIP dark mode"
"fix typo"
"actually fix it"
"ok now it works"
"forgot to save"
```

Squash turns that into one clean commit on `main`:

```
"Add dark mode toggle with localStorage persistence"
```

Set it as default: Settings → General → Pull Requests → check "Allow squash merging" and uncheck the others if you want to enforce it.

## What You Learned

- Pull requests are a pause between "done" and "merged"
- The diff view catches bugs your editor doesn't
- Branch protection prevents pushing directly to `main`
- PR templates automate your review checklist
- Squash merge keeps `main` history clean
- 30 seconds of self-review saves hours of debugging

You're branching. You're reviewing. You're merging through PRs. But you're still deploying manually — `npm run deploy` after every merge. You forget sometimes. The site gets stale.

Next chapter: a robot that deploys for you every time you merge to `main`.

---

[← Chapter 2: Branches](chapter-02-branches.md) | [Chapter 4: The Robot →](chapter-04-github-actions.md)
