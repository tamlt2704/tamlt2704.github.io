# Chapter 1: Your First Test

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Locators →](chapter-02-locators.md)

---

## The Problem

Dana wants proof of concept by end of day. "Show me one test that verifies login works. If you can do that, I'll give you the two weeks."

You need to:
1. Open a browser
2. Navigate to the login page
3. Verify something is there
4. Close the browser

Sounds simple. Let's see.

## The Simplest Possible Test

Create `tests/login.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';

test('login page loads', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc');
  await expect(page).toHaveTitle(/TodoMVC/);
});
```

Run it:

```bash
npx playwright test tests/login.spec.ts
```

Output:
```
Running 3 tests using 3 workers
  3 passed (2.1s)
```

Wait — 3 tests? You wrote one. Playwright runs each test across all configured browsers (Chromium, Firefox, WebKit) by default. Three browsers, one test each = 3 test runs.

## Anatomy of a Test

```typescript
import { test, expect } from '@playwright/test';
//      ^^^^  ^^^^^^
//      |     Assertion library
//      Test runner

test('login page loads', async ({ page }) => {
//   ^^^^^^^^^^^^^^^^^^         ^^^^^^
//   Test name (shows in        Fixture: a fresh browser tab
//   reports)                   (Playwright creates it for you)

  await page.goto('https://demo.playwright.dev/todomvc');
  //    ^^^^^^^^^^
  //    Navigate to URL. Waits for page to load.

  await expect(page).toHaveTitle(/TodoMVC/);
  //    ^^^^^^       ^^^^^^^^^^^
  //    Web-first    Retries until true or timeout
  //    assertion
});
```

Every line is `await` because browser operations are asynchronous. The browser is a separate process — you're sending commands to it and waiting for responses.

## Running Tests

```bash
# Run all tests
npx playwright test

# Run a specific file
npx playwright test tests/login.spec.ts

# Run in headed mode (see the browser)
npx playwright test --headed

# Run in a specific browser
npx playwright test --project=chromium

# Run a specific test by name
npx playwright test -g "login page loads"
```

### Headed vs Headless

By default, tests run **headless** — no visible browser window. This is fast and works in CI.

For debugging, use `--headed` to watch the browser:

```bash
npx playwright test --headed
```

## Navigation

```typescript
test('navigate to pages', async ({ page }) => {
  // Go to a URL
  await page.goto('https://example.com');
  
  // Wait for a specific URL pattern
  await page.goto('https://example.com/dashboard');
  await expect(page).toHaveURL(/dashboard/);
  
  // Go back/forward
  await page.goBack();
  await page.goForward();
  
  // Reload
  await page.reload();
});
```

`page.goto()` waits for the page to reach the `load` state by default. You can change this:

```typescript
// Wait until there are no network requests for 500ms
await page.goto('https://example.com', { waitUntil: 'networkidle' });

// Wait only for the DOM to be ready (faster, less reliable)
await page.goto('https://example.com', { waitUntil: 'domcontentloaded' });
```

## Basic Assertions

Playwright's assertions are **web-first** — they automatically retry until the condition is met or the timeout expires.

```typescript
test('basic assertions', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc');
  
  // Page-level assertions
  await expect(page).toHaveTitle(/TodoMVC/);
  await expect(page).toHaveURL(/todomvc/);
  
  // Element assertions
  const header = page.locator('h1');
  await expect(header).toBeVisible();
  await expect(header).toHaveText('todos');
  await expect(header).toContainText('todo');
  
  // Element state
  const input = page.locator('.new-todo');
  await expect(input).toBeVisible();
  await expect(input).toBeEnabled();
  await expect(input).toBeEmpty();
  
  // Count elements
  const items = page.locator('.todo-list li');
  await expect(items).toHaveCount(0);
});
```

### Why "Web-First" Matters

Traditional assertion (fails immediately):
```typescript
// BAD: checks once, fails if element isn't ready yet
const text = await page.textContent('h1');
expect(text).toBe('todos');  // Might fail if page is still loading!
```

Web-first assertion (retries automatically):
```typescript
// GOOD: retries for up to 5 seconds
await expect(page.locator('h1')).toHaveText('todos');
```

Web-first assertions handle timing automatically. The element might not exist yet, might be loading, might be animating in. The assertion waits patiently.

## Interacting with the Page

```typescript
test('add a todo item', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc');
  
  // Type into an input
  const input = page.locator('.new-todo');
  await input.fill('Buy groceries');
  
  // Press Enter
  await input.press('Enter');
  
  // Verify the item was added
  const items = page.locator('.todo-list li');
  await expect(items).toHaveCount(1);
  await expect(items.first()).toHaveText('Buy groceries');
});
```

### Click, Fill, Press

```typescript
// Click a button
await page.locator('button.submit').click();

// Fill an input (clears existing text first)
await page.locator('#email').fill('user@example.com');

// Type character by character (for autocomplete, etc.)
await page.locator('#search').type('playwright');

// Press a key
await page.locator('#input').press('Enter');
await page.locator('#input').press('Control+a');

// Check a checkbox
await page.locator('#agree').check();

// Select from dropdown
await page.locator('#country').selectOption('US');
```

## A Real Login Test

Let's write what Dana asked for — a login test against a demo app:

```typescript
test('user can log in', async ({ page }) => {
  // Navigate to login page
  await page.goto('https://the-internet.herokuapp.com/login');
  
  // Fill in credentials
  await page.locator('#username').fill('tomsmith');
  await page.locator('#password').fill('SuperSecretPassword!');
  
  // Click login button
  await page.locator('button[type="submit"]').click();
  
  // Verify successful login
  await expect(page).toHaveURL(/secure/);
  await expect(page.locator('.flash.success')).toContainText('You logged into a secure area!');
});
```

Run it:
```bash
npx playwright test tests/login.spec.ts --headed
```

You watch the browser open, navigate to the page, fill in the form, click the button, and verify the result. All in about 2 seconds.

## Test Structure: describe and test.describe

Group related tests:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Login', () => {
  test('successful login', async ({ page }) => {
    await page.goto('https://the-internet.herokuapp.com/login');
    await page.locator('#username').fill('tomsmith');
    await page.locator('#password').fill('SuperSecretPassword!');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/secure/);
  });

  test('failed login shows error', async ({ page }) => {
    await page.goto('https://the-internet.herokuapp.com/login');
    await page.locator('#username').fill('wrong');
    await page.locator('#password').fill('wrong');
    await page.locator('button[type="submit"]').click();
    await expect(page.locator('.flash.error')).toBeVisible();
  });
});
```

## Before/After Hooks

```typescript
test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Runs before every test in this describe block
    await page.goto('https://example.com/login');
    await page.locator('#email').fill('user@test.com');
    await page.locator('#password').fill('password');
    await page.locator('button[type="submit"]').click();
  });

  test('shows welcome message', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Welcome');
  });

  test('shows project list', async ({ page }) => {
    await expect(page.locator('.project-list')).toBeVisible();
  });
});
```

## The HTML Report

After running tests, Playwright generates an HTML report:

```bash
npx playwright test
npx playwright show-report
```

This opens a browser with:
- Pass/fail status for each test
- Duration
- Browser used
- Screenshots on failure (if configured)
- Trace files for debugging

## Dana's Reaction

You show Dana the login test running in headed mode. She watches the browser fill in the form and verify the redirect.

Dana: "That's it? That's the whole test?"

You: "That's it. Playwright handles the browser lifecycle, waiting for elements, and assertions. I just describe what the user does."

Dana: "But those selectors — `#username`, `button[type="submit"]` — what happens when the frontend team changes the HTML?"

You: "That's the next problem. CSS selectors are brittle. Playwright has better ways to find elements."

## What You Learned

- **Test structure** — `test('name', async ({ page }) => { ... })`
- **Navigation** — `page.goto(url)` with automatic wait for page load
- **Interactions** — `fill()`, `click()`, `press()`, `check()`
- **Assertions** — web-first assertions that retry automatically
- **Running tests** — `npx playwright test` with options for headed, browser, grep
- **Hooks** — `beforeEach` for shared setup
- **Reports** — HTML report with pass/fail, duration, screenshots

The test works. But it's fragile — tied to CSS selectors that break when the UI changes. The next chapter introduces locators: Playwright's resilient way to find elements.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Locators →](chapter-02-locators.md)
