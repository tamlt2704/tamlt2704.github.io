# Chapter 4: Forms and Inputs

[← Chapter 3: Auto-Waiting](chapter-03-auto-waiting.md) | [Chapter 5: Authentication →](chapter-05-authentication.md)

---

## The Problem

ShipFast's project creation form has: text inputs, a rich text editor, a date picker, file uploads, a multi-select dropdown, and a drag-to-reorder priority list. Your simple `fill()` and `click()` aren't enough.

Dana: "The project creation flow is our most important path. If a user can't create a project, nothing else matters."

## Text Inputs

```typescript
test('text inputs', async ({ page }) => {
  // fill() clears existing text and types new text
  await page.getByLabel('Project name').fill('My Project');
  
  // Verify the value
  await expect(page.getByLabel('Project name')).toHaveValue('My Project');
  
  // Clear an input
  await page.getByLabel('Project name').clear();
  await expect(page.getByLabel('Project name')).toBeEmpty();
  
  // Type character by character (triggers keydown/keyup events)
  // Useful for autocomplete/search inputs
  await page.getByLabel('Search').pressSequentially('playwright', { delay: 100 });
});
```

### fill() vs pressSequentially()

- `fill()` — sets the value directly. Fast. Doesn't trigger individual key events.
- `pressSequentially()` — types each character. Slower. Triggers all keyboard events. Use for autocomplete, search-as-you-type, or inputs that validate on each keystroke.

## Checkboxes and Radio Buttons

```typescript
test('checkboxes', async ({ page }) => {
  // Check
  await page.getByLabel('Send notifications').check();
  await expect(page.getByLabel('Send notifications')).toBeChecked();
  
  // Uncheck
  await page.getByLabel('Send notifications').uncheck();
  await expect(page.getByLabel('Send notifications')).not.toBeChecked();
  
  // setChecked — set to specific state
  await page.getByLabel('Public project').setChecked(true);
  await page.getByLabel('Public project').setChecked(false);
});

test('radio buttons', async ({ page }) => {
  // Radio buttons use check() too
  await page.getByLabel('High priority').check();
  await expect(page.getByLabel('High priority')).toBeChecked();
  await expect(page.getByLabel('Low priority')).not.toBeChecked();
});
```

## Select Dropdowns

```typescript
test('native select', async ({ page }) => {
  // By value
  await page.getByLabel('Country').selectOption('US');
  
  // By label text
  await page.getByLabel('Country').selectOption({ label: 'United States' });
  
  // Multiple selections
  await page.getByLabel('Tags').selectOption(['bug', 'urgent', 'frontend']);
  
  // Verify selection
  await expect(page.getByLabel('Country')).toHaveValue('US');
});
```

### Custom Dropdowns (Non-Native)

Most modern apps use custom dropdown components (React Select, Headless UI, etc.) that aren't native `<select>` elements:

```typescript
test('custom dropdown', async ({ page }) => {
  // Click to open the dropdown
  await page.getByRole('combobox', { name: 'Assignee' }).click();
  
  // Wait for options to appear
  await expect(page.getByRole('listbox')).toBeVisible();
  
  // Click an option
  await page.getByRole('option', { name: 'Alice Johnson' }).click();
  
  // Verify selection
  await expect(page.getByRole('combobox', { name: 'Assignee' })).toHaveText('Alice Johnson');
});

test('searchable dropdown', async ({ page }) => {
  // Click to open
  await page.getByRole('combobox', { name: 'Team' }).click();
  
  // Type to filter
  await page.getByRole('combobox', { name: 'Team' }).fill('eng');
  
  // Select from filtered results
  await page.getByRole('option', { name: 'Engineering' }).click();
});
```

## Date Pickers

```typescript
test('date picker - native input', async ({ page }) => {
  // For native date inputs, fill with ISO format
  await page.getByLabel('Due date').fill('2025-03-15');
  await expect(page.getByLabel('Due date')).toHaveValue('2025-03-15');
});

test('date picker - custom component', async ({ page }) => {
  // Click to open the calendar
  await page.getByLabel('Due date').click();
  
  // Navigate to the right month
  await page.getByRole('button', { name: 'Next month' }).click();
  
  // Click the day
  await page.getByRole('gridcell', { name: '15' }).click();
  
  // Verify
  await expect(page.getByLabel('Due date')).toHaveValue(/March 15/);
});
```

## File Uploads

```typescript
test('single file upload', async ({ page }) => {
  // Standard file input
  await page.getByLabel('Upload avatar').setInputFiles('tests/fixtures/avatar.png');
  
  // Verify upload
  await expect(page.getByText('avatar.png')).toBeVisible();
});

test('multiple file upload', async ({ page }) => {
  await page.getByLabel('Attachments').setInputFiles([
    'tests/fixtures/doc1.pdf',
    'tests/fixtures/doc2.pdf',
  ]);
  
  await expect(page.getByText('doc1.pdf')).toBeVisible();
  await expect(page.getByText('doc2.pdf')).toBeVisible();
});

test('drag and drop file upload', async ({ page }) => {
  // For drag-and-drop zones, use the hidden file input
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('tests/fixtures/report.csv');
});

test('remove uploaded file', async ({ page }) => {
  // Upload then clear
  await page.getByLabel('Avatar').setInputFiles('tests/fixtures/avatar.png');
  await page.getByLabel('Avatar').setInputFiles([]);  // Clear
});
```

### Creating Test Files Programmatically

```typescript
import { test, expect } from '@playwright/test';
import path from 'path';

test('upload with buffer', async ({ page }) => {
  await page.getByLabel('Import data').setInputFiles({
    name: 'data.csv',
    mimeType: 'text/csv',
    buffer: Buffer.from('name,email\nAlice,alice@test.com\nBob,bob@test.com'),
  });
});
```

## Textareas and Rich Text Editors

```typescript
test('textarea', async ({ page }) => {
  await page.getByLabel('Description').fill('This is a multi-line\ndescription');
  await expect(page.getByLabel('Description')).toHaveValue(/multi-line/);
});

test('contenteditable rich text', async ({ page }) => {
  // Rich text editors often use contenteditable divs
  const editor = page.locator('[contenteditable="true"]');
  await editor.click();
  await editor.fill('Bold text here');
  
  // Or type with formatting shortcuts
  await editor.press('Control+a');
  await editor.press('Control+b');  // Bold
  await editor.pressSequentially('Important note');
});
```

## Multi-Step Forms (Wizards)

```typescript
test('multi-step project creation', async ({ page }) => {
  await page.goto('/projects/new');
  
  // Step 1: Basic info
  await page.getByLabel('Project name').fill('Q4 Launch');
  await page.getByLabel('Description').fill('Product launch for Q4');
  await page.getByRole('button', { name: 'Next' }).click();
  
  // Step 2: Team
  await expect(page.getByText('Step 2 of 3')).toBeVisible();
  await page.getByRole('combobox', { name: 'Team' }).click();
  await page.getByRole('option', { name: 'Engineering' }).click();
  await page.getByLabel('Alice Johnson').check();
  await page.getByLabel('Bob Smith').check();
  await page.getByRole('button', { name: 'Next' }).click();
  
  // Step 3: Settings
  await expect(page.getByText('Step 3 of 3')).toBeVisible();
  await page.getByLabel('Public').check();
  await page.getByLabel('Due date').fill('2025-12-31');
  await page.getByRole('button', { name: 'Create Project' }).click();
  
  // Verify success
  await expect(page.getByText('Project created')).toBeVisible();
  await expect(page).toHaveURL(/projects\/[\w-]+/);
});
```

## Form Validation

```typescript
test('shows validation errors', async ({ page }) => {
  await page.goto('/projects/new');
  
  // Submit empty form
  await page.getByRole('button', { name: 'Create' }).click();
  
  // Check validation messages
  await expect(page.getByText('Project name is required')).toBeVisible();
  await expect(page.getByLabel('Project name')).toHaveAttribute('aria-invalid', 'true');
  
  // Fix the error
  await page.getByLabel('Project name').fill('Valid Name');
  
  // Error should disappear
  await expect(page.getByText('Project name is required')).toBeHidden();
});

test('inline validation on blur', async ({ page }) => {
  await page.goto('/signup');
  
  // Type invalid email and tab away
  await page.getByLabel('Email').fill('not-an-email');
  await page.getByLabel('Email').press('Tab');
  
  // Validation error appears
  await expect(page.getByText('Please enter a valid email')).toBeVisible();
  
  // Fix it
  await page.getByLabel('Email').fill('valid@email.com');
  await page.getByLabel('Email').press('Tab');
  
  // Error disappears
  await expect(page.getByText('Please enter a valid email')).toBeHidden();
});
```

## Keyboard Shortcuts

```typescript
test('keyboard interactions', async ({ page }) => {
  // Tab through form fields
  await page.getByLabel('Name').press('Tab');
  await expect(page.getByLabel('Email')).toBeFocused();
  
  // Submit with Enter
  await page.getByLabel('Search').fill('query');
  await page.getByLabel('Search').press('Enter');
  
  // Keyboard shortcuts
  await page.keyboard.press('Control+s');  // Save
  await page.keyboard.press('Escape');     // Close modal
  
  // Hold modifier keys
  await page.keyboard.down('Shift');
  await page.getByText('Item 1').click();
  await page.getByText('Item 5').click();  // Shift+click for range select
  await page.keyboard.up('Shift');
});
```

## What You Learned

- **fill()** — set input value directly (fast, no key events)
- **pressSequentially()** — type character by character (for autocomplete)
- **check()/uncheck()** — checkboxes and radio buttons
- **selectOption()** — native `<select>` elements
- **Custom dropdowns** — click to open, click option (role-based)
- **setInputFiles()** — file uploads (single, multiple, buffer)
- **Date pickers** — native (fill with ISO) or custom (click through calendar)
- **Multi-step forms** — assert step indicators between pages
- **Validation** — verify error messages appear and disappear
- **Keyboard** — Tab, Enter, shortcuts, modifier keys

Forms are covered. But every test so far starts by navigating to the login page and typing credentials. That's slow and repetitive. The next chapter shows how to authenticate once and reuse the session across all tests.

---

[← Chapter 3: Auto-Waiting](chapter-03-auto-waiting.md) | [Chapter 5: Authentication →](chapter-05-authentication.md)
