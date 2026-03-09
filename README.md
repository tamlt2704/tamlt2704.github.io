1. npx create-next-app@latest .

2. update next.config.ts

```
const nextConfig: NextConfig = {
  /* config options here */
  output: 'export',
  images: {
    unoptimized: true
  }
};
```

output: 'export'

+ Tells Next.js to generate a fully static site

+ Creates an out/ folder with HTML, CSS, JS files

+ No Node.js server needed - just static files GitHub Pages can serve

images: { unoptimized: true }

+ Disables Next.js's built-in image optimization

+ Image optimization requires a server (which GitHub Pages doesn't have)

+ Your images will work but won't be automatically resized/optimized


3. Add to package.json scripts:
"scripts": {
  "build": "next build"
}

4. Add a .nojekyll file (prevents GitHub from ignoring files starting with _)

# Install gh-pages
npm install --save-dev gh-pages

# Add to package.json scripts:
"scripts": {
  "build": "next build",
  "deploy": "next build && touch out/.nojekyll && gh-pages -d out -t true"
}

# Deploy
npm run deploy