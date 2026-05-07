# Chapter 7: Network Interception

[← Chapter 6: Page Object Model](chapter-06-page-objects.md) | [Chapter 8: CI Configuration →](chapter-08-ci-configuration.md)

---

## The Problem

You need to test: "When the API returns a 500 error, the app shows an error message." But you can't make the real API return 500 on demand. You also need to test: "When the project list is empty, the app shows an empty state." But the test database always has projects.

Dana: "We need to test error handling. Last month a 503 from Stripe crashed the billing page because nobody tested that path."

Playwright can intercept any network request and return whatever you want — mock responses, errors, delays, or modified data.

## Route Interception Basics

```typescript
test('show error when API fails', async ({ page }) => {
  // Intercept the API call and return a 500 error
  await page.route('**/api/projects', (route) => {
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal server error' }),
    });
  });
  
  await page.goto('/projects');
  
  // Verify error UI
  await expect(page.getByText('Something went wrong')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
});
```

## Mocking API Responses

```typescript
test('display projects from API', async ({ page }) => {
  // Return fake project data
  await page.route('**/api/projects', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: 'Project Alpha', status: 'active' },
        { id: 2, name: 'Project Beta', status: 'archived' },
      ]),
    });
  });
  
  await page.goto('/projects');
  
  await expect(page.getByText('Project Alpha')).toBeVisible();
  await expect(page.getByText('Project Beta')).toBeVisible();
});

test('empty state when no projects', async ({ page }) => {
  await page.route('**/api/projects', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    });
  });
  
  await page.goto('/projects');
  
  await expect(page.getByText('No projects yet')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Create your first project' })).toBeVisible();
});
```

## Modifying Real Responses

Sometimes you want the real response but with modifications:

```typescript
test('modify API response', async ({ page }) => {
  await page.route('**/api/projects', async (route) => {
    // Get the real response
    const response = await route.fetch();
    const json = await response.json();
    
    // Modify it
    json.push({ id: 999, name: 'Injected Project', status: 'active' });
    
    // Return modified response
    await route.fulfill({
      response,
      body: JSON.stringify(json),
    });
  });
  
  await page.goto('/projects');
  await expect(page.getByText('Injected Project')).toBeVisible();
});
```

## Simulating Network Conditions

```typescript
test('slow network shows loading state', async ({ page }) => {
  await page.route('**/api/projects', async (route) => {
    // Delay the response by 3 seconds
    await new Promise(resolve => setTimeout(resolve, 3000));
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 1, name: 'Project' }]),
    });
  });
  
  await page.goto('/projects');
  
  // Loading state should be visible
  await expect(page.getByText('Loading projects...')).toBeVisible();
  
  // After delay, content appears
  await expect(page.getByText('Project')).toBeVisible({ timeout: 5000 });
  await expect(page.getByText('Loading projects...')).toBeHidden();
});

test('network timeout', async ({ page }) => {
  await page.route('**/api/projects', (route) => {
    route.abort('timedout');
  });
  
  await page.goto('/projects');
  await expect(page.getByText('Network error')).toBeVisible();
});
```

## Intercepting by Method

```typescript
test('intercept POST request', async ({ page }) => {
  await page.route('**/api/projects', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ id: 42, name: 'New Project' }),
      });
    } else {
      route.continue();  // Let GET requests pass through
    }
  });
  
  await page.goto('/projects/new');
  await page.getByLabel('Name').fill('New Project');
  await page.getByRole('button', { name: 'Create' }).click();
  
  await expect(page.getByText('Project created')).toBeVisible();
});
```

## Waiting for and Asserting Requests

```typescript
test('verify request payload', async ({ page }) => {
  // Wait for the POST request
  const requestPromise = page.waitForRequest('**/api/projects');
  
  await page.goto('/projects/new');
  await page.getByLabel('Name').fill('My Project');
  await page.getByLabel('Description').fill('A description');
  await page.getByRole('button', { name: 'Create' }).click();
  
  // Assert the request was sent correctly
  const request = await requestPromise;
  expect(request.method()).toBe('POST');
  
  const body = request.postDataJSON();
  expect(body.name).toBe('My Project');
  expect(body.description).toBe('A description');
});

test('verify response handling', async ({ page }) => {
  const responsePromise = page.waitForResponse('**/api/projects');
  
  await page.goto('/projects');
  
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  
  const data = await response.json();
  expect(data.length).toBeGreaterThan(0);
});
```

## URL Pattern Matching

```typescript
// Exact URL
await page.route('https://api.shipfast.com/v1/projects', handler);

// Glob patterns
await page.route('**/api/projects', handler);           // Any origin
await page.route('**/api/projects/*', handler);         // With ID
await page.route('**/api/projects/*/tasks', handler);   // Nested resource

// Regex
await page.route(/\/api\/projects\/\d+$/, handler);

// Function predicate
await page.route(
  (url) => url.pathname.startsWith('/api/') && url.searchParams.has('page'),
  handler
);
```

## Mocking Third-Party Services

```typescript
test('Stripe payment flow with mock', async ({ page }) => {
  // Mock Stripe's client-side API
  await page.route('**/v1/payment_intents', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'pi_mock_123',
        status: 'succeeded',
        client_secret: 'pi_mock_123_secret_456',
      }),
    });
  });
  
  await page.goto('/billing/upgrade');
  await page.getByRole('button', { name: 'Upgrade to Pro' }).click();
  await expect(page.getByText('Payment successful')).toBeVisible();
});
```

## HAR File Recording and Playback

Record real network traffic and replay it in tests:

```bash
# Record HAR file
npx playwright open --save-har=tests/fixtures/projects.har https://app.shipfast.com/projects
```

```typescript
test('use recorded HAR file', async ({ page }) => {
  // Replay all network requests from the HAR file
  await page.routeFromHAR('tests/fixtures/projects.har', {
    url: '**/api/**',
    update: false,  // Set to true to re-record
  });
  
  await page.goto('/projects');
  await expect(page.getByText('Project Alpha')).toBeVisible();
});
```

HAR files are great for:
- Deterministic tests (same data every time)
- Testing without a backend
- Capturing complex multi-request flows

## Removing Routes

```typescript
test('remove route mid-test', async ({ page }) => {
  // First: mock the API
  await page.route('**/api/projects', (route) => {
    route.fulfill({ status: 200, body: '[]' });
  });
  
  await page.goto('/projects');
  await expect(page.getByText('No projects')).toBeVisible();
  
  // Remove the mock — subsequent requests hit the real API
  await page.unroute('**/api/projects');
  
  await page.reload();
  // Now shows real data
});
```

## What You Learned

- **route()** — intercept requests and return custom responses
- **fulfill()** — return mock data, errors, or modified responses
- **abort()** — simulate network failures
- **continue()** — let requests pass through unchanged
- **Delays** — simulate slow networks to test loading states
- **Request assertions** — verify payloads sent by the app
- **HAR files** — record and replay network traffic
- **URL patterns** — glob, regex, or function predicates

You can now test any error state, edge case, or third-party integration without depending on external services. Next: making tests work reliably in CI.

---

[← Chapter 6: Page Object Model](chapter-06-page-objects.md) | [Chapter 8: CI Configuration →](chapter-08-ci-configuration.md)
