# Chapter 4: Typography & Content — Making Text Beautiful

[← Chapter 3: Responsive Navbar](chapter-03-responsive-navbar.md) | [Chapter 5: Colors & Theming →](chapter-05-colors-theming.md)

---

## The Task

Sora: "We have a changelog page and a help center. Long-form content. I need headings, paragraphs, lists, code blocks — all looking clean without styling every single element manually."

---

## The Type Scale

Tailwind's font size utilities follow a harmonious scale:

```
────────────────────────────────────────────────────────────
 Class      │ Size    │ Line Height │ Use Case
────────────────────────────────────────────────────────────
 text-xs    │ 12px    │ 16px        │ Labels, badges, captions
 text-sm    │ 14px    │ 20px        │ Secondary text, nav items
 text-base  │ 16px    │ 24px        │ Body text (default)
 text-lg    │ 18px    │ 28px        │ Slightly emphasized body
 text-xl    │ 20px    │ 28px        │ Card titles, section heads
 text-2xl   │ 24px    │ 32px        │ Page section titles
 text-3xl   │ 30px    │ 36px        │ Page titles
 text-4xl   │ 36px    │ 40px        │ Hero headings
 text-5xl   │ 48px    │ 48px        │ Large hero text
 text-6xl   │ 60px    │ 60px        │ Display text
────────────────────────────────────────────────────────────
```

---

## Building a Page Header

```tsx
function PageHeader({ title, description }) {
  return (
    <div className="mb-8">
      <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
        {title}
      </h1>
      {description && (
        <p className="mt-2 text-lg text-gray-600">
          {description}
        </p>
      )}
    </div>
  );
}
```

New utilities:
- `tracking-tight` → `letter-spacing: -0.025em` (tighter letters for headings)
- `tracking-wide` → `letter-spacing: 0.025em` (wider for small caps/labels)

---

## Font Weight & Style

```html
<!-- Weights -->
<p class="font-thin">100</p>
<p class="font-light">300</p>
<p class="font-normal">400 (default)</p>
<p class="font-medium">500</p>
<p class="font-semibold">600</p>
<p class="font-bold">700</p>
<p class="font-extrabold">800</p>
<p class="font-black">900</p>

<!-- Style & decoration -->
<p class="italic">Italic text</p>
<p class="underline">Underlined</p>
<p class="line-through">Strikethrough</p>
<p class="uppercase tracking-wide text-xs">Label text</p>
<p class="capitalize">capitalize each word</p>
```

---

## Line Height & Spacing

```html
<!-- Line height (leading) -->
<p class="leading-none">1.0 — tight, for headings</p>
<p class="leading-tight">1.25</p>
<p class="leading-snug">1.375</p>
<p class="leading-normal">1.5 (default)</p>
<p class="leading-relaxed">1.625 — comfortable reading</p>
<p class="leading-loose">2.0 — very spacious</p>

<!-- Max width for readability -->
<p class="max-w-prose">
  This paragraph will never exceed ~65 characters per line,
  which is the optimal reading width. Tailwind's max-w-prose
  is 65ch.
</p>
```

Sora: "Body text should never exceed 65-75 characters per line. Wider than that and the eye loses its place."

`max-w-prose` handles this automatically.

---

## The Prose Plugin: Styling Rich Content

For long-form content (blog posts, docs, changelogs), styling every element manually is painful. The `@tailwindcss/typography` plugin adds a `prose` class that styles all child elements beautifully.

```bash
npm install -D @tailwindcss/typography
```

Add to your CSS:

```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```

Now:

```tsx
function ChangelogEntry({ date, title, html }) {
  return (
    <article className="border-b border-gray-200 pb-8 mb-8">
      <time className="text-sm text-gray-500 font-medium uppercase tracking-wide">
        {date}
      </time>
      <h2 className="text-2xl font-bold text-gray-900 mt-2">{title}</h2>

      {/* prose styles all child HTML elements */}
      <div
        className="prose prose-gray mt-4 max-w-none"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </article>
  );
}
```

What `prose` gives you for free:
- Headings with proper sizes and spacing
- Paragraphs with comfortable line height
- Lists with bullets/numbers and indentation
- Code blocks with background and padding
- Links with color and underline
- Blockquotes with left border
- Tables with borders and padding
- Images with rounded corners

---

## Prose Modifiers

```html
<!-- Size variants -->
<div class="prose prose-sm">Small text (14px base)</div>
<div class="prose prose-base">Default (16px base)</div>
<div class="prose prose-lg">Large text (18px base)</div>
<div class="prose prose-xl">Extra large (20px base)</div>

<!-- Color themes -->
<div class="prose prose-gray">Gray headings/links</div>
<div class="prose prose-blue">Blue links</div>

<!-- Override specific elements -->
<div class="prose prose-headings:text-blue-900 prose-a:text-blue-600 prose-code:text-pink-600">
  Content with custom heading, link, and code colors
</div>

<!-- Remove max-width constraint -->
<div class="prose max-w-none">
  Full-width prose content
</div>
```

---

## Text Utilities You'll Use Daily

```html
<!-- Truncation -->
<p class="truncate">This very long text will be cut off with an ellipsis...</p>
<p class="line-clamp-2">This text will show at most 2 lines then ellipsis...</p>
<p class="line-clamp-3">Three lines max...</p>

<!-- Alignment -->
<p class="text-left">Left (default)</p>
<p class="text-center">Centered</p>
<p class="text-right">Right-aligned</p>

<!-- Wrapping -->
<p class="whitespace-nowrap">Never wraps</p>
<p class="break-words">Breaks long words to prevent overflow</p>
<p class="break-all">Breaks anywhere (for URLs, hashes)</p>

<!-- Selection -->
<p class="select-none">Can't select this text</p>
<p class="select-all">Selects all on click (good for code)</p>
```

---

## Building a Help Center Page

```tsx
function HelpCenter() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <PageHeader
        title="Help Center"
        description="Everything you need to know about Pixelflow."
      />

      {/* Search */}
      <div className="relative mb-12">
        <input
          type="search"
          placeholder="Search articles..."
          className="w-full px-4 py-3 pl-10 rounded-lg border border-gray-300 text-base focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
      </div>

      {/* Category grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <HelpCategory
          title="Getting Started"
          description="Set up your workspace and invite your team."
          articles={["Create your first project", "Invite team members", "Connect integrations"]}
        />
        <HelpCategory
          title="Billing"
          description="Manage your subscription and invoices."
          articles={["Change your plan", "Download invoices", "Cancel subscription"]}
        />
      </div>
    </div>
  );
}

function HelpCategory({ title, description, articles }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
      <p className="text-sm text-gray-500 mt-1">{description}</p>
      <ul className="mt-4 space-y-2">
        {articles.map((article) => (
          <li key={article}>
            <a href="#" className="text-sm text-blue-600 hover:text-blue-800 hover:underline">
              {article}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## Sora's Typography Rules

Sora writes them on the whiteboard:

```
Heading 1:  text-3xl  font-bold   tracking-tight  text-gray-900
Heading 2:  text-2xl  font-bold   tracking-tight  text-gray-900
Heading 3:  text-xl   font-semibold               text-gray-900
Body:       text-base font-normal                  text-gray-700
Secondary:  text-sm   font-normal                  text-gray-500
Caption:    text-xs   font-medium  uppercase tracking-wide  text-gray-400
Link:       text-sm   font-medium                  text-blue-600
```

You: "This is our type system. Six styles. Covers everything."

Dev: "What about `text-md`?"

You: "Doesn't exist. `text-base` is 16px. There's no `md` — it goes `sm` → `base` → `lg`."

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ Classes
────────────────────────────────┼──────────────────────────────────────
Page title                      │ text-3xl font-bold tracking-tight
Section title                   │ text-2xl font-bold
Card title                      │ text-lg font-semibold
Body text                       │ text-base text-gray-700
Secondary text                  │ text-sm text-gray-500
Label / caption                 │ text-xs uppercase tracking-wide
Readable width                  │ max-w-prose
Truncate single line            │ truncate
Truncate multi-line             │ line-clamp-{n}
Rich content styling            │ prose prose-gray
Tight heading letters           │ tracking-tight
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "The type system is solid. Now let's talk color. I want a custom brand palette — not just Tailwind's defaults. And gradients for the hero sections. And the colors need to work in both light and dark mode."

Colors, gradients, and building a custom palette.

---

[← Chapter 3: Responsive Navbar](chapter-03-responsive-navbar.md) | [Chapter 5: Colors & Theming →](chapter-05-colors-theming.md)
