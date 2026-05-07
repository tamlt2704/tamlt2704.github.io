# Chapter 2: Locators

[← Chapter 1: Your First Test](chapter-01-first-test.md) | [Chapter 3: Auto-Waiting →](chapter-03-auto-waiting.md)

---

## The Problem

Your login test works. Then the frontend team refactors the login page. They change `<input id="username">` to `<input name="email" class="auth-input-field">`. Your test breaks.

Marcus (QA): "This is why I don't trust automation. Every time the UI changes, all the tests break. I've seen it happen with Selenium — a 500-test suite that nobody maintains because half the tests are broken."

He's right. If your tests are coupled to implementation details (CSS classes, IDs, DOM structure), they'll break constantly. You need selectors that are resilient to refactoring.

## The Locator Priority

Playwright recommends locators in this order (most resilient to least):

1. **Role-based** — `getByRole('button', { name: 'Submit' })`
2. **Label-based** — `getByLabel('Email')`
3. **Placeholder-based** — `getByPlaceholder('Enter your email')`
4. **Text-based** — `getByText('Welcome back')`
5. **Test ID** — `getByTestId('login-form')`
6. **CSS/XPath** — `locator('#username')` (last resort)

The higher on the list, the more your tests reflect how users actually find elements — and the less they break when implementation changes.

## Role-Based Locators

Users don't think "click the element with class `btn-primary`." They think "click the Submit button." Role-based locators match this mental model:

```typescript
test('role-based locators', async ({ page }) => {
  await page.goto('https://the-internet.herokuapp.com/login');
  
  // Find by ARIA role and accessible name
  await page.getByRole('heading', { name: 'Login Page' }).isVisible();
  await page.getByRole('textbox', { name: 'Username' }).fill('tomsmith');
  await page.getByRole('button', { name: 'Login' }).click();
  
  // Links
  await page.getByRole('link', { name: 'Elemental Selenium' });
  
  // Common roles: button, textbox, heading, link, checkbox, 
  //               radio, combobox, listbox, tab, dialog
});
```

### Why Roles Are Best

- They test accessibility (if the role is wrong, your app has an a11y bug)
- They survive CSS refactors (class names change, roles don't)
- They survive DOM restructuring (nesting changes, roles don't)
- They match how screen readers navigate the page

```typescript
// These all find the same button, but role-based is most resilient:
page.getByRole('button', { name: 'Submit' });  // ✓ Best
page.locator('button:has-text("Submit")');      // OK
page.locator('.btn-submit');                     // Fragile
page.locator('#submit-btn');                     // Fragile
page.locator('form > div:nth-child(3) > button'); // Terrible
```

## Label-Based Locators

For form inputs, `getByLabel` finds the input associated with a `<label>`:

```typescript
test('label-based locators', async ({ page }) => {
  // <label for="email">Email address</label>
  // <input id="email" type="email" />
  await page.getByLabel('Email address').fill('user@test.com');
  
  // <label>
  //   Password
  //   <input type="password" />
  // </label>
  await page.getByLabel('Password').fill('secret123');
  
  // Checkboxes
  await page.getByLabel('Remember me').check();
});
```

This works regardless of the input's ID, class, or position in the DOM. If the label text stays the same, the test works.

## Text-Based Locators

Find elements by their visible text:

```typescript
test('text-based locators', async ({ page }) => {
  // Exact text
  await page.getByText('Welcome back');
  
  // Partial text (substring)
  await page.getByText('Welcome', { exact: false });
  
  // Regex
  await page.getByText(/welcome/i);
  
  // Headings specifically
  await page.getByRole('heading', { name: 'Dashboard' });
});
```

## Placeholder-Based Locators

```typescript
test('placeholder locators', async ({ page }) => {
  // <input placeholder="Search projects..." />
  await page.getByPlaceholder('Search projects...').fill('my project');
  
  // Partial match
  await page.getByPlaceholder(/search/i).fill('query');
});
```

## Test IDs: The Escape Hatch

When no semantic locator works (no label, no role, no unique text), use test IDs:

```html
<!-- In your app's HTML -->
<div data-testid="project-card-123" class="card">...</div>
```

```typescript
test('test ID locators', async ({ page }) => {
  await page.getByTestId('project-card-123').click();
  await page.getByTestId('delete-confirmation').getByRole('button', { name: 'Confirm' }).click();
});
```

Test IDs are:
- Stable (developers know not to change them)
- Explicit (clearly exist for testing)
- Not tied to styling or structure

Configure the test ID attribute in `playwright.config.ts`:

```typescript
export default defineConfig({
  use: {
    testIdAttribute: 'data-testid', // default
    // or 'data-test', 'data-cy', etc.
  },
});
```

## CSS and XPath (Last Resort)

When nothing else works:

```typescript
test('css and xpath', async ({ page }) => {
  // CSS selector
  await page.locator('.project-list > .card:first-child').click();
  await page.locator('[data-status="active"]').click();
  
  // XPath
  await page.locator('xpath=//button[contains(text(), "Submit")]').click();
  
  // Combining CSS with text
  await page.locator('button:has-text("Submit")').click();
  await page.locator('.card:has-text("My Project")').click();
});
```

## Filtering and Chaining Locators

Locators can be narrowed down:

```typescript
test('filtering locators', async ({ page }) => {
  // Filter by text
  const activeCard = page.locator('.card').filter({ hasText: 'Active' });
  await activeCard.click();
  
  // Filter by child element
  const cardWithButton = page.locator('.card').filter({
    has: page.getByRole('button', { name: 'Edit' })
  });
  await cardWithButton.click();
  
  // Chain locators (scope within parent)
  const sidebar = page.locator('.sidebar');
  await sidebar.getByRole('link', { name: 'Settings' }).click();
  
  // Nth element
  await page.locator('.card').nth(0).click();  // First card
  await page.locator('.card').first().click(); // Same thing
  await page.locator('.card').last().click();  // Last card
});
```

## The Locator Codegen Tool

Don't guess selectors. Let Playwright generate them:

```bash
npx playwright codegen https://the-internet.herokuapp.com/login
```

This opens a browser and a code generator. Click on elements, and Playwright writes the locator code for you — using the best available strategy (role > label > test ID > CSS).

## Rewriting the Login Test

Before (fragile):
```typescript
test('login - fragile', async ({ page }) => {
  await page.goto('/login');
  await page.locator('#username').fill('tomsmith');
  await page.locator('#password').fill('SuperSecretPassword!');
  await page.locator('button[type="submit"]').click();
  await expect(page.locator('.flash.success')).toBeVisible();
});
```

After (resilient):
```typescript
test('login - resilient', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Username').fill('tomsmith');
  await page.getByLabel('Password').fill('SuperSecretPassword!');
  await page.getByRole('button', { name: 'Login' }).click();
  await expect(page.getByText('You logged into a secure area')).toBeVisible();
});
```

The second version survives:
- Changing the input's ID or class
- Restructuring the form's HTML
- Changing the button's CSS class
- Moving elements around in the DOM

It only breaks if the *user-visible* text changes — which is a real product change that should probably update the test anyway.

## Strictness: Locators Must Match Exactly One Element

```typescript
// If multiple buttons match, Playwright throws an error:
await page.getByRole('button').click();
// Error: locator.click: Error: strict mode violation:
//   getByRole('button') resolved to 5 elements

// Fix: be more specific
await page.getByRole('button', { name: 'Submit' }).click();
```

This strictness prevents accidentally clicking the wrong element. If your locator is ambiguous, Playwright tells you immediately.

## Marcus Changes His Mind

You show Marcus the refactored tests using role-based locators.

Marcus: "So if I change the CSS class on the login button, the test still passes?"

You: "Yes. It finds the button by its accessible name, not its class."

Marcus: "And if I add a new button to the page?"

You: "As long as there's only one button named 'Login', it still works. If there are two, Playwright throws an error immediately — it won't silently click the wrong one."

Marcus: "That's... actually better than what I expected."

## What You Learned

- **Locator priority** — role > label > placeholder > text > test ID > CSS
- **Role-based** — `getByRole('button', { name: 'Submit' })` — most resilient
- **Label-based** — `getByLabel('Email')` — great for form inputs
- **Test IDs** — `getByTestId('card')` — explicit escape hatch
- **Filtering** — `.filter({ hasText: '...' })` to narrow results
- **Chaining** — scope locators within parent elements
- **Strictness** — locators must match exactly one element (no silent ambiguity)
- **Codegen** — `npx playwright codegen` generates locators for you

Your tests are now resilient to UI refactoring. But there's still a timing problem: what happens when you click a button and the result takes 500ms to appear? The next chapter explains Playwright's auto-waiting mechanism.

---

[← Chapter 1: Your First Test](chapter-01-first-test.md) | [Chapter 3: Auto-Waiting →](chapter-03-auto-waiting.md)
