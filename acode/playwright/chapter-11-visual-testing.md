# Chapter 11: Visual Testing

[← Chapter 10: Advanced Interactions](chapter-10-advanced-interactions.md) | [Chapter 12: End-to-End Flows →](chapter-12-e2e-flows.md)

---

## The Problem

A CSS change breaks the layout of the dashboard. All functional tests pass — buttons still click, text still appears, forms still submit. But the sidebar overlaps the main content, making the app unusable.

Marcus: "Your tests said everything was fine. The app looked like a train wreck."

Functional tests verify behavior. Visual tests verify appearance. You need both.

## Screenshot Comparison

Playwright can compare screenshots against known-good baselines:

```typescript
import { test, expect } from '@playwright/test';

test('dashboard looks correct', async ({ page }) => {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  
  // Compare full page against baseline
  await expect(page).toHaveScreenshot('dashboard.png');
});

test('project card looks correct', async ({ page }) => {
  await page.goto('/projects');
  
  // Compare a specific element
  const card = page.locator('[data-testid="project-card"]').first();
  await expect(card).toHaveScreenshot('project-card.png');
});
```

### First Run: Create Baselines

```bash
npx playwright test --update-snapshots
```

This creates baseline screenshots in `tests/__snapshots__/`. Subsequent runs compare against these baselines.

### When Screenshots Differ

If the screenshot doesn't match the baseline, the test fails and generates:
- `expected.png` — the baseline
- `actual.png` — what the test captured
- `diff.png` — highlighted differences

These appear in the HTML report for easy visual comparison.

## Configuring Visual Comparisons

```typescript
// playwright.config.ts
export default defineConfig({
  expect: {
    toHaveScreenshot: {
      // Allow small pixel differences (anti-aliasing, rendering)
      maxDiffPixelRatio: 0.01,  // 1% of pixels can differ
      
      // Or absolute pixel count
      maxDiffPixels: 100,
      
      // Threshold for individual pixel color difference (0-1)
      threshold: 0.2,
    },
  },
});
```

### Per-Test Configuration

```typescript
test('chart renders correctly', async ({ page }) => {
  await page.goto('/analytics');
  
  // Charts have animation — allow more difference
  await expect(page.locator('.chart')).toHaveScreenshot('chart.png', {
    maxDiffPixelRatio: 0.05,  // 5% tolerance
    animations: 'disabled',   // Disable CSS animations
  });
});
```

## Handling Dynamic Content

Screenshots break when content changes (timestamps, avatars, random data). Mask or hide dynamic elements:

```typescript
test('dashboard visual', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Mask dynamic elements
  await expect(page).toHaveScreenshot('dashboard.png', {
    mask: [
      page.locator('.timestamp'),
      page.locator('.user-avatar'),
      page.locator('[data-testid="notification-count"]'),
    ],
  });
});
```

### Hide Elements with CSS

```typescript
test('page without dynamic content', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Hide elements via CSS before screenshot
  await page.addStyleTag({
    content: `
      .timestamp, .avatar, .live-indicator { visibility: hidden !important; }
    `,
  });
  
  await expect(page).toHaveScreenshot('dashboard-static.png');
});
```

### Freeze Animations

```typescript
test('no animation interference', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Disable all animations
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        transition-duration: 0s !important;
      }
    `,
  });
  
  await expect(page).toHaveScreenshot('dashboard.png');
});

// Or use the built-in option:
await expect(page).toHaveScreenshot('dashboard.png', {
  animations: 'disabled',
});
```

## Responsive Visual Testing

Test different viewport sizes:

```typescript
test.describe('responsive design', () => {
  test('desktop layout', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/dashboard');
    await expect(page).toHaveScreenshot('dashboard-desktop.png');
  });

  test('tablet layout', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/dashboard');
    await expect(page).toHaveScreenshot('dashboard-tablet.png');
  });

  test('mobile layout', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
    await expect(page).toHaveScreenshot('dashboard-mobile.png');
  });
});
```

## Dark Mode

```typescript
test('dark mode appearance', async ({ page }) => {
  // Emulate dark color scheme
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto('/dashboard');
  await expect(page).toHaveScreenshot('dashboard-dark.png');
});

test('light mode appearance', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto('/dashboard');
  await expect(page).toHaveScreenshot('dashboard-light.png');
});
```

## Full Page Screenshots

```typescript
test('full page visual', async ({ page }) => {
  await page.goto('/pricing');
  
  // Capture the entire scrollable page
  await expect(page).toHaveScreenshot('pricing-full.png', {
    fullPage: true,
  });
});
```

## Visual Testing Strategy

Not every page needs visual tests. Focus on:

1. **Landing pages** — first impression matters
2. **Complex layouts** — dashboards, data tables, charts
3. **Component library** — buttons, cards, forms in all states
4. **Responsive breakpoints** — mobile, tablet, desktop
5. **Theme variants** — light/dark mode

Don't visual-test:
- Pages with mostly dynamic content (feeds, timelines)
- Pages that change frequently (active development)
- Simple CRUD forms (functional tests are enough)

## Updating Baselines

When you intentionally change the UI:

```bash
# Update all snapshots
npx playwright test --update-snapshots

# Update snapshots for specific tests
npx playwright test tests/visual.spec.ts --update-snapshots
```

Review the changes in git diff before committing. Baseline images should be committed to the repository.

## Cross-Browser Visual Differences

Different browsers render slightly differently. Playwright stores separate baselines per browser:

```
tests/__snapshots__/
├── dashboard-chromium.png
├── dashboard-firefox.png
└── dashboard-webkit.png
```

Each browser has its own baseline. This handles font rendering differences, scrollbar styles, and other browser-specific quirks.

## What You Learned

- **toHaveScreenshot()** — compare page/element against baseline image
- **Baselines** — created with `--update-snapshots`, stored in git
- **Tolerance** — `maxDiffPixelRatio` and `threshold` for acceptable differences
- **Masking** — hide dynamic content (timestamps, avatars) from comparison
- **Animations** — disable with `animations: 'disabled'` for stable screenshots
- **Responsive** — test different viewport sizes
- **Dark mode** — `emulateMedia({ colorScheme: 'dark' })`
- **Strategy** — visual test layouts and components, not dynamic content

Visual tests catch CSS regressions that functional tests miss. The final chapter brings everything together: complete end-to-end flows that test the full user journey.

---

[← Chapter 10: Advanced Interactions](chapter-10-advanced-interactions.md) | [Chapter 12: End-to-End Flows →](chapter-12-e2e-flows.md)
