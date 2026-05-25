# Chapter 18: Auth & User Progress

[← Chapter 17: View Counts](/blog/nextjs-ghpages/chapter-17-view-counts) | [Chapter 19: Comments & Reactions →](/blog/nextjs-ghpages/chapter-19-comments)

---

## Why Auth

Your reader finishes Chapter 5. Closes the browser. Comes back tomorrow. Where were they? Which quizzes did they pass? What code did they write in the playground?

Without auth, every visit is a stranger. With auth, you can:

- Track reading progress (checkmarks on completed chapters)
- Save quiz scores
- Remember playground code
- Show personalized recommendations

## GitHub OAuth (Perfect for a Dev Blog)

Your readers are developers. They have GitHub accounts. One-click login.

### Step 1: Enable GitHub Provider in Supabase

1. Supabase Dashboard → Authentication → Providers
2. Enable **GitHub**
3. You need a GitHub OAuth App:
   - Go to GitHub → Settings → Developer settings → OAuth Apps → New
   - Application name: `My Blog`
   - Homepage URL: `https://yourusername.github.io`
   - Callback URL: `https://abcdefgh.supabase.co/auth/v1/callback`
4. Copy the Client ID and Client Secret into Supabase

### Step 2: The Auth Component

Create `app/components/AuthButton.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import type { User } from "@supabase/supabase-js";

export function AuthButton() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Check current session
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const login = () => {
    supabase.auth.signInWithOAuth({
      provider: "github",
      options: {
        redirectTo: window.location.href, // come back to same page
      },
    });
  };

  const logout = () => {
    supabase.auth.signOut();
    setUser(null);
  };

  if (user) {
    return (
      <div className="flex items-center gap-2">
        <img
          src={user.user_metadata.avatar_url}
          alt={user.user_metadata.user_name}
          className="h-7 w-7 rounded-full"
        />
        <span className="hidden text-sm text-gray-600 sm:inline dark:text-gray-400">
          {user.user_metadata.user_name}
        </span>
        <button onClick={logout} className="text-xs text-gray-400 hover:text-gray-600">
          Logout
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={login}
      className="rounded border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-800"
    >
      Login with GitHub
    </button>
  );
}
```

Add it to your navbar. One button. Login → GitHub OAuth → redirect back → avatar shows.

### Step 3: The Progress Table

```sql
create table user_progress (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade,
  slug text not null,
  completed boolean default false,
  quiz_score int,
  updated_at timestamptz default now(),
  unique(user_id, slug)
);

-- RLS: users can only see/edit their own progress
alter table user_progress enable row level security;

create policy "Users read own progress"
  on user_progress for select
  using (auth.uid() = user_id);

create policy "Users write own progress"
  on user_progress for insert
  with check (auth.uid() = user_id);

create policy "Users update own progress"
  on user_progress for update
  using (auth.uid() = user_id);
```

### Step 4: The Progress Hook

```tsx
// hooks/useProgress.ts
"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

interface Progress {
  completed: boolean;
  quiz_score: number | null;
}

export function useProgress(slug: string) {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
      if (data.user) {
        supabase
          .from("user_progress")
          .select("completed, quiz_score")
          .eq("user_id", data.user.id)
          .eq("slug", slug)
          .single()
          .then(({ data: prog }) => {
            setProgress(prog || { completed: false, quiz_score: null });
          });
      }
    });
  }, [slug]);

  const markComplete = async () => {
    if (!user) return;
    await supabase.from("user_progress").upsert({
      user_id: user.id,
      slug,
      completed: true,
      updated_at: new Date().toISOString(),
    });
    setProgress((prev) => (prev ? { ...prev, completed: true } : null));
  };

  const saveQuizScore = async (score: number) => {
    if (!user) return;
    await supabase.from("user_progress").upsert({
      user_id: user.id,
      slug,
      quiz_score: score,
      updated_at: new Date().toISOString(),
    });
    setProgress((prev) => (prev ? { ...prev, quiz_score: score } : null));
  };

  return { progress, markComplete, saveQuizScore, isLoggedIn: !!user };
}
```

### Step 5: "Mark as Complete" Button

```tsx
// app/blog/components/ChapterComplete.tsx
"use client";

import { useProgress } from "@/hooks/useProgress";

export function ChapterComplete({ slug }: { slug: string }) {
  const { progress, markComplete, isLoggedIn } = useProgress(slug);

  if (!isLoggedIn) return null; // only show for logged-in users

  return (
    <div className="mt-8 border-t pt-6">
      {progress?.completed ? (
        <p className="flex items-center gap-2 text-sm text-green-600">
          <span>✓</span> Chapter completed
        </p>
      ) : (
        <button
          onClick={markComplete}
          className="rounded bg-teal-600 px-4 py-2 text-sm text-white hover:bg-teal-700"
        >
          Mark as complete
        </button>
      )}
    </div>
  );
}
```

### Step 6: Progress on the Series Page

Show checkmarks next to completed chapters:

```tsx
// In your chapter list
{
  chapters.map((ch) => (
    <Link key={ch} href={`/blog/${series}/${ch}`} className="flex items-center gap-2">
      {completedSlugs.includes(`${series}/${ch}`) && (
        <span className="text-xs text-green-500">✓</span>
      )}
      <span>{ch.replace(/-/g, " ")}</span>
    </Link>
  ));
}
```

### Step 7: Quiz Saves Score

Update your Quiz component to save scores:

```tsx
import { useProgress } from "@/hooks/useProgress";

export function Quiz({ question, options, answer, slug }: QuizProps & { slug?: string }) {
  const { saveQuizScore, isLoggedIn } = useProgress(slug || "");

  const handleSelect = (index: number) => {
    setSelected(index);
    setRevealed(true);

    // Save score if logged in
    if (isLoggedIn && slug) {
      saveQuizScore(index === answer ? 100 : 0);
    }
  };
  // ...
}
```

## The Complete Auth Flow

```
Reader visits blog → sees content (no login required)
    ↓
Clicks "Login with GitHub" → GitHub OAuth → redirected back
    ↓
Now logged in → avatar in navbar
    ↓
Completes a chapter → "Mark as complete" → saved to Supabase
    ↓
Takes a quiz → score saved automatically
    ↓
Returns tomorrow → progress is there, chapters show ✓
```

Content is always public. Auth is optional. Progress is a bonus for logged-in readers.

## Security Notes

- The `anon` key can only do what RLS policies allow
- Users can only read/write their own progress (RLS enforces this)
- View counts are public (no auth needed)
- Never put the `service_role` key in client code (that bypasses RLS)

---

## What's Next

Chapter 19 adds comments and reactions — readers can leave feedback on chapters, upvote helpful content, and you can build a community around your writing.
