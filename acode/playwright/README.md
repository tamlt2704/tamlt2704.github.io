# Playwright

A 12-chapter course that builds a production-grade E2E test suite from scratch. Every chapter solves a real testing problem — flaky selectors, timing issues, authentication, CI failures, and more.

## Story

You're a frontend engineer at ShipFast, tasked with replacing a 3-day manual QA process with automated browser tests. You have two weeks.

## Chapters

| Ch | Title | Core Concept |
|---|---|---|
| 0 | [Overview](chapter-00-overview.md) | Setup, prerequisites, roadmap |
| 1 | [Your First Test](chapter-01-first-test.md) | Navigation, assertions, running tests |
| 2 | [Locators](chapter-02-locators.md) | Roles, labels, test IDs, resilient selectors |
| 3 | [Auto-Waiting](chapter-03-auto-waiting.md) | Actionability, web-first assertions, no sleeps |
| 4 | [Forms and Inputs](chapter-04-forms-inputs.md) | Fill, check, select, upload, date pickers |
| 5 | [Authentication](chapter-05-authentication.md) | Storage state, global setup, multiple roles |
| 6 | [Page Object Model](chapter-06-page-objects.md) | Encapsulation, fixtures, maintainability |
| 7 | [Network Interception](chapter-07-network-interception.md) | Mocking APIs, error states, HAR files |
| 8 | [CI Configuration](chapter-08-ci-configuration.md) | GitHub Actions, retries, parallelism, sharding |
| 9 | [Debugging](chapter-09-debugging.md) | Traces, UI mode, inspector, screenshots |
| 10 | [Advanced Interactions](chapter-10-advanced-interactions.md) | Drag-drop, modals, multi-tab, iframes |
| 11 | [Visual Testing](chapter-11-visual-testing.md) | Screenshot comparison, responsive, dark mode |
| 12 | [End-to-End Flows](chapter-12-e2e-flows.md) | API testing, multi-user, complete journeys |

## Prerequisites

- Node.js 18+
- `npm init playwright@latest`

## Quick Start

```bash
mkdir my-tests && cd my-tests
npm init playwright@latest
npx playwright test
```
