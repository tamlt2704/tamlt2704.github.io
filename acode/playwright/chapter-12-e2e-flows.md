# Chapter 12: End-to-End Flows

[← Chapter 11: Visual Testing](chapter-11-visual-testing.md)

---

## The Problem

You have tests for individual pages. Login works. Project creation works. Task management works. But does the *entire flow* work? Can a user sign up, create a project, invite a teammate, create tasks, drag them across the board, and export a report — all in one session?

Dana: "Last week, project creation worked fine in isolation. But when you created a project right after signing up, it failed because the onboarding modal blocked the button. No individual test caught it."

End-to-end flows test the complete user journey — multiple pages, multiple features, real data flowing through the system.

## API Testing with Playwright

Playwright isn't just for browsers. It can test APIs directly:

```typescript
import { test, expect } from '@playwright/test';

test('API: create and retrieve project', async ({ request }) => {
  // Create a project via API
  const createResponse = await request.post('/api/projects', {
    data: {
      name: 'API Test Project',
      description: 'Created via API',
    },
  });
  expect(createResponse.ok()).toBeTruthy();
  
  const project = await createResponse.json();
  expect(project.id).toBeDefined();
  expect(project.name).toBe('API Test Project');
  
  // Retrieve it
  const getResponse = await request.get(`/api/projects/${project.id}`);
  expect(getResponse.ok()).toBeTruthy();
  
  const retrieved = await getResponse.json();
  expect(retrieved.name).toBe('API Test Project');
  
  // Clean up
  const deleteResponse = await request.delete(`/api/projects/${project.id}`);
  expect(deleteResponse.ok()).toBeTruthy();
});
```

## Database Seeding

For reliable E2E tests, start with known data:

```typescript
// tests/fixtures.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  // Seed database before each test
  seedData: [async ({ request }, use) => {
    // Create test data via API
    const project = await request.post('/api/test/seed', {
      data: {
        projects: [
          { name: 'Test Project', tasks: ['Task 1', 'Task 2', 'Task 3'] },
        ],
        users: [
          { email: 'alice@test.com', role: 'admin' },
          { email: 'bob@test.com', role: 'member' },
        ],
      },
    });
    
    const data = await project.json();
    await use(data);
    
    // Cleanup after test
    await request.post('/api/test/cleanup', { data: { ids: data.ids } });
  }, { auto: true }],
});
```

## The Complete User Journey

```typescript
test.describe('Complete project lifecycle', () => {
  test('create project → add tasks → complete → archive', async ({ page }) => {
    // 1. Navigate to projects
    await page.goto('/projects');
    
    // 2. Create a new project
    await page.getByRole('button', { name: 'New Project' }).click();
    await page.getByLabel('Project name').fill('Q1 Sprint');
    await page.getByLabel('Description').fill('First quarter deliverables');
    await page.getByRole('button', { name: 'Create' }).click();
    
    await expect(page).toHaveURL(/projects\/[\w-]+/);
    await expect(page.getByRole('heading', { name: 'Q1 Sprint' })).toBeVisible();
    
    // 3. Add tasks
    await page.getByRole('button', { name: 'Add Task' }).click();
    await page.getByLabel('Task title').fill('Design mockups');
    await page.getByRole('button', { name: 'Save' }).click();
    await expect(page.getByText('Design mockups')).toBeVisible();
    
    await page.getByRole('button', { name: 'Add Task' }).click();
    await page.getByLabel('Task title').fill('Implement API');
    await page.getByRole('button', { name: 'Save' }).click();
    await expect(page.getByText('Implement API')).toBeVisible();
    
    // 4. Complete a task
    await page.getByText('Design mockups').click();
    await page.getByRole('button', { name: 'Mark Complete' }).click();
    await expect(page.getByText('Design mockups')).toHaveCSS('text-decoration-line', 'line-through');
    
    // 5. Verify progress
    await expect(page.getByText('1 of 2 tasks complete')).toBeVisible();
    
    // 6. Archive the project
    await page.getByRole('button', { name: 'Project settings' }).click();
    await page.getByRole('button', { name: 'Archive' }).click();
    await page.getByRole('dialog').getByRole('button', { name: 'Confirm' }).click();
    
    await expect(page.getByText('Project archived')).toBeVisible();
    await expect(page).toHaveURL(/projects/);
  });
});
```

## Multi-User Flows

Test collaboration by using multiple browser contexts:

```typescript
test('real-time collaboration', async ({ browser }) => {
  // Create two separate browser contexts (two users)
  const aliceContext = await browser.newContext({
    storageState: 'playwright/.auth/alice.json',
  });
  const bobContext = await browser.newContext({
    storageState: 'playwright/.auth/bob.json',
  });
  
  const alicePage = await aliceContext.newPage();
  const bobPage = await bobContext.newPage();
  
  // Both open the same project
  await alicePage.goto('/projects/shared-project');
  await bobPage.goto('/projects/shared-project');
  
  // Alice creates a task
  await alicePage.getByRole('button', { name: 'Add Task' }).click();
  await alicePage.getByLabel('Task title').fill('Alice task');
  await alicePage.getByRole('button', { name: 'Save' }).click();
  
  // Bob should see it appear in real-time
  await expect(bobPage.getByText('Alice task')).toBeVisible({ timeout: 10000 });
  
  // Cleanup
  await aliceContext.close();
  await bobContext.close();
});
```

## Billing Flow (With Mocked Payment)

```typescript
test('upgrade to pro plan', async ({ page }) => {
  // Mock Stripe to avoid real charges
  await page.route('**/v1/payment_intents', (route) => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({
        id: 'pi_test_123',
        status: 'succeeded',
        client_secret: 'pi_test_123_secret',
      }),
    });
  });
  
  await page.route('**/v1/payment_methods', (route) => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({
        id: 'pm_test_456',
        card: { brand: 'visa', last4: '4242' },
      }),
    });
  });
  
  // Navigate to billing
  await page.goto('/settings/billing');
  await page.getByRole('button', { name: 'Upgrade to Pro' }).click();
  
  // Fill payment form (in iframe)
  const stripeFrame = page.frameLocator('iframe[name*="stripe"]');
  await stripeFrame.getByPlaceholder('Card number').fill('4242424242424242');
  await stripeFrame.getByPlaceholder('MM / YY').fill('12/28');
  await stripeFrame.getByPlaceholder('CVC').fill('123');
  
  await page.getByRole('button', { name: 'Subscribe' }).click();
  
  // Verify upgrade
  await expect(page.getByText('Pro Plan')).toBeVisible();
  await expect(page.getByText('$29/month')).toBeVisible();
});
```

## Email Verification Flow

```typescript
test('signup with email verification', async ({ page, request }) => {
  // Sign up
  await page.goto('/signup');
  await page.getByLabel('Email').fill('newuser@test.com');
  await page.getByLabel('Password').fill('SecurePass123!');
  await page.getByRole('button', { name: 'Sign Up' }).click();
  
  await expect(page.getByText('Check your email')).toBeVisible();
  
  // Get verification link from test email API
  const emailResponse = await request.get('/api/test/emails/newuser@test.com');
  const emails = await emailResponse.json();
  const verifyLink = emails[0].body.match(/href="([^"]+verify[^"]+)"/)[1];
  
  // Click verification link
  await page.goto(verifyLink);
  await expect(page.getByText('Email verified')).toBeVisible();
  await expect(page).toHaveURL(/dashboard/);
});
```

## Test Data Isolation

Each test should be independent. Strategies:

### 1. Unique Data Per Test

```typescript
test('create project with unique name', async ({ page }) => {
  const projectName = `Test Project ${Date.now()}`;
  
  await page.goto('/projects/new');
  await page.getByLabel('Name').fill(projectName);
  await page.getByRole('button', { name: 'Create' }).click();
  
  await expect(page.getByRole('heading', { name: projectName })).toBeVisible();
});
```

### 2. API Cleanup in afterEach

```typescript
test.afterEach(async ({ request }) => {
  // Delete all test projects
  await request.delete('/api/test/cleanup');
});
```

### 3. Database Transactions (Rollback)

```typescript
// If your test API supports it:
test.beforeEach(async ({ request }) => {
  await request.post('/api/test/begin-transaction');
});

test.afterEach(async ({ request }) => {
  await request.post('/api/test/rollback-transaction');
});
```

## Smoke Tests: The Critical Path

A minimal set of tests that verify the app is functional:

```typescript
// tests/smoke.spec.ts
test.describe('Smoke tests', { tag: '@smoke' }, () => {
  test('app loads', async ({ page }) => {
    const response = await page.goto('/');
    expect(response?.ok()).toBeTruthy();
  });

  test('user can log in', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('user@test.com');
    await page.getByLabel('Password').fill('password');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page).toHaveURL(/dashboard/);
  });

  test('user can create a project', async ({ page }) => {
    await page.goto('/projects/new');
    await page.getByLabel('Name').fill(`Smoke ${Date.now()}`);
    await page.getByRole('button', { name: 'Create' }).click();
    await expect(page.getByText('Project created')).toBeVisible();
  });

  test('user can create a task', async ({ page }) => {
    await page.goto('/projects');
    await page.locator('[data-testid="project-card"]').first().click();
    await page.getByRole('button', { name: 'Add Task' }).click();
    await page.getByLabel('Title').fill('Smoke test task');
    await page.getByRole('button', { name: 'Save' }).click();
    await expect(page.getByText('Smoke test task')).toBeVisible();
  });
});
```

Run smoke tests on every deploy:

```bash
npx playwright test --grep @smoke
```

## The Final Test Suite Structure

```
tests/
├── auth.setup.ts              # Authentication setup
├── fixtures.ts                # Custom fixtures
├── smoke.spec.ts              # Critical path (run on every deploy)
├── auth/
│   ├── login.spec.ts          # Login flows
│   ├── signup.spec.ts         # Registration
│   └── password-reset.spec.ts # Password recovery
├── projects/
│   ├── create.spec.ts         # Project CRUD
│   ├── settings.spec.ts       # Project settings
│   └── archive.spec.ts       # Archiving
├── tasks/
│   ├── board.spec.ts          # Task board interactions
│   ├── create.spec.ts         # Task creation
│   └── drag-drop.spec.ts     # Drag and drop
├── billing/
│   ├── upgrade.spec.ts        # Plan upgrades
│   └── invoices.spec.ts      # Invoice history
├── collaboration/
│   └── realtime.spec.ts       # Multi-user features
└── visual/
    ├── dashboard.spec.ts      # Visual regression
    └── components.spec.ts     # Component screenshots
```

## Dana's Final Review

Dana reviews the test suite after two weeks:

"We have 87 tests covering login, project management, task boards, billing, and collaboration. They run in 4 minutes on CI. They've already caught 3 regressions that would have shipped to production."

Marcus: "I'm... impressed. The tests are readable. They don't break every time we change a CSS class. And when they do fail, the trace viewer shows exactly what went wrong."

You: "The key was building it right from the start — resilient locators, proper waiting, page objects, network mocking, and good CI configuration. The tests describe what users do, not how the DOM is structured."

Dana: "Roll it out to the whole team."

## What You Learned

- **API testing** — `request.post/get/delete` for backend verification
- **Database seeding** — create known state before tests
- **Complete flows** — test entire user journeys across multiple pages
- **Multi-user** — separate browser contexts for collaboration testing
- **Payment mocking** — intercept Stripe/payment APIs for billing tests
- **Email flows** — test verification via test email APIs
- **Data isolation** — unique names, cleanup hooks, transactions
- **Smoke tests** — minimal critical-path tests for every deploy
- **Suite organization** — by feature, with shared fixtures and page objects

## The Complete Playwright Toolkit

| Chapter | Problem | Solution |
|---|---|---|
| 1 | Verify the app works | First test, navigation, assertions |
| 2 | Selectors break on refactor | Role-based locators, test IDs |
| 3 | Timing issues | Auto-waiting, web-first assertions |
| 4 | Complex form interactions | fill, check, select, upload, keyboard |
| 5 | Repetitive login | Storage state, global setup |
| 6 | Unmaintainable tests | Page Object Model |
| 7 | Can't test error states | Network interception, mocking |
| 8 | Fails in CI | Config, retries, parallelism, sharding |
| 9 | Can't debug failures | Traces, UI mode, inspector, screenshots |
| 10 | Complex UI interactions | Drag-drop, modals, multi-tab, iframes |
| 11 | CSS regressions | Visual screenshot comparison |
| 12 | Integration gaps | Full E2E flows, API testing, multi-user |

You started with a manual QA process that took 3 days. You end with an automated suite that runs in 4 minutes, catches regressions before they ship, and gives developers confidence to deploy on Friday.

That's Playwright.

---

[← Chapter 11: Visual Testing](chapter-11-visual-testing.md)
