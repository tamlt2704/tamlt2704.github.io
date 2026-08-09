# Chapter 71: Kiro & Kiro Crew — Automate Developer Workflows

## What you'll learn

- Using Kiro CLI for productivity (headless mode, scripting, automation)
- Subagents (Kiro Crew): multi-agent pipelines for complex tasks
- Custom agents: specialized experts for your workflow
- Hooks: trigger actions automatically (pre/post tool use, on completion)
- The Planning Agent: structured requirements → implementation
- Practical workflows: research → implement → review pipelines

---

## PART 1: Kiro CLI Power Features

## 71.1 Headless mode (automation & scripts)

Run Kiro in scripts, CI/CD, or automation without interactive input:

```bash
# Single query — runs and exits
kiro-cli chat --no-interactive --trust-all-tools "Run cargo test and summarize results"

# Trust specific tools only
kiro-cli chat --no-interactive --trust-tools=read,grep,glob "Find all TODO comments in src/"

# In a script with error handling
if kiro-cli chat --no-interactive --trust-all-tools "Check for security vulnerabilities"; then
  echo "Analysis complete"
else
  echo "Failed with exit code $?"
fi

# Pipe output (useful in CI)
kiro-cli chat --no-interactive "List all exported functions in src/api/" > api-exports.txt
```

**Requirements for headless mode:**
- Must provide initial query as argument
- Use `--trust-all-tools` or `--trust-tools=tool1,tool2` (avoids hanging on approval)
- No interactive commands work (`/model` picker, etc.)

## 71.2 Session management (resume work)

```bash
# Save conversation — use /chat save during a session

# Resume last conversation
kiro-cli chat --resume

# Pick from saved conversations
kiro-cli chat --resume-picker

# List all saved sessions
kiro-cli chat --list-sessions
# Chat SessionId: f2946a26-... | 2 hours ago | Implement auth | 15 msgs
# Chat SessionId: 7bd2c90f-... | 1 day ago | Refactor DB layer | 23 msgs

# Delete old sessions
kiro-cli chat --delete-session abc123
```

**Tip:** Sessions are directory-specific. Resume only works for conversations in the current directory.

## 71.3 Agent selection (specialist modes)

```bash
# Start with a specific agent
kiro-cli chat --agent rust-expert
kiro-cli chat --agent aidlc-architect
kiro-cli chat --agent aidlc-qa-engineer

# Switch agent mid-session
/agent rust-expert

# List available agents
kiro-cli agent list
```

---

## PART 2: Subagents (Kiro Crew) — Multi-Agent Pipelines

## 71.4 What is Kiro Crew?

The `subagent` tool spawns multiple AI agents as a pipeline (DAG). Each stage:
- Uses a specialized agent (different expertise/prompt)
- Runs as its own session
- Can depend on other stages (sequential) or run in parallel
- Reports results back to the main agent

```
SIMPLE CHAIN:        "Do this one task"
KIRO CREW:           "Research → Implement → Review" (3 agents, each specialized)
```

## 71.5 Parallel research (3 agents simultaneously)

```
"Compare testing frameworks for our Node.js project"

Pipeline:
  ┌─────────────────┐
  │ jest-research    │──┐
  └─────────────────┘  │
  ┌─────────────────┐  ├──→ Results arrive in parallel
  │ vitest-research  │──┤
  └─────────────────┘  │
  ┌─────────────────┐  │
  │ mocha-research   │──┘
  └─────────────────┘
```

Just ask naturally: *"Compare Jest, Vitest, and Mocha for our project — research each in parallel."*

The subagent tool configuration:
```json
{
  "task": "Compare testing frameworks for our Node.js project",
  "stages": [
    {"name": "jest-research", "role": "kiro_default", "prompt_template": "Research Jest for {task}"},
    {"name": "vitest-research", "role": "kiro_default", "prompt_template": "Research Vitest for {task}"},
    {"name": "mocha-research", "role": "kiro_default", "prompt_template": "Research Mocha for {task}"}
  ]
}
```

All three start immediately (no `depends_on` → parallel).

## 71.6 Sequential pipeline (Research → Implement → Review)

```
Pipeline:
  research ──→ implement ──→ review
  (gather       (write         (check
   context)      code)          quality)
```

```json
{
  "task": "Add CSV export to the reports page",
  "stages": [
    {"name": "research", "role": "kiro_default", "prompt_template": "Gather requirements and existing code patterns for {task}"},
    {"name": "implement", "role": "kiro_default", "prompt_template": "Implement {task}", "depends_on": ["research"]},
    {"name": "review", "role": "kiro_default", "prompt_template": "Review the implementation of {task}", "depends_on": ["implement"]}
  ]
}
```

`research` starts → when done, `implement` starts → when done, `review` starts.

## 71.7 Fan-out / Fan-in (parallel → merge)

```
  security-scan ──┐
                   ├──→ report (merges findings)
  perf-analysis ──┘
```

```json
{
  "task": "Audit the authentication module",
  "stages": [
    {"name": "security-scan", "role": "aidlc-security-engineer", "prompt_template": "Scan for vulnerabilities in {task}"},
    {"name": "perf-analysis", "role": "kiro_default", "prompt_template": "Analyze performance of {task}"},
    {"name": "report", "role": "kiro_default", "prompt_template": "Compile findings for {task}", "depends_on": ["security-scan", "perf-analysis"]}
  ]
}
```

Both scans run in parallel → both must finish before report stage starts.

## 71.8 Monitor progress

Press `Ctrl+G` during a crew pipeline to see stage status (which stages are running, complete, or waiting).

---

## PART 3: Custom Agents

## 71.9 Create a specialized agent

Create `.kiro/agents/code-reviewer.json`:

```json
{
  "name": "code-reviewer",
  "description": "Expert code reviewer focused on quality and security",
  "prompt": "You are an expert code reviewer. Focus on: security vulnerabilities, performance issues, readability, test coverage gaps, and best practices violations. Be specific, reference line numbers, and suggest fixes.",
  "tools": ["read", "grep", "glob", "code"],
  "allowedTools": ["read", "grep", "glob", "code"],
  "resources": ["file://src/**/*", "file://tests/**/*"],
  "keyboardShortcut": "ctrl+shift+r",
  "welcomeMessage": "Ready to review code. Point me at a file or PR."
}
```

```bash
# Use it
kiro-cli chat --agent code-reviewer "Review src/auth/login.ts for security issues"

# Or switch mid-session
/agent code-reviewer
```

## 71.10 Agent for documentation generation

```json
{
  "name": "doc-writer",
  "description": "Generates API documentation and READMEs",
  "prompt": "You are a technical documentation specialist. Generate clear, concise documentation with examples. Use markdown formatting. Include: description, parameters, return values, examples, and edge cases.",
  "tools": ["read", "write", "grep", "glob", "code"],
  "allowedTools": ["read", "grep", "glob", "code"],
  "resources": ["file://src/**/*", "file://README.md"],
  "welcomeMessage": "I'll help document your code. What needs documentation?"
}
```

## 71.11 Agent for test generation

```json
{
  "name": "test-writer",
  "description": "Generates comprehensive unit and integration tests",
  "prompt": "You are a QA engineer. Generate thorough tests covering: happy path, edge cases, error cases, boundary conditions. Use the project's existing test framework and style. Include arrange/act/assert pattern with clear test names.",
  "tools": ["read", "write", "grep", "glob", "code", "shell"],
  "allowedTools": ["read", "grep", "glob", "code"],
  "toolsSettings": {
    "shell": {
      "allowedCommands": ["npm test", "cargo test", "./gradlew test"]
    }
  },
  "resources": ["file://src/**/*", "file://tests/**/*"],
  "welcomeMessage": "Point me at code to test. I'll generate comprehensive test cases."
}
```

## 71.12 Control which agents can be used in crews

```json
{
  "toolsSettings": {
    "crew": {
      "availableAgents": ["code-reviewer", "test-writer", "doc-writer", "kiro_default"],
      "trustedAgents": ["code-reviewer", "doc-writer"]
    }
  }
}
```

- `availableAgents`: which agents can be spawned as subagents (glob patterns supported: `"test-*"`)
- `trustedAgents`: agents that run without asking for your approval

---

## PART 4: Hooks — Automatic Actions

## 71.13 What hooks do

Hooks execute commands at trigger points in the agent lifecycle:

| Trigger | When | Use case |
|---------|------|----------|
| `agentSpawn` | Agent starts | Load context (git status, env info) |
| `userPromptSubmit` | User sends message | Log prompts, inject context |
| `preToolUse` | Before any tool runs | Validate, block dangerous ops |
| `postToolUse` | After tool completes | Log, format, notify |
| `stop` | Agent finishes responding | Auto-format, auto-test, compile check |

## 71.14 Practical hook examples

**Auto-run tests after code changes:**
```json
{
  "hooks": {
    "stop": [
      {
        "command": "npm test -- --silent 2>&1 | tail -5"
      }
    ]
  }
}
```

**Show git status when agent starts:**
```json
{
  "hooks": {
    "agentSpawn": [
      { "command": "git status --short" },
      { "command": "git log --oneline -5" }
    ]
  }
}
```

**Block writes to protected files:**
```json
{
  "hooks": {
    "preToolUse": [
      {
        "matcher": "write",
        "command": "bash -c 'INPUT=$(cat); FILE=$(echo $INPUT | jq -r .tool_input.path // empty); if [[ \"$FILE\" == *\".env\"* ]] || [[ \"$FILE\" == *\"secrets\"* ]]; then echo \"BLOCKED: Cannot write to $FILE\" >&2; exit 2; fi'"
      }
    ]
  }
}
```

Exit code 2 from a `preToolUse` hook = **blocks** the tool from executing.

**Auto-format on file write:**
```json
{
  "hooks": {
    "postToolUse": [
      {
        "matcher": "write",
        "command": "bash -c 'INPUT=$(cat); FILE=$(echo $INPUT | jq -r .tool_input.path // empty); if [[ \"$FILE\" == *.ts ]] || [[ \"$FILE\" == *.js ]]; then npx prettier --write \"$FILE\" 2>/dev/null; fi'"
      }
    ]
  }
}
```

## 71.15 Hook settings

```json
{
  "hooks": {
    "preToolUse": [
      {
        "matcher": "shell",
        "command": "/path/to/validator.sh",
        "timeout_ms": 5000,
        "cache_ttl_seconds": 60
      }
    ]
  }
}
```

- `timeout_ms`: max execution time (default 10000ms)
- `cache_ttl_seconds`: cache output for N seconds (0 = no cache)

Hide hook status messages (silent hooks):
```bash
kiro-cli settings hooks.showStatus false
```

---

## PART 5: The Planning Agent

## 71.16 Structured planning before coding

Press `Shift+Tab` or type `/plan` to enter planning mode:

```
> /plan Build a REST API for user authentication

[plan] > I understand you want to build an auth API.

[1]: What authentication method?
a. Email/Password
b. OAuth (Google, GitHub)
c. Magic Links
d. Multi-factor

[2]: What's your tech stack?
a. Node.js + Express
b. Spring Boot
c. Other

> 1=a, 2=b

[plan] > *Researching Spring Boot auth patterns...*
         *Exploring your existing codebase...*

**Implementation Plan:**
Task 1: Create User entity and repository
Task 2: Implement JWT service
Task 3: Build login/register endpoints
Task 4: Add security filter chain

Ready to implement? [y/n]: y
```

Planning agent is **read-only** — it can't modify files. It researches, plans, then hands off to the execution agent.

---

## PART 6: Productivity Workflows

## 71.17 Daily development workflow

```bash
# Morning: start with context
kiro-cli chat --agent my-dev-agent
> "What did I work on yesterday? Show me my recent git commits and any open PRs."

# Deep work: implement a feature
> "Implement the notification service based on the design in docs/notification-design.md"

# Save progress
/chat save

# Code review: switch agent
/agent code-reviewer
> "Review the changes I just made in src/notifications/"

# End of day: documentation
/agent doc-writer
> "Update the README to include the new notification API endpoints"
```

## 71.18 Automated CI/CD integration

```bash
#!/bin/bash
# .github/scripts/ai-review.sh — AI code review in CI

# Review changed files
CHANGED_FILES=$(git diff --name-only HEAD~1)

kiro-cli chat --no-interactive --trust-all-tools \
  "Review these changed files for issues: $CHANGED_FILES. 
   Focus on security, performance, and breaking changes.
   Output as a markdown checklist."
```

## 71.19 Batch operations

```bash
# Generate tests for all new files
kiro-cli chat --no-interactive --trust-all-tools --agent test-writer \
  "Generate unit tests for all files in src/services/ that don't have test files yet"

# Document undocumented functions
kiro-cli chat --no-interactive --trust-all-tools --agent doc-writer \
  "Find all exported functions in src/ without JSDoc comments and add documentation"

# Refactor pattern
kiro-cli chat --no-interactive --trust-all-tools \
  "Find all console.log statements in src/ and replace with proper logger calls"
```

## 71.20 Research pipeline (crew)

For complex research tasks, ask Kiro to use multiple agents:

```
"I need to choose between Kafka and RabbitMQ for our event system.
Research both in parallel — one agent per technology — then compile 
a comparison with pros/cons and a recommendation for our use case
(50K events/sec, at-least-once delivery, 3 consumers)."
```

Kiro spawns the crew automatically:
- Agent 1: researches Kafka
- Agent 2: researches RabbitMQ  
- Agent 3: waits for both, then compiles comparison

---

## Summary

✅ Headless mode: `--no-interactive --trust-all-tools` for scripting/CI
✅ Session management: save/resume conversations across sessions
✅ Subagents (Crew): parallel research, sequential pipelines, fan-out/fan-in patterns
✅ Custom agents: specialized JSON configs for reviewer, test-writer, doc-writer
✅ Hooks: auto-actions on spawn, tool use, completion (block, format, test, log)
✅ Planning agent: structured requirements → plan → handoff to implementation
✅ Practical workflows: daily dev, CI/CD, batch operations, research pipelines

## Key takeaways

**Kiro Crew is parallel brainpower.** Instead of one agent doing everything sequentially, spawn 3 agents researching in parallel. Results arrive 3× faster with specialized focus.

**Custom agents are your productivity multiplier.** A `code-reviewer` agent with specific instructions catches different things than a general assistant. A `test-writer` produces better tests because its ENTIRE prompt is about testing. Specialization works for AI just like it works for people.

**Hooks automate the tedious.** Auto-format on save, auto-test on completion, block writes to .env — these small automations remove friction from every interaction. Set up once, benefit forever.

**Headless mode turns Kiro into a CI tool.** Run code reviews, generate docs, check for patterns — all as automated scripts in your pipeline. `$?` exit codes integrate with any CI system.

---

→ [Back to Chapter 70: Experiments with Kids](./70-EXPERIMENTS-WITH-KIDS.md)
