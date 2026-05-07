# Chapter 0: Before You Start

[Chapter 1: Your First Test →](chapter-01-first-test.md)

---

## The Story

You're a frontend engineer at **ShipFast**, a mid-size SaaS company that builds project management tools. The app has grown to 200+ pages, dozens of forms, complex workflows, and integrations with Slack, GitHub, and Stripe.

Testing is a mess. The QA team manually clicks through critical paths before every release. It takes 3 days. They miss regressions constantly. Last month, a broken login flow shipped to production and wasn't caught for 6 hours.

Your engineering manager, **Dana**, pulls you aside:

"We need automated end-to-end tests. Real browser tests that click buttons, fill forms, and verify the app works. I've heard Playwright is the modern choice. You have two weeks to set up a test suite that covers our critical paths — login, project creation, task management, billing. If it works, we roll it out to the whole team."

You've written unit tests. You've written integration tests. But browser automation? That's a different world. Flaky selectors, timing issues, network races, authentication flows, file uploads, iframes, multiple tabs...

Over the next 12 chapters, you'll build a production-grade Playwright test suite from scratch. Every chapter solves a real testing problem — and every naive approach fails in a way that teaches you why Playwright's API is designed the way it is.

## How to Read This

Every chapter follows the same loop:

1. A testing scenario that seems simple but isn't
2. The naive approach that breaks
3. Why it breaks (timing, flakiness, architecture)
4. The Playwright way that handles it correctly
5. The pattern you'll reuse everywhere

No API shows up before you need it. You won't learn about fixtures until your tests need shared setup. You won't touch network interception until you need to test error states.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Frontend Engineer | "I've written Jest tests. How different can browser tests be?" |
| **Dana** | Engineering Manager | Pragmatic. "Does it catch regressions? Ship it." |
| **Marcus** | Senior QA | Skeptical of automation. "I've seen Selenium suites rot." |
| **The App** | ShipFast | React SPA, Next.js, REST API, WebSocket notifications |
| **CI** | GitHub Actions | Where tests must pass before merge |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | Need to verify the app works at all | First test, navigation, assertions, running tests |
| 2 | Tests break when selectors change | Locators, roles, test IDs, best practices |
| 3 | Tests fail because the page isn't ready | Auto-waiting, actionability, web-first assertions |
| 4 | Need to interact with forms and inputs | Filling forms, dropdowns, checkboxes, file uploads |
| 5 | Every test needs to log in first | Authentication, storage state, fixtures |
| 6 | Tests are slow and repetitive | Page Object Model, reusable helpers, organization |
| 7 | Need to test error states and edge cases | Network interception, mocking API responses |
| 8 | Tests pass locally but fail in CI | Configuration, browsers, retries, parallelism |
| 9 | Can't debug why a test failed | Tracing, screenshots, videos, debugging tools |
| 10 | Need to test complex UI interactions | Drag-and-drop, modals, toasts, keyboard, multi-tab |
| 11 | Need to test visual appearance | Visual regression testing, screenshot comparison |
| 12 | Need to test the full workflow end-to-end | API testing, database seeding, complete flows |

## Prerequisites

### Node.js 18+

```bash
node --version
# v18.x or higher
```

### A Fresh Project

```bash
mkdir shipfast-tests
cd shipfast-tests
npm init -y
```

### Install Playwright

```bash
npm init playwright@latest
```

This installs Playwright and downloads browser binaries (Chromium, Firefox, WebKit). Say yes to the defaults:
- TypeScript: Yes
- Tests folder: `tests`
- GitHub Actions workflow: Yes
- Install browsers: Yes

### Verify Installation

```bash
npx playwright test --version
```

### Project Structure After Setup

```
shipfast-tests/
├── tests/
│   └── example.spec.ts
├── playwright.config.ts
├── package.json
└── node_modules/
```

## The Key Idea

Unit tests verify functions in isolation. Integration tests verify modules together. **End-to-end tests verify the application from the user's perspective** — real browsers, real clicks, real page loads.

| | Unit Tests | E2E Tests |
|---|---|---|
| Speed | Milliseconds | Seconds |
| Scope | One function | Entire user flow |
| Dependencies | Mocked | Real (or intercepted) |
| Confidence | "This function works" | "The user can do this" |
| Maintenance | Low | Higher (UI changes) |
| Flakiness | Rare | Common (if done wrong) |

Playwright's job: make E2E tests fast, reliable, and maintainable. It auto-waits for elements, runs tests in parallel, provides powerful debugging tools, and works across Chromium, Firefox, and WebKit.

The goal isn't 100% E2E coverage. It's covering the critical paths that, if broken, would cost the company money or users.

## What Makes Playwright Different

If you've used Selenium or Cypress, Playwright is a generational leap:

| Feature | Selenium | Cypress | Playwright |
|---|---|---|---|
| Multi-browser | Yes (slow) | Chromium only* | Chromium, Firefox, WebKit |
| Auto-waiting | No | Partial | Full |
| Multi-tab/window | Painful | No | Native |
| Network interception | No | Yes | Yes (more powerful) |
| Parallelism | External tools | Limited | Built-in |
| Language | Many | JS only | JS, Python, Java, C# |
| iframes | Painful | Painful | Native |
| Speed | Slow | Fast | Fastest |

*Cypress added experimental multi-browser support later.

Playwright controls browsers via the Chrome DevTools Protocol (CDP) and equivalent protocols for Firefox and WebKit. It's not injecting scripts into the page — it's controlling the browser from outside, which gives it superpowers: multiple tabs, downloads, geolocation, permissions, and more.

## Notation

Throughout the course:

```typescript
// This is a test file (*.spec.ts)
import { test, expect } from '@playwright/test';

test('description of what this verifies', async ({ page }) => {
  // Test code here
});
```

- `test` — defines a test case
- `expect` — makes assertions
- `page` — a browser tab you control
- `async/await` — everything is asynchronous (browser operations take time)

Let's write your first test.

---

[Chapter 1: Your First Test →](chapter-01-first-test.md)
