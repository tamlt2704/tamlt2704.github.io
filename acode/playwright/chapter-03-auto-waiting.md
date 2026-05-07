# Chapter 3: Auto-Waiting

[← Chapter 2: Locators](chapter-02-locators.md) | [Chapter 4: Forms and Inputs →](chapter-04-forms-inputs.md)

---

## The Problem

Your test clicks "Create Project" and immediately checks for the new project in the list. It fails. The project takes 800ms to appear (API call + re-render). You add `await page.waitForTimeout(1000)` and it passes. Then it fails in CI where the API is slower. You bump it to 3000ms. Now the test is slow and still occasionally flaky.

Marcus: "This is the #1 reason Selenium suites die. Sleep statements everywhere. Tests that take 20 minutes because they're 80% waiting."

You're right to hate `waitForTimeout`. It's either too short (flaky) or too long (slow). Playwright has a better way.

## Playwright's Auto-Wait Mechanism

Every Playwright action automatically waits for the element to be **actionable** before proceeding:

```typescript
// This single line does ALL of this:
await page.getByRole('button', { name: 'Submit' }).click();

// 1. Wait for the element to appear in the DOM
// 2. Wait for it to be visible (not hidden, not zero-size)
// 3. Wait for it to be stable (not animating)
// 4. Wait for it to be enabled (not disabled)
// 5. Wait for it to receive pointer events (not covered by another element)
// 6. Scroll it into view if needed
// 7. Click the center of the element
```

You never write explicit waits for these conditions. Playwright handles them.

## Actionability Checks

Different actions wait for different conditions:

| Action | Visible | Stable | Enabled | Receives Events |
|---|---|---|---|---|
| `click()` | ✓ | ✓ | ✓ | ✓ |
| `fill()` | ✓ | ✓ | ✓ | ✓ |
| `check()` | ✓ | ✓ | ✓ | ✓ |
| `hover()` | ✓ | ✓ | | ✓ |
| `textContent()` | | | | |
| `isVisible()` | | | | |

`textContent()` and `isVisible()` don't wait — they return the current state immediately. That's why you should use web-first assertions instead.

## Web-First Assertions: The Right Way to Wait

```typescript
// BAD: checks once, fails if not ready
const text = await page.locator('.status').textContent();
expect(text).toBe('Complete');  // Might fail!

// GOOD: retries until true or timeout (default 5s)
await expect(page.locator('.status')).toHaveText('Complete');
```

Web-first assertions retry automatically:

```typescript
test('project creation', async ({ page }) => {
  await page.goto('/projects');
  await page.getByRole('button', { name: 'New Project' }).click();
  await page.getByLabel('Project name').fill('My Project');
  await page.getByRole('button', { name: 'Create' }).click();
  
  // This retries for up to 5 seconds until the project appears
  await expect(page.getByText('My Project')).toBeVisible();
  
  // This retries until the URL changes
  await expect(page).toHaveURL(/projects\/\d+/);
  
  // This retries until the count matches
  await expect(page.locator('.project-card')).toHaveCount(1);
});
```

## Common Web-First Assertions

```typescript
// Visibility
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();

// Text content
await expect(locator).toHaveText('exact text');
await expect(locator).toContainText('partial');
await expect(locator).toHaveText(/regex/);

// Input values
await expect(locator).toHaveValue('input value');
await expect(locator).toBeEmpty();

// State
await expect(locator).toBeEnabled();
await expect(locator).toBeDisabled();
await expect(locator).toBeChecked();

// Attributes and CSS
await expect(locator).toHaveAttribute('href', '/dashboard');
await expect(locator).toHaveClass(/active/);
await expect(locator).toHaveCSS('color', 'rgb(255, 0, 0)');

// Count
await expect(locator).toHaveCount(5);

// Page-level
await expect(page).toHaveTitle(/Dashboard/);
await expect(page).toHaveURL(/dashboard/);
```

## Negation: Waiting for Things to Disappear

```typescript
test('loading spinner disappears', async ({ page }) => {
  await page.getByRole('button', { name: 'Load Data' }).click();
  
  // Wait for spinner to appear
  await expect(page.locator('.spinner')).toBeVisible();
  
  // Wait for spinner to disappear (retries until hidden)
  await expect(page.locator('.spinner')).toBeHidden();
  
  // Or using .not
  await expect(page.locator('.spinner')).not.toBeVisible();
});
```

## Configuring Timeouts

```typescript
// Per-assertion timeout
await expect(page.locator('.result')).toBeVisible({ timeout: 10000 });

// Global timeout in playwright.config.ts
export default defineConfig({
  expect: {
    timeout: 5000,  // Default assertion timeout
  },
  timeout: 30000,   // Default test timeout
});
```

## When You Actually Need to Wait

Rare cases where auto-waiting isn't enough:

### Waiting for Navigation

```typescript
// Wait for navigation after clicking a link
await page.getByRole('link', { name: 'Dashboard' }).click();
await page.waitForURL('**/dashboard');
```

### Waiting for Network Requests

```typescript
// Wait for an API call to complete
const responsePromise = page.waitForResponse('**/api/projects');
await page.getByRole('button', { name: 'Load' }).click();
const response = await responsePromise;
expect(response.status()).toBe(200);
```

### Waiting for a Specific Condition

```typescript
// Wait for a function to return true
await page.waitForFunction(() => {
  return document.querySelectorAll('.item').length > 5;
});
```

### Waiting for Load State

```typescript
// Wait for all network requests to finish
await page.waitForLoadState('networkidle');
```

## The Anti-Pattern: waitForTimeout

```typescript
// NEVER DO THIS
await page.waitForTimeout(2000);  // Arbitrary sleep

// Why it's bad:
// - Too short → flaky (fails when server is slow)
// - Too long → slow (wastes time when server is fast)
// - Hides the real problem (what are you actually waiting for?)
```

If you find yourself reaching for `waitForTimeout`, ask: "What condition am I actually waiting for?" Then use a web-first assertion or `waitForResponse`/`waitForURL` instead.

## Real Example: Async Form Submission

```typescript
test('submit form and verify success', async ({ page }) => {
  await page.goto('/projects/new');
  
  // Fill the form
  await page.getByLabel('Name').fill('New Project');
  await page.getByLabel('Description').fill('A test project');
  await page.getByRole('combobox', { name: 'Team' }).selectOption('engineering');
  
  // Submit — this triggers an API call
  await page.getByRole('button', { name: 'Create Project' }).click();
  
  // The button might show a loading state
  await expect(page.getByRole('button', { name: 'Creating...' })).toBeVisible();
  
  // Wait for success — the page redirects or shows a message
  await expect(page.getByText('Project created successfully')).toBeVisible();
  
  // Verify we're on the new project page
  await expect(page).toHaveURL(/projects\/[\w-]+/);
  await expect(page.getByRole('heading', { name: 'New Project' })).toBeVisible();
});
```

No sleeps. No explicit waits. Each assertion retries until the condition is met. If the API takes 100ms or 3000ms, the test adapts automatically.

## Dana's Question

Dana: "So the tests never have timing issues?"

You: "Almost never. Playwright waits for elements to be ready before interacting, and assertions retry automatically. The only time you need explicit waits is for things Playwright can't infer — like waiting for a specific network request to complete."

Dana: "What about forms? We have some complex ones — multi-step wizards, file uploads, date pickers."

You: "That's next."

## What You Learned

- **Auto-waiting** — every action waits for the element to be actionable
- **Actionability** — visible, stable, enabled, receives events
- **Web-first assertions** — retry automatically until condition is met or timeout
- **Negation** — `not.toBeVisible()` waits for element to disappear
- **Timeouts** — configurable per-assertion and globally
- **waitForURL/waitForResponse** — for navigation and network events
- **Anti-pattern** — never use `waitForTimeout` (arbitrary sleeps)

Auto-waiting eliminates the #1 source of test flakiness. Your tests adapt to any server speed without explicit sleeps. Next: handling complex form interactions.

---

[← Chapter 2: Locators](chapter-02-locators.md) | [Chapter 4: Forms and Inputs →](chapter-04-forms-inputs.md)
