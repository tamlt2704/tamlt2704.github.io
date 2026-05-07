# Chapter 10: Advanced Interactions

[← Chapter 9: Debugging](chapter-09-debugging.md) | [Chapter 11: Visual Testing →](chapter-11-visual-testing.md)

---

## The Problem

ShipFast's task board has drag-and-drop columns, toast notifications that auto-dismiss, modals that trap focus, keyboard shortcuts, and a real-time collaboration feature that opens tasks in new tabs.

Dana: "The task board is where users spend 80% of their time. If drag-and-drop breaks, we hear about it within minutes."

Simple `click()` and `fill()` won't cut it here.

## Drag and Drop

```typescript
test('drag task to different column', async ({ page }) => {
  await page.goto('/board');
  
  // Drag from "To Do" to "In Progress"
  const task = page.locator('[data-testid="task-card-123"]');
  const targetColumn = page.locator('[data-testid="column-in-progress"]');
  
  await task.dragTo(targetColumn);
  
  // Verify task moved
  await expect(targetColumn.getByText('Fix login bug')).toBeVisible();
});

test('drag to reorder', async ({ page }) => {
  await page.goto('/board');
  
  // Drag task to a specific position
  const task = page.locator('[data-testid="task-5"]');
  const target = page.locator('[data-testid="task-2"]');
  
  await task.dragTo(target);
  
  // Verify order
  const tasks = page.locator('[data-testid^="task-"]');
  await expect(tasks.nth(1)).toContainText('Task 5');
});
```

### Manual Drag (More Control)

```typescript
test('drag with precise control', async ({ page }) => {
  const source = page.locator('[data-testid="task-card"]');
  const target = page.locator('[data-testid="drop-zone"]');
  
  // Get bounding boxes
  const sourceBox = await source.boundingBox();
  const targetBox = await target.boundingBox();
  
  // Manual drag sequence
  await page.mouse.move(sourceBox!.x + sourceBox!.width / 2, 
                         sourceBox!.y + sourceBox!.height / 2);
  await page.mouse.down();
  await page.mouse.move(targetBox!.x + targetBox!.width / 2, 
                         targetBox!.y + targetBox!.height / 2, 
                         { steps: 10 });  // Smooth movement
  await page.mouse.up();
});
```

## Modals and Dialogs

### Browser Dialogs (alert, confirm, prompt)

```typescript
test('handle browser confirm dialog', async ({ page }) => {
  // Set up dialog handler BEFORE triggering it
  page.on('dialog', async (dialog) => {
    expect(dialog.message()).toBe('Are you sure you want to delete?');
    await dialog.accept();  // Click OK
    // or: await dialog.dismiss();  // Click Cancel
  });
  
  await page.getByRole('button', { name: 'Delete' }).click();
  await expect(page.getByText('Item deleted')).toBeVisible();
});

test('handle prompt dialog', async ({ page }) => {
  page.on('dialog', async (dialog) => {
    await dialog.accept('New name');  // Enter text and click OK
  });
  
  await page.getByRole('button', { name: 'Rename' }).click();
});
```

### Custom Modal Components

```typescript
test('modal interaction', async ({ page }) => {
  await page.getByRole('button', { name: 'Delete Project' }).click();
  
  // Wait for modal to appear
  const modal = page.getByRole('dialog');
  await expect(modal).toBeVisible();
  
  // Interact within the modal
  await expect(modal.getByText('This action cannot be undone')).toBeVisible();
  await modal.getByRole('button', { name: 'Confirm Delete' }).click();
  
  // Modal should close
  await expect(modal).toBeHidden();
});

test('close modal with Escape', async ({ page }) => {
  await page.getByRole('button', { name: 'Settings' }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).toBeHidden();
});
```

## Toast Notifications

Toasts appear briefly and auto-dismiss. You need to catch them before they disappear:

```typescript
test('success toast appears after save', async ({ page }) => {
  await page.getByRole('button', { name: 'Save' }).click();
  
  // Toast appears — assert quickly (it auto-dismisses in 3-5 seconds)
  await expect(page.getByRole('alert')).toContainText('Saved successfully');
  
  // Wait for it to disappear
  await expect(page.getByRole('alert')).toBeHidden({ timeout: 10000 });
});

test('error toast on failure', async ({ page }) => {
  // Mock API failure
  await page.route('**/api/save', (route) => route.fulfill({ status: 500 }));
  
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByRole('alert')).toContainText('Failed to save');
});
```

## Multiple Tabs and Windows

```typescript
test('open link in new tab', async ({ page, context }) => {
  await page.goto('/projects');
  
  // Wait for the new page (tab) to open
  const newPagePromise = context.waitForEvent('page');
  await page.getByRole('link', { name: 'View in new tab' }).click();
  const newPage = await newPagePromise;
  
  // Interact with the new tab
  await newPage.waitForLoadState();
  await expect(newPage).toHaveURL(/project-details/);
  await expect(newPage.getByRole('heading')).toContainText('Project Details');
  
  // Switch back to original tab
  await page.bringToFront();
});

test('popup window', async ({ page, context }) => {
  const popupPromise = context.waitForEvent('page');
  await page.getByRole('button', { name: 'Connect GitHub' }).click();
  const popup = await popupPromise;
  
  // Interact with OAuth popup
  await popup.getByRole('button', { name: 'Authorize' }).click();
  
  // Popup closes, back to main page
  await expect(page.getByText('GitHub connected')).toBeVisible();
});
```

## iframes

```typescript
test('interact with iframe content', async ({ page }) => {
  await page.goto('/embed-demo');
  
  // Get the iframe locator
  const frame = page.frameLocator('#payment-iframe');
  
  // Interact with elements inside the iframe
  await frame.getByLabel('Card number').fill('4242424242424242');
  await frame.getByLabel('Expiry').fill('12/25');
  await frame.getByLabel('CVC').fill('123');
  await frame.getByRole('button', { name: 'Pay' }).click();
});

test('nested iframes', async ({ page }) => {
  const outerFrame = page.frameLocator('#outer');
  const innerFrame = outerFrame.frameLocator('#inner');
  await innerFrame.getByRole('button', { name: 'Submit' }).click();
});
```

## Hover and Tooltips

```typescript
test('tooltip appears on hover', async ({ page }) => {
  await page.goto('/dashboard');
  
  await page.getByRole('button', { name: 'Help' }).hover();
  await expect(page.getByRole('tooltip')).toContainText('Click for help');
});

test('dropdown menu on hover', async ({ page }) => {
  await page.locator('.nav-item').hover();
  await expect(page.locator('.dropdown-menu')).toBeVisible();
  await page.locator('.dropdown-menu').getByText('Settings').click();
});
```

## Right-Click (Context Menu)

```typescript
test('context menu', async ({ page }) => {
  await page.goto('/files');
  
  await page.locator('[data-testid="file-item"]').click({ button: 'right' });
  
  await expect(page.locator('.context-menu')).toBeVisible();
  await page.locator('.context-menu').getByText('Rename').click();
});
```

## Keyboard Shortcuts

```typescript
test('keyboard shortcuts', async ({ page }) => {
  await page.goto('/editor');
  
  // Ctrl+S to save
  await page.keyboard.press('Control+s');
  await expect(page.getByText('Saved')).toBeVisible();
  
  // Ctrl+K to open command palette
  await page.keyboard.press('Control+k');
  await expect(page.getByRole('dialog', { name: 'Command palette' })).toBeVisible();
  
  // Type and select
  await page.keyboard.type('create task');
  await page.keyboard.press('Enter');
});

test('multi-select with keyboard', async ({ page }) => {
  await page.goto('/files');
  
  // Click first item
  await page.locator('[data-testid="file-1"]').click();
  
  // Ctrl+click to add to selection
  await page.locator('[data-testid="file-3"]').click({ modifiers: ['Control'] });
  await page.locator('[data-testid="file-5"]').click({ modifiers: ['Control'] });
  
  // Verify 3 items selected
  await expect(page.locator('.selected')).toHaveCount(3);
});
```

## Downloads

```typescript
test('download a file', async ({ page }) => {
  // Wait for the download to start
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Export CSV' }).click();
  const download = await downloadPromise;
  
  // Verify filename
  expect(download.suggestedFilename()).toBe('projects.csv');
  
  // Save to disk and verify contents
  const path = await download.path();
  // Or save to a specific location:
  await download.saveAs('tests/downloads/projects.csv');
});
```

## Clipboard

```typescript
test('copy to clipboard', async ({ page, context }) => {
  // Grant clipboard permission
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  
  await page.goto('/share');
  await page.getByRole('button', { name: 'Copy link' }).click();
  
  // Read clipboard
  const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
  expect(clipboardText).toContain('https://shipfast.com/share/');
});
```

## Geolocation and Permissions

```typescript
test('location-based features', async ({ context, page }) => {
  // Set geolocation
  await context.setGeolocation({ latitude: 37.7749, longitude: -122.4194 });
  await context.grantPermissions(['geolocation']);
  
  await page.goto('/nearby');
  await expect(page.getByText('San Francisco')).toBeVisible();
});
```

## What You Learned

- **Drag and drop** — `dragTo()` or manual mouse control for precision
- **Dialogs** — handle alert/confirm/prompt with `page.on('dialog')`
- **Modals** — `getByRole('dialog')` for custom modal components
- **Toasts** — assert quickly before auto-dismiss
- **Multi-tab** — `context.waitForEvent('page')` for new tabs/popups
- **iframes** — `page.frameLocator()` to interact with embedded content
- **Hover** — `hover()` for tooltips and dropdown menus
- **Keyboard** — shortcuts, modifiers, multi-select
- **Downloads** — `waitForEvent('download')` to capture files
- **Clipboard/Geolocation** — permissions and browser APIs

You can now test any UI interaction. Next: verifying that the app *looks* correct, not just that it functions correctly.

---

[← Chapter 9: Debugging](chapter-09-debugging.md) | [Chapter 11: Visual Testing →](chapter-11-visual-testing.md)
