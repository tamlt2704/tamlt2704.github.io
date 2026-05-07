# Chapter 8: CI Configuration

[← Chapter 7: Network Interception](chapter-07-network-interception.md) | [Chapter 9: Debugging →](chapter-09-debugging.md)

---

## The Problem

Tests pass on your machine. They fail in CI. Different timing, different resources, no display server, different browser versions. The classic "works on my machine" problem.

Dana: "The tests need to run on every PR. If they're flaky in CI, developers will ignore them. Then we're back to manual testing."

## The Playwright Config

`playwright.config.ts` is the control center:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  
  // Run tests in parallel
  fullyParallel: true,
  
  // Fail the build on test.only (prevents accidental commits)
  forbidOnly: !!process.env.CI,
  
  // Retry failed tests in CI (not locally)
  retries: process.env.CI ? 2 : 0,
  
  // Limit parallel workers in CI (less resources)
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter
  reporter: process.env.CI 
    ? [['html'], ['github']]  // HTML report + GitHub annotations
    : [['html']],
  
  use: {
    // Base URL for all tests
    baseURL: 'http://localhost:3000',
    
    // Capture trace on first retry (for debugging failures)
    trace: 'on-first-retry',
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video on failure
    video: 'on-first-retry',
  },

  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['setup'],
    },
    // Mobile viewports
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
      dependencies: ['setup'],
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 13'] },
      dependencies: ['setup'],
    },
  ],

  // Start the dev server before tests
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

## GitHub Actions Workflow

`.github/workflows/playwright.yml`:

```yaml
name: Playwright Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      
      - name: Run Playwright tests
        run: npx playwright test
      
      - name: Upload test report
        uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

### Key Points

- `npx playwright install --with-deps` installs browsers AND system dependencies (fonts, libraries)
- Upload the report as an artifact so you can download and view it after failures
- `if: ${{ !cancelled() }}` ensures the report uploads even when tests fail
- `timeout-minutes: 60` prevents runaway tests from burning CI minutes

## Retries: Handling Flakiness

```typescript
export default defineConfig({
  retries: process.env.CI ? 2 : 0,
});
```

With 2 retries, a test gets 3 attempts. If it passes on any attempt, it's marked as "flaky" (not failed). This prevents spurious failures from blocking PRs while still flagging instability.

Per-test retry configuration:

```typescript
// This specific test is known to be flaky
test('WebSocket notification', async ({ page }) => {
  test.info().annotations.push({ type: 'flaky', description: 'WebSocket timing' });
  // ...
});

// Or set retries for a describe block
test.describe('real-time features', () => {
  test.describe.configure({ retries: 3 });
  
  test('live updates', async ({ page }) => { /* ... */ });
});
```

## Parallelism

```typescript
export default defineConfig({
  // Run test files in parallel
  fullyParallel: true,
  
  // Number of parallel workers
  workers: process.env.CI ? 1 : undefined,  // undefined = half of CPU cores
});
```

Tests run in parallel by default. Each test gets its own browser context (isolated cookies, storage, etc.). Tests should not depend on each other's state.

If tests share a database, you might need:

```typescript
// Serial execution for tests that share state
test.describe.configure({ mode: 'serial' });

test.describe('billing flow', () => {
  test('add payment method', async ({ page }) => { /* ... */ });
  test('upgrade plan', async ({ page }) => { /* ... */ });  // Depends on previous
  test('verify invoice', async ({ page }) => { /* ... */ }); // Depends on previous
});
```

## Sharding: Split Across CI Machines

For large test suites, split across multiple CI runners:

```yaml
jobs:
  test:
    strategy:
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    steps:
      - name: Run tests
        run: npx playwright test --shard=${{ matrix.shard }}
```

This runs 4 parallel jobs, each executing 25% of the tests. A 20-minute suite becomes 5 minutes.

## Web Server Configuration

Playwright can start your app before tests:

```typescript
export default defineConfig({
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,  // 2 minutes to start
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
```

- `reuseExistingServer: !process.env.CI` — locally, use your running dev server; in CI, start fresh
- `timeout` — how long to wait for the server to be ready
- Playwright polls the URL until it responds with 200

### Multiple Servers

```typescript
export default defineConfig({
  webServer: [
    {
      command: 'npm run start:frontend',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run start:api',
      url: 'http://localhost:4000/health',
      reuseExistingServer: !process.env.CI,
    },
  ],
});
```

## Environment-Specific Configuration

```typescript
export default defineConfig({
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
  },
});
```

```bash
# Run against staging
BASE_URL=https://staging.shipfast.com npx playwright test

# Run against production (read-only tests)
BASE_URL=https://app.shipfast.com npx playwright test tests/smoke/
```

## Reporters

```typescript
export default defineConfig({
  reporter: [
    // Always generate HTML report
    ['html', { open: 'never' }],
    
    // GitHub annotations (shows errors inline in PR)
    ['github'],
    
    // JUnit XML (for CI tools that parse it)
    ['junit', { outputFile: 'results.xml' }],
    
    // JSON (for custom processing)
    ['json', { outputFile: 'results.json' }],
    
    // List reporter (console output)
    ['list'],
  ],
});
```

## Tagging Tests for Selective Runs

```typescript
// Tag tests
test('critical: user can log in', { tag: '@smoke' }, async ({ page }) => { /* ... */ });
test('user can change avatar', { tag: '@slow' }, async ({ page }) => { /* ... */ });
```

```bash
# Run only smoke tests
npx playwright test --grep @smoke

# Skip slow tests
npx playwright test --grep-invert @slow
```

## What You Learned

- **playwright.config.ts** — central configuration for all test behavior
- **Retries** — handle flakiness without blocking PRs
- **Parallelism** — tests run in parallel with isolated contexts
- **Sharding** — split tests across CI machines for speed
- **Web server** — auto-start your app before tests
- **GitHub Actions** — complete workflow with artifact upload
- **Reporters** — HTML, GitHub annotations, JUnit, JSON
- **Tags** — selectively run subsets of tests

Tests run reliably in CI. But when they fail, you need to figure out why. The next chapter covers Playwright's powerful debugging tools.

---

[← Chapter 7: Network Interception](chapter-07-network-interception.md) | [Chapter 9: Debugging →](chapter-09-debugging.md)
