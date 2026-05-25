# Chapter 20: Monetization — Buy Me a Coffee & Beyond

[← Chapter 19: Comments & Reactions](chapter-19-comments.md) | [Chapter 21: Multi-Language →](chapter-21-multi-language.md)

---

## The Conversation

You've written 50 chapters. Thousands of readers. Someone emails: "Your binary search explanation finally made it click. How can I support you?"

You need a way to accept that support. Not a paywall — your content stays free. Just a tip jar for people who want to give back.

## Buy Me a Coffee (5 Minutes)

### Step 1: Create Your Page

1. Go to [buymeacoffee.com](https://www.buymeacoffee.com)
2. Sign up (free)
3. Set your page name: `buymeacoffee.com/yourusername`
4. Add a profile photo, bio, and a thank-you message
5. Connect your payment method (Stripe or PayPal)

### Step 2: The Component

Create `app/components/BuyMeCoffee.tsx`:

```tsx
interface Props {
  username: string;
  variant?: "button" | "banner" | "inline";
}

export function BuyMeCoffee({ username, variant = "button" }: Props) {
  const url = `https://buymeacoffee.com/${username}`;

  if (variant === "banner") {
    return (
      <div className="my-8 p-5 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 text-center">
        <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
          Found this helpful? Consider supporting the project.
        </p>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-yellow-400 text-gray-900 rounded-lg font-medium text-sm hover:bg-yellow-300 transition shadow-sm"
        >
          ☕ Buy me a coffee
        </a>
      </div>
    );
  }

  if (variant === "inline") {
    return (
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-sm text-yellow-700 dark:text-yellow-400 hover:underline"
      >
        ☕ Support this project
      </a>
    );
  }

  // Default: button
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-400 text-gray-900 rounded-lg font-medium text-sm hover:bg-yellow-300 transition"
    >
      ☕ Buy me a coffee
    </a>
  );
}
```

### Step 3: Place It Strategically

**In the navbar** (always visible):

```tsx
<nav className="flex items-center gap-3">
  <LangSwitcher />
  <ThemeToggle />
  <BuyMeCoffee username="yourusername" variant="inline" />
  <AuthButton />
</nav>
```

**At the end of each chapter** (after the reader got value):

```tsx
// In app/blog/[...slug]/page.tsx, after the content:
<BuyMeCoffee username="yourusername" variant="banner" />
<Comments slug={slug} />
```

**In markdown** (register as MDX component):

```tsx
components={{
  ...existingComponents,
  BuyMeCoffee,
}}
```

Then in any `.md` file:

```markdown
## Thanks for Reading

<BuyMeCoffee username="yourusername" variant="banner" />
```

### Step 4: The Official Widget (Alternative)

Buy Me a Coffee also provides an official floating widget:

```tsx
// app/components/BmcWidget.tsx
"use client";

import { useEffect } from "react";

export function BmcWidget({ username }: { username: string }) {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js";
    script.setAttribute("data-name", "BMC-Widget");
    script.setAttribute("data-id", username);
    script.setAttribute("data-description", "Support me on Buy me a coffee!");
    script.setAttribute("data-color", "#FFDD00");
    script.async = true;
    document.body.appendChild(script);
    return () => { document.body.removeChild(script); };
  }, [username]);

  return null;
}
```

This adds a floating button in the bottom-right corner. Some people find it intrusive — the custom component approach gives you more control.

## Alternatives to Buy Me a Coffee

| Platform | Fees | Best For |
|----------|------|----------|
| [Buy Me a Coffee](https://buymeacoffee.com) | 5% | Simple tip jar |
| [Ko-fi](https://ko-fi.com) | 0% (free!) | Zero-fee tips |
| [GitHub Sponsors](https://github.com/sponsors) | 0% | Developer audience |
| [Stripe Payment Links](https://stripe.com) | 2.9% + 30¢ | Custom amounts |
| [Gumroad](https://gumroad.com) | 10% | Selling premium content |

For a free blog with optional support: **Ko-fi** (zero fees) or **GitHub Sponsors** (your readers already have GitHub accounts).

## GitHub Sponsors Button

If your readers are developers:

```tsx
export function SponsorButton({ username }: { username: string }) {
  return (
    <a
      href={`https://github.com/sponsors/${username}`}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-2 px-4 py-2 border border-pink-300 text-pink-600 rounded-lg text-sm hover:bg-pink-50 dark:hover:bg-pink-900/20 transition"
    >
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
        <path d="M4.25 2.5c-1.336 0-2.75 1.164-2.75 3 0 2.15 1.58 4.144 3.365 5.682A20.565 20.565 0 008 13.393a20.561 20.561 0 003.135-2.211C12.92 9.644 14.5 7.65 14.5 5.5c0-1.836-1.414-3-2.75-3-1.373 0-2.609.986-3.029 2.456a.75.75 0 01-1.442 0C6.859 3.486 5.623 2.5 4.25 2.5z" />
      </svg>
      Sponsor
    </a>
  );
}
```

## Premium Content (Optional)

If you want to gate some chapters behind a payment:

```tsx
// Simple client-side gate (not truly secure, but enough for soft paywall)
function PremiumContent({ children, slug }: { children: React.ReactNode; slug: string }) {
  const { isLoggedIn } = useProgress(slug);
  const [hasAccess, setHasAccess] = useState(false);

  useEffect(() => {
    // Check if user has premium access in Supabase
    if (isLoggedIn) {
      supabase.from("user_access")
        .select("premium")
        .eq("user_id", user.id)
        .single()
        .then(({ data }) => setHasAccess(data?.premium || false));
    }
  }, [isLoggedIn]);

  if (!hasAccess) {
    return (
      <div className="p-8 text-center border rounded-lg bg-gray-50 dark:bg-gray-800">
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          This chapter is available to supporters.
        </p>
        <BuyMeCoffee username="yourusername" />
      </div>
    );
  }

  return <>{children}</>;
}
```

**Important:** Client-side gating is not secure — determined users can view source. For a blog, that's fine. If you need real security, serve premium content from Supabase Edge Functions.

## The Non-Pushy Approach

The best monetization for educational content:

1. **All content is free** — no paywalls, no "subscribe to continue"
2. **Support is optional** — a banner at the end, not a popup
3. **Value first** — readers support because they got value, not because you asked
4. **Multiple options** — some prefer one-time tips, others monthly sponsorship

```markdown
## End of Chapter

If this series helped you land a job, pass an interview, or just understand
something that was confusing — consider buying me a coffee. It keeps the
content free for everyone.

<BuyMeCoffee username="yourusername" variant="banner" />
```

---

## What's Next

Chapter 21 takes your course global — multi-language support so you can teach in English, French, Vietnamese, and Chinese from the same codebase.
