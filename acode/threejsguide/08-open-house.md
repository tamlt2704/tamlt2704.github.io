# Chapter 8: Open House

> **What you'll learn:** Building for production, GitHub Actions deployment, and common deployment pitfalls.

### Build the Static Site

```bash
npm run build
```

This runs `next build` which, with `output: 'export'`, produces an `out/` directory containing:
```
out/
├── index.html
├── 404.html
├── _next/
│   └── static/          # JS bundles, CSS
├── models/              # Your .glb files (copied from public/)
├── textures/            # Your texture files
└── .nojekyll            # Tells GitHub Pages to skip Jekyll processing
```

### The `.nojekyll` File

**Critical.** GitHub Pages runs Jekyll by default, which ignores folders starting with `_`. Next.js outputs everything to `_next/`. Without `.nojekyll`, your entire app breaks silently — HTML loads but no JS or CSS.

Create it in your `public/` folder:

```bash
touch public/.nojekyll
```

It gets copied to `out/` during build.

### Test Locally Before Deploying

```bash
npx serve out
```

This serves the `out/` folder on a local HTTP server. Check that:
- The 3D scene loads
- Models appear
- Textures load
- Navigation works (if you have multiple pages)

> **Note:** `basePath` will be active if you built with `NODE_ENV=production`. Locally, paths will be prefixed with `/my-3d-house`, so you'll need to visit `http://localhost:3000/my-3d-house`.

### GitHub Actions — Automated Deployment

Create the workflow file:

**`.github/workflows/deploy.yml`**
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npm run build

      - uses: actions/upload-pages-artifact@v3
        with:
          path: out

      - id: deployment
        uses: actions/deploy-pages@v4
```

### Enable GitHub Pages

1. Go to your repo on GitHub → **Settings** → **Pages**
2. Under **Source**, select **GitHub Actions**
3. Push to `main` — the action runs and deploys

Your site will be live at `https://username.github.io/my-3d-house/`.

### Common Deployment Issues

| Problem | Cause | Fix |
|---|---|---|
| Blank white page | `_next/` folder ignored by Jekyll | Add `.nojekyll` to `public/` |
| 404 on all assets | Missing `basePath` in next.config | Set `basePath: '/repo-name'` |
| Models don't load | Hardcoded `/models/...` path | Use `basePath` prefix in model paths |
| Textures missing | Same as models | Use `basePath` prefix |
| Page works but refresh 404s | GitHub Pages can't handle client routes | Use `trailingSlash: true` in next.config |
| Build fails in CI | Different Node version | Pin Node version in workflow |

### Adding `trailingSlash`

For multi-page sites, add this to `next.config.ts`:

```ts
const nextConfig: NextConfig = {
  output: 'export',
  basePath: process.env.NODE_ENV === 'production' ? '/my-3d-house' : '',
  trailingSlash: true,  // generates /about/index.html instead of /about.html
  images: {
    unoptimized: true,
  },
}
```

This ensures each route has its own `index.html`, which GitHub Pages can resolve on direct navigation/refresh.

### Performance Checklist Before Going Live

- [ ] Models are Draco-compressed (`.glb` under 1-2MB each)
- [ ] Textures are compressed (`.webp` or `.jpg`, not raw `.png`)
- [ ] Post-processing is disabled or reduced on mobile
- [ ] `OrbitControls` has zoom/rotation limits
- [ ] Loading state shows progress (not a blank screen)
- [ ] Tested on mobile (Chrome DevTools device mode at minimum)
- [ ] Total page weight under 5MB for reasonable load times

---

> **🏗 The house is open.** Live on the internet, free hosting, no server needed.

---

[← Chapter 7: Landscaping](./07-landscaping.md) | [Summary →](./09-summary.md)
