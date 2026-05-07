# Chapter 6: Page Object Model

[← Chapter 5: Authentication](chapter-05-authentication.md) | [Chapter 7: Network Interception →](chapter-07-network-interception.md)

---

## The Problem

Your test suite has 50 tests. The project list page appears in 20 of them. When the team renames the "New Project" button to "Create Project", you update 20 tests. When they move the search bar, another 15 tests break.

Marcus: "I told you. The maintenance burden grows until nobody wants to touch the tests."

He's right — if every test directly references page elements, a single UI change cascades across the entire suite. You need an abstraction layer.

## The Page Object Model (POM)

A Page Object encapsulates all interactions with a specific page. Tests call methods on the page object instead of directly manipulating locators.

```typescript
// pages/ProjectListPage.ts
import { Page, Locator, expect } from '@playwright/test';

export class ProjectListPage {
  readonly page: Page;
  readonly newProjectButton: Locator;
  readonly searchInput: Locator;
  readonly projectCards: Locator;

  constructor(page: Page) {
    this.page = page;
    this.newProjectButton = page.getByRole('button', { name: 'New Project' });
    this.searchInput = page.getByPlaceholder('Search projects...');
    this.projectCards = page.locator('[data-testid="project-card"]');
  }

  async goto() {
    await this.page.goto('/projects');
    await expect(this.page).toHaveURL(/projects/);
  }

  async createProject(name: string) {
    await this.newProjectButton.click();
    await this.page.getByLabel('Project name').fill(name);
    await this.page.getByRole('button', { name: 'Create' }).click();
  }

  async search(query: string) {
    await this.searchInput.fill(query);
  }

  async getProjectCount() {
    return await this.projectCards.count();
  }

  async expectProjectVisible(name: string) {
    await expect(this.page.getByText(name)).toBeVisible();
  }

  async expectProjectCount(count: number) {
    await expect(this.projectCards).toHaveCount(count);
  }
}
```

## Using Page Objects in Tests

```typescript
// tests/projects.spec.ts
import { test, expect } from '@playwright/test';
import { ProjectListPage } from '../pages/ProjectListPage';

test('create a new project', async ({ page }) => {
  const projectList = new ProjectListPage(page);
  await projectList.goto();
  await projectList.createProject('Q4 Launch');
  await projectList.expectProjectVisible('Q4 Launch');
});

test('search filters projects', async ({ page }) => {
  const projectList = new ProjectListPage(page);
  await projectList.goto();
  await projectList.search('Launch');
  await projectList.expectProjectVisible('Q4 Launch');
});
```

Now if the button text changes from "New Project" to "Create Project", you update one line in `ProjectListPage.ts` — not 20 tests.

## Multiple Page Objects

```typescript
// pages/LoginPage.ts
export class LoginPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.page.getByLabel('Email').fill(email);
    await this.page.getByLabel('Password').fill(password);
    await this.page.getByRole('button', { name: 'Sign in' }).click();
  }

  async expectError(message: string) {
    await expect(this.page.getByRole('alert')).toContainText(message);
  }
}

// pages/DashboardPage.ts
export class DashboardPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async expectWelcomeMessage(name: string) {
    await expect(this.page.getByRole('heading')).toContainText(`Welcome, ${name}`);
  }

  async navigateToProjects() {
    await this.page.getByRole('link', { name: 'Projects' }).click();
    return new ProjectListPage(this.page);
  }

  async getNotificationCount() {
    const badge = this.page.locator('[data-testid="notification-badge"]');
    const text = await badge.textContent();
    return parseInt(text || '0');
  }
}
```

## Page Objects as Fixtures

For cleaner test code, expose page objects as fixtures:

```typescript
// tests/fixtures.ts
import { test as base } from '@playwright/test';
import { ProjectListPage } from '../pages/ProjectListPage';
import { DashboardPage } from '../pages/DashboardPage';

type Pages = {
  projectListPage: ProjectListPage;
  dashboardPage: DashboardPage;
};

export const test = base.extend<Pages>({
  projectListPage: async ({ page }, use) => {
    await use(new ProjectListPage(page));
  },
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
});

export { expect } from '@playwright/test';
```

```typescript
// tests/projects.spec.ts
import { test, expect } from './fixtures';

test('create project from dashboard', async ({ dashboardPage, projectListPage }) => {
  await dashboardPage.page.goto('/dashboard');
  const projects = await dashboardPage.navigateToProjects();
  await projects.createProject('New Feature');
  await projects.expectProjectVisible('New Feature');
});
```

## Component-Level Page Objects

Not every page object represents a full page. Reusable components get their own objects:

```typescript
// components/NavigationBar.ts
export class NavigationBar {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async navigateTo(section: string) {
    await this.page.getByRole('navigation').getByRole('link', { name: section }).click();
  }

  async openUserMenu() {
    await this.page.getByRole('button', { name: 'User menu' }).click();
  }

  async logout() {
    await this.openUserMenu();
    await this.page.getByRole('menuitem', { name: 'Sign out' }).click();
  }

  async expectCurrentSection(section: string) {
    await expect(
      this.page.getByRole('navigation').getByRole('link', { name: section })
    ).toHaveAttribute('aria-current', 'page');
  }
}

// components/ConfirmDialog.ts
export class ConfirmDialog {
  readonly page: Page;
  readonly dialog: Locator;

  constructor(page: Page) {
    this.page = page;
    this.dialog = page.getByRole('dialog');
  }

  async confirm() {
    await this.dialog.getByRole('button', { name: 'Confirm' }).click();
  }

  async cancel() {
    await this.dialog.getByRole('button', { name: 'Cancel' }).click();
  }

  async expectMessage(text: string) {
    await expect(this.dialog).toContainText(text);
  }
}
```

## POM Best Practices

### DO: Expose meaningful actions

```typescript
// Good: describes user intent
async createProject(name: string, team?: string) { ... }
async archiveProject(name: string) { ... }
async inviteMember(email: string, role: string) { ... }
```

### DON'T: Expose raw locators for tests to manipulate

```typescript
// Bad: leaks implementation details
getSubmitButton() { return this.page.locator('.btn-submit'); }
```

### DO: Include assertions in page objects

```typescript
// Good: encapsulates what "success" looks like
async expectProjectCreated(name: string) {
  await expect(this.page.getByText(`${name} created`)).toBeVisible();
  await expect(this.page).toHaveURL(/projects/);
}
```

### DON'T: Put test logic in page objects

```typescript
// Bad: page objects shouldn't decide what to test
async testProjectCreation() {  // This is a test, not a page action
  await this.createProject('test');
  await this.expectProjectCreated('test');
}
```

### DO: Return new page objects for navigation

```typescript
async clickCreateProject(): Promise<ProjectFormPage> {
  await this.newProjectButton.click();
  return new ProjectFormPage(this.page);
}
```

## Project Structure

```
shipfast-tests/
├── tests/
│   ├── auth.setup.ts
│   ├── fixtures.ts
│   ├── projects.spec.ts
│   ├── tasks.spec.ts
│   └── billing.spec.ts
├── pages/
│   ├── LoginPage.ts
│   ├── DashboardPage.ts
│   ├── ProjectListPage.ts
│   ├── ProjectFormPage.ts
│   └── TaskBoardPage.ts
├── components/
│   ├── NavigationBar.ts
│   ├── ConfirmDialog.ts
│   └── Toast.ts
├── playwright.config.ts
└── package.json
```

## What You Learned

- **Page Object Model** — encapsulate page interactions in classes
- **Single responsibility** — one class per page/component
- **Meaningful methods** — `createProject()` not `clickButton()`
- **Assertions in POM** — `expectProjectVisible()` encapsulates verification
- **Fixtures** — expose page objects as test fixtures for cleaner code
- **Component objects** — reusable UI components (nav, dialogs, toasts)
- **Maintenance** — UI changes update one file, not dozens of tests

Your tests are organized and maintainable. But they only test the happy path — what happens when the API returns an error? When the network is slow? When the server is down? The next chapter shows how to intercept and mock network requests.

---

[← Chapter 5: Authentication](chapter-05-authentication.md) | [Chapter 7: Network Interception →](chapter-07-network-interception.md)
