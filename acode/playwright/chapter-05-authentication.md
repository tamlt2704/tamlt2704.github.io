# Chapter 5: Authentication

[← Chapter 4: Forms and Inputs](chapter-04-forms-inputs.md) | [Chapter 6: Page Object Model →](chapter-06-page-objects.md)

---

## The Problem

You have 30 tests. Every single one starts with:

```typescript
await page.goto('/login');
await page.getByLabel('Email').fill('user@test.com');
await page.getByLabel('Password').fill('password123');
await page.getByRole('button', { name: 'Sign in' }).click();
await expect(page).toHaveURL(/dashboard/);
```

That's 5 seconds per test just for login. 30 tests × 5 seconds = 2.5 minutes wasted on repetitive authentication. And if the login flow changes, you update 30 tests.

Dana: "Can't you log in once and reuse the session?"

Yes. Playwright's **storage state** lets you authenticate once, save the cookies/localStorage, and reuse them across all tests.

## The Strategy: Global Setup

1. Run a setup script that logs in via the browser
2. Save the authenticated state (cookies + localStorage) to a file
3. Every test loads that state — starts already logged in

## Step 1: Create the Auth Setup

Create `tests/auth.setup.ts`:

```typescript
import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Perform login
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  
  // Wait for login to complete
  await expect(page).toHaveURL(/dashboard/);
  
  // Save authentication state
  await page.context().storageState({ path: authFile });
});
```

## Step 2: Configure Projects

In `playwright.config.ts`:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    // Setup project — runs first
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    
    // Tests that need authentication
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],  // Wait for setup to complete
    },
    
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

## Step 3: Add to .gitignore

```
playwright/.auth/
```

The auth state contains session tokens — don't commit it.

## Step 4: Write Tests Without Login

Now every test starts already authenticated:

```typescript
test('create a project', async ({ page }) => {
  // No login needed! Already authenticated via storageState
  await page.goto('/projects/new');
  await page.getByLabel('Name').fill('Test Project');
  await page.getByRole('button', { name: 'Create' }).click();
  await expect(page.getByText('Project created')).toBeVisible();
});
```

## Multiple Roles

ShipFast has admins, regular users, and viewers. Each needs different auth state:

```typescript
// tests/auth.setup.ts
import { test as setup } from '@playwright/test';

const adminFile = 'playwright/.auth/admin.json';
const userFile = 'playwright/.auth/user.json';

setup('authenticate as admin', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('admin@shipfast.com');
  await page.getByLabel('Password').fill('admin-password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/admin/dashboard');
  await page.context().storageState({ path: adminFile });
});

setup('authenticate as user', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@shipfast.com');
  await page.getByLabel('Password').fill('user-password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: userFile });
});
```

Configure projects per role:

```typescript
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'admin-tests',
      testDir: './tests/admin',
      use: { storageState: 'playwright/.auth/admin.json' },
      dependencies: ['setup'],
    },
    {
      name: 'user-tests',
      testDir: './tests/user',
      use: { storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup'],
    },
  ],
});
```

## API-Based Authentication (Faster)

If your app supports API login, skip the browser entirely:

```typescript
setup('authenticate via API', async ({ request }) => {
  const response = await request.post('/api/auth/login', {
    data: {
      email: 'user@test.com',
      password: 'password123',
    },
  });
  
  expect(response.ok()).toBeTruthy();
  
  // Save the response cookies as storage state
  await request.storageState({ path: 'playwright/.auth/user.json' });
});
```

API auth is faster (no browser rendering) and more reliable (no UI to break).

## Tests That Need Fresh Login

Some tests specifically test the login flow itself. These should NOT use stored auth:

```typescript
// tests/login.spec.ts
import { test, expect } from '@playwright/test';

// Override: don't use stored auth for this file
test.use({ storageState: { cookies: [], origins: [] } });

test('login with valid credentials', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/dashboard/);
});

test('login with invalid credentials shows error', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('wrong@test.com');
  await page.getByLabel('Password').fill('wrong');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Invalid credentials')).toBeVisible();
});
```

## Session Expiry

If your session expires during the test run:

```typescript
setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  
  // Verify we're actually logged in before saving
  await expect(page.getByRole('button', { name: 'user@test.com' })).toBeVisible();
  
  await page.context().storageState({ path: authFile });
});
```

For long-running test suites, consider refreshing auth state between test groups.

## Fixtures for Per-Test Authentication

For tests that need a unique user (e.g., testing user-specific data):

```typescript
// tests/fixtures.ts
import { test as base } from '@playwright/test';

type TestFixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<TestFixtures>({
  authenticatedPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: 'playwright/.auth/user.json',
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
});
```

## What You Learned

- **Storage state** — save cookies/localStorage after login, reuse across tests
- **Global setup** — authenticate once before all tests run
- **Dependencies** — `dependencies: ['setup']` ensures auth runs first
- **Multiple roles** — separate auth files for admin, user, viewer
- **API auth** — faster than browser-based login
- **Overriding auth** — `test.use({ storageState: ... })` for login-specific tests
- **Result** — tests start instantly (no 5-second login per test)

Authentication is solved. But your test file is growing — 500 lines of repetitive page interactions. The next chapter introduces the Page Object Model for organizing and reusing test code.

---

[← Chapter 4: Forms and Inputs](chapter-04-forms-inputs.md) | [Chapter 6: Page Object Model →](chapter-06-page-objects.md)
