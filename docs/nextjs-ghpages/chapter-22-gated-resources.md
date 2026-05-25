# Chapter 22: Gated Resources for Registered Users

[← Chapter 21: Multi-Language](chapter-21-multi-language.md)

---

## The Strategy

All your teaching content is free. Anyone can read every chapter. But you offer bonus resources — cheat sheets, source code, project templates, video walkthroughs — that require a free account.

Why?

1. **Builds your user list** — you know who's learning from you
2. **Increases engagement** — logged-in users track progress, take quizzes
3. **Creates upgrade path** — free account → paid resources later (if you want)
4. **Feels fair** — "sign up for free to get the extras" is a reasonable ask

## The Three Tiers

```
┌─────────────────────────────────────────────────┐
│  PUBLIC (everyone)                              │
│  • All chapters, all languages                  │
│  • Code examples in the text                    │
│  • Interactive quizzes and playgrounds          │
├─────────────────────────────────────────────────┤
│  REGISTERED (free account)                      │
│  • PDF cheat sheets                             │
│  • Complete source code downloads               │
│  • Project starter templates                    │
│  • Progress tracking + saved quiz scores        │
├─────────────────────────────────────────────────┤
│  SUPPORTER (Buy Me a Coffee / Sponsor)          │
│  • Video walkthroughs                           │
│  • 1-on-1 code review (limited)                 │
│  • Early access to new courses                  │
└─────────────────────────────────────────────────┘
```

This chapter covers the **Registered** tier.

## Component 1: Soft Gate (Inline Content)

For bonus content that lives inside markdown — links, extra explanations, download buttons:

```tsx
// app/blog/components/RegisteredOnly.tsx
"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

interface Props {
  children: React.ReactNode;
  message?: string;
}

export function RegisteredOnly({ children, message }: Props) {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user ?? null);
      }
    );
    return () => subscription.unsubscribe();
  }, []);

  if (loading) {
    return (
      <div className="my-6 p-5 rounded-lg border border-gray-200 dark:border-gray-700 animate-pulse">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="my-6 p-6 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800/50">
        <div className="text-center">
          <p className="text-2xl mb-2">🔒</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {message || "This resource is available to registered users."}
          </p>
          <button
            onClick={() => supabase.auth.signInWithOAuth({
              provider: "github",
              options: { redirectTo: window.location.href },
            })}
            className="inline-flex items-center gap-2 px-4 py-2 bg-gray-900 dark:bg-white dark:text-gray-900 text-white rounded-lg text-sm font-medium hover:opacity-90 transition"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            Sign up free with GitHub
          </button>
          <p className="text-xs text-gray-400 mt-2">No spam. Just saves your progress.</p>
        </div>
      </div>
    );
  }

  return <div className="my-6">{children}</div>;
}
```

Register it as an MDX component:

```tsx
components={{
  ...existingComponents,
  RegisteredOnly,
}}
```

### Usage in Markdown

```markdown
## Summary

You now understand binary search. It's O(log n) because each step
halves the search space.

<RegisteredOnly message="Sign up to download the cheat sheet">

### 📥 Bonus Resources

- [Binary Search Cheat Sheet (PDF)](/resources/binary-search.pdf)
- [Complete source code for this chapter](https://github.com/you/algo-code/tree/main/ch02)
- [Practice problems with solutions](/resources/ch02-practice.md)

</RegisteredOnly>
```

The reader sees the chapter content. At the bottom, a locked box says "sign up to get the extras." One click → GitHub OAuth → content unlocks.

## Component 2: Secure File Downloads

For files you don't want accessible without auth (PDFs, zips, templates):

### Setup Supabase Storage

In the Supabase dashboard:

1. Go to **Storage** → Create bucket: `resources`
2. Set it to **Private** (not public)
3. Upload your files: `resources/binary-search.pdf`, `resources/starter-template.zip`

Add RLS policy:

```sql
-- Only authenticated users can download from 'resources' bucket
create policy "Authenticated downloads"
  on storage.objects for select
  using (bucket_id = 'resources' and auth.role() = 'authenticated');
```

### The Download Component

```tsx
// app/blog/components/SecureDownload.tsx
"use client";

import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";

interface Props {
  path: string;       // path in storage bucket, e.g. "python/cheatsheet.pdf"
  label: string;      // display text
  size?: string;      // optional file size display
}

export function SecureDownload({ path, label, size }: Props) {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setUser(data.user));
  }, []);

  const download = async () => {
    if (!user) {
      supabase.auth.signInWithOAuth({
        provider: "github",
        options: { redirectTo: window.location.href },
      });
      return;
    }

    setLoading(true);
    setError("");

    const { data, error: err } = await supabase.storage
      .from("resources")
      .download(path);

    if (err) {
      setError("Download failed. Try again.");
      setLoading(false);
      return;
    }

    if (data) {
      const url = URL.createObjectURL(data);
      const a = document.createElement("a");
      a.href = url;
      a.download = path.split("/").pop() || "download";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }

    setLoading(false);
  };

  return (
    <button
      onClick={download}
      disabled={loading}
      className="inline-flex items-center gap-2 px-3 py-2 rounded-md border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition text-sm disabled:opacity-50"
    >
      <span>📥</span>
      <span>{loading ? "Downloading..." : label}</span>
      {size && <span className="text-xs text-gray-400">({size})</span>}
      {!user && <span className="text-xs text-gray-400 ml-1">🔒</span>}
      {error && <span className="text-xs text-red-500 ml-2">{error}</span>}
    </button>
  );
}
```

### Usage in Markdown

```markdown
## Downloads

<SecureDownload path="python-basics/cheatsheet.pdf" label="Python Cheat Sheet" size="2.1 MB" />
<SecureDownload path="python-basics/starter-project.zip" label="Starter Template" size="450 KB" />
<SecureDownload path="python-basics/solutions.pdf" label="Exercise Solutions" size="1.8 MB" />
```

If not logged in: clicking shows the GitHub login flow. After login, the download starts automatically (redirect back to same page).

If logged in: instant download. The file URL is never exposed — Supabase generates a temporary signed URL server-side.

## Component 3: Resource Library Page

A dedicated page listing all available resources:

```tsx
// app/resources/page.tsx
"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import { SecureDownload } from "@/app/blog/components/SecureDownload";

interface Resource {
  name: string;
  path: string;
  size: string;
  category: string;
}

const RESOURCES: Resource[] = [
  { name: "Python Basics Cheat Sheet", path: "python/cheatsheet.pdf", size: "2.1 MB", category: "Python" },
  { name: "React Hooks Reference", path: "react/hooks-reference.pdf", size: "1.5 MB", category: "React" },
  { name: "Algorithm Complexity Table", path: "algorithms/complexity.pdf", size: "800 KB", category: "Algorithms" },
  { name: "Full Course Source Code", path: "all/source-code.zip", size: "12 MB", category: "All" },
  { name: "Project Starter Template", path: "templates/nextjs-blog.zip", size: "450 KB", category: "Templates" },
];

export default function ResourcesPage() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setUser(data.user));
  }, []);

  const categories = [...new Set(RESOURCES.map(r => r.category))];

  return (
    <main className="max-w-3xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold mb-2">Resources</h1>
      <p className="text-gray-500 mb-8">
        Cheat sheets, source code, and templates.
        {!user && " Sign up free to download."}
      </p>

      {categories.map(cat => (
        <section key={cat} className="mb-8">
          <h2 className="text-lg font-semibold mb-3">{cat}</h2>
          <div className="space-y-2">
            {RESOURCES.filter(r => r.category === cat).map(r => (
              <SecureDownload key={r.path} path={r.path} label={r.name} size={r.size} />
            ))}
          </div>
        </section>
      ))}
    </main>
  );
}
```

## Tracking Downloads

Know which resources are popular:

```sql
create table download_log (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id),
  resource_path text not null,
  downloaded_at timestamptz default now()
);

alter table download_log enable row level security;
create policy "Users log own downloads"
  on download_log for insert
  with check (auth.uid() = user_id);
```

Add to the download function:

```tsx
// After successful download:
if (data && user) {
  supabase.from("download_log").insert({
    user_id: user.id,
    resource_path: path,
  });
}
```

Now you know: "The Python cheat sheet was downloaded 342 times this month."

## Email Collection (Optional)

If you want to email users about new courses:

```sql
-- Users table already exists via Supabase Auth
-- Access email via auth.users table or user metadata

-- Or create a newsletter opt-in:
create table newsletter (
  user_id uuid references auth.users(id) primary key,
  email text not null,
  opted_in boolean default true,
  created_at timestamptz default now()
);
```

After login, prompt once:

```tsx
function NewsletterPrompt() {
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (localStorage.getItem("newsletter-prompted")) setDismissed(true);
  }, []);

  const optIn = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (user?.email) {
      await supabase.from("newsletter").upsert({
        user_id: user.id,
        email: user.email,
      });
    }
    localStorage.setItem("newsletter-prompted", "1");
    setDismissed(true);
  };

  const dismiss = () => {
    localStorage.setItem("newsletter-prompted", "1");
    setDismissed(true);
  };

  if (dismissed) return null;

  return (
    <div className="fixed bottom-4 right-4 max-w-sm p-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg border z-40">
      <p className="text-sm mb-3">Get notified when new courses drop?</p>
      <div className="flex gap-2">
        <button onClick={optIn} className="px-3 py-1.5 bg-teal-600 text-white text-sm rounded">
          Yes, notify me
        </button>
        <button onClick={dismiss} className="px-3 py-1.5 text-gray-500 text-sm">
          No thanks
        </button>
      </div>
    </div>
  );
}
```

## Security: What's Actually Protected?

| Method | Security Level | Use For |
|--------|---------------|---------|
| `<RegisteredOnly>` | Soft (client-side hide) | Bonus links, extra text, non-sensitive |
| Supabase Storage (private bucket) | Hard (server-enforced) | PDFs, zips, paid content |
| Supabase Edge Functions | Hardest (custom logic) | License checks, usage limits |

**Soft gate** = content is in the HTML, just hidden. A developer could find it in view-source. That's fine for "sign up to see the download link" — the value is convenience, not secrecy.

**Hard gate** = the file literally cannot be accessed without a valid auth token. Supabase Storage enforces this at the API level. No workaround.

## The User Journey

```
Reader finds your blog via Google
    ↓
Reads 3 chapters (free, no login)
    ↓
Sees "🔒 Sign up to download cheat sheet"
    ↓
Clicks → GitHub OAuth → 2 seconds → logged in
    ↓
Downloads cheat sheet, progress starts tracking
    ↓
Comes back next week → progress is saved
    ↓
Finishes course → sees "Buy me a coffee" banner
    ↓
Maybe supports you. Maybe doesn't. Content stays free either way.
```

No friction for reading. Minimal friction for extras. Zero friction for coming back.

---

## Series Complete

22 chapters. A full-stack learning platform:

| Part | Chapters | What |
|------|----------|------|
| Build | 0–7 | Static blog + interactive components |
| Polish | 8–11 | Dark mode, mobile, performance |
| Understand | 12–15 | JS, React, Hooks, TypeScript |
| Backend | 16–19 | Supabase: views, auth, comments |
| Scale | 20–22 | Monetization, i18n, gated resources |

**Free for readers. Free to host. Yours to grow.**
