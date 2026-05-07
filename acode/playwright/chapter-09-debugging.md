# Chapter 9: Debugging

[← Chapter 8: CI Configuration](chapter-08-ci-configuration.md) | [Chapter 10: Advanced Interactions →](chapter-10-advanced-interactions.md)

---

## The Problem

A test fails in CI. The error message says: "Timeout waiting for element to be visible." Which element? Why isn't it visible? Is the page even loaded? Did the API return an error? Is there a JavaScript exception?

Marcus: "When my manual tests fail, I can see the screen. I can open DevTools. I can check the network tab. How do you debug an invisible headless browser?"

Playwright has answers for all of this.

## The Trace Viewer

The most powerful debugging tool. A trace captures everything that happened during a test: screenshots at every step, DOM snapshots, network requests, console logs, and action timelines.

### Enable Traces

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    trace: 'on-first-retry',  // Capture trace when a test is retried
    // Options: 'on', 'off', 'on-first-retry', 'retain-on-failure'
  },
});
```

### View a Trace

```bash
# After a failed test, open the trace
npx playwright show-trace test-results/login-chromium/trace.zip
```

The trace viewer shows:
- **Timeline** — every action with timestamps
- **Screenshots** — before and after each action
- **DOM snapshot** — inspect the page at any point in time
- **Network** — every request/response with timing
- **Console** — all console.log, errors, warnings
- **Source** — the test code with the failing line highlighted

### Record Traces Always (During Development)

```bash
npx playwright test --trace on
```

## UI Mode: Interactive Debugging

```bash
npx playwright test --ui
```

This opens an interactive window where you can:
- See all tests in a tree view
- Run individual tests
- Watch tests execute in real-time
- Step through actions
- Inspect the page at each step
- Filter and search tests

UI mode is the best way to develop new tests — you see exactly what's happening.

## Headed Mode + Slow Motion

```bash
# Watch the browser with a delay between actions
npx playwright test --headed --slowmo=500
```

`--slowmo=500` adds a 500ms pause between every action. You can visually follow what the test is doing.

## The Playwright Inspector (Step Debugging)

```bash
npx playwright test --debug
```

This opens the browser with the Playwright Inspector panel. You can:
- Step through the test one action at a time
- See the locator highlighted on the page
- Modify locators and test them live
- Resume execution

### Debug a Specific Test

```bash
npx playwright test -g "create project" --debug
```

### Pause in Code

```typescript
test('debug this test', async ({ page }) => {
  await page.goto('/projects');
  
  // Pause here — opens inspector
  await page.pause();
  
  // Continue after you click "Resume" in the inspector
  await page.getByRole('button', { name: 'Create' }).click();
});
```

## Screenshots

### On Failure (Automatic)

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
    // Options: 'on', 'off', 'only-on-failure'
  },
});
```

Screenshots are saved in `test-results/` and attached to the HTML report.

### Manual Screenshots

```typescript
test('capture state', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Full page screenshot
  await page.screenshot({ path: 'screenshots/dashboard.png', fullPage: true });
  
  // Element screenshot
  await page.locator('.chart').screenshot({ path: 'screenshots/chart.png' });
});
```

## Video Recording

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    video: 'on-first-retry',
    // Options: 'on', 'off', 'on-first-retry', 'retain-on-failure'
  },
});
```

Videos are saved as WebM files in `test-results/`. They show exactly what happened in the browser — invaluable for debugging timing issues.

## Console and Error Logging

```typescript
test('capture console errors', async ({ page }) => {
  // Listen for console messages
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      console.log(`Browser error: ${msg.text()}`);
    }
  });
  
  // Listen for uncaught exceptions
  page.on('pageerror', (error) => {
    console.log(`Page error: ${error.message}`);
  });
  
  await page.goto('/dashboard');
});
```

### Fail on Console Errors

```typescript
test('no console errors on page load', async ({ page }) => {
  const errors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  
  expect(errors).toHaveLength(0);
});
```

## Debugging Locators

When a locator doesn't find the element:

```typescript
test('debug locator', async ({ page }) => {
  await page.goto('/projects');
  
  // See what the locator resolves to
  const locator = page.getByRole('button', { name: 'Create' });
  console.log(await locator.count());  // 0 = not found
  
  // Try a broader locator to see what's on the page
  const allButtons = page.getByRole('button');
  console.log(await allButtons.count());
  
  // Print all button names
  for (const button of await allButtons.all()) {
    console.log(await button.textContent());
  }
});
```

### The Codegen Approach

When you can't figure out the right locator:

```bash
npx playwright codegen http://localhost:3000/projects
```

Click on the element you want. Playwright shows you the best locator.

## Debugging Network Issues

```typescript
test('debug API calls', async ({ page }) => {
  // Log all requests
  page.on('request', (request) => {
    console.log(`>> ${request.method()} ${request.url()}`);
  });
  
  // Log all responses
  page.on('response', (response) => {
    console.log(`<< ${response.status()} ${response.url()}`);
  });
  
  // Log failed requests
  page.on('requestfailed', (request) => {
    console.log(`FAILED: ${request.url()} - ${request.failure()?.errorText}`);
  });
  
  await page.goto('/dashboard');
});
```

## Common Debugging Scenarios

### "Element not found"

```typescript
// 1. Is the page loaded?
await page.screenshot({ path: 'debug.png' });

// 2. Is the element in the DOM but hidden?
const count = await page.locator('.my-element').count();
console.log(`Found ${count} elements`);

// 3. Is it inside an iframe?
const frame = page.frameLocator('iframe');
await frame.locator('.my-element').click();

// 4. Is it behind a loading state?
await page.waitForLoadState('networkidle');
```

### "Timeout waiting for navigation"

```typescript
// Check if a dialog/popup is blocking
const dialog = page.locator('[role="dialog"]');
if (await dialog.isVisible()) {
  console.log('Dialog is blocking!');
  await dialog.getByRole('button', { name: 'Close' }).click();
}
```

### "Test passes locally, fails in CI"

Common causes:
- **Timing** — CI is slower; increase timeouts or use proper waits
- **Screen size** — CI might use a different viewport; elements are off-screen
- **Fonts** — different fonts affect layout; use `--update-snapshots` for visual tests
- **Network** — CI might not reach external services; mock them

## Annotations for Reports

```typescript
test('important flow', async ({ page }) => {
  // Add context to the report
  test.info().annotations.push({
    type: 'issue',
    description: 'https://github.com/shipfast/app/issues/123',
  });
  
  // Attach extra info on failure
  await test.step('Load dashboard', async () => {
    await page.goto('/dashboard');
  });
  
  await test.step('Create project', async () => {
    await page.getByRole('button', { name: 'New' }).click();
    // Steps show up in the trace and report
  });
});
```

## What You Learned

- **Trace viewer** — full replay of test execution (screenshots, DOM, network, console)
- **UI mode** — interactive test development and debugging
- **Inspector** — step through tests, inspect locators live
- **page.pause()** — breakpoint in test code
- **Screenshots/video** — automatic capture on failure
- **Console logging** — capture browser errors and warnings
- **Network logging** — see all requests and responses
- **Annotations** — add context to test reports

You can now diagnose any test failure. Next: handling complex UI interactions that go beyond simple clicks and fills.

---

[← Chapter 8: CI Configuration](chapter-08-ci-configuration.md) | [Chapter 10: Advanced Interactions →](chapter-10-advanced-interactions.md)
