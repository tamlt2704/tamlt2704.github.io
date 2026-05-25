# Chapter 19: Comments & Reactions

[← Chapter 18: Auth & Progress](chapter-18-auth-progress.md)

---

## The Community Layer

Your blog has readers. Some want to say "this helped me." Some want to ask "what about edge case X?" Some want to point out a typo. Comments turn a one-way broadcast into a conversation.

## Option A: Giscus (Zero Backend)

If you don't want to manage comments yourself, [Giscus](https://giscus.app) uses GitHub Discussions as the backend. Free, no database needed:

```tsx
// app/blog/components/Comments.tsx
"use client";

import { useEffect, useRef } from "react";

export function Comments({ slug }: { slug: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://giscus.app/client.js";
    script.setAttribute("data-repo", "yourusername/yourusername.github.io");
    script.setAttribute("data-repo-id", "R_xxxxx");  // from giscus.app setup
    script.setAttribute("data-category", "Blog Comments");
    script.setAttribute("data-category-id", "DIC_xxxxx");
    script.setAttribute("data-mapping", "pathname");
    script.setAttribute("data-theme", "preferred_color_scheme");
    script.setAttribute("data-lang", "en");
    script.crossOrigin = "anonymous";
    script.async = true;

    ref.current?.appendChild(script);
    return () => { ref.current?.innerHTML = ""; };
  }, [slug]);

  return <div ref={ref} className="mt-12" />;
}
```

Pros: zero maintenance, GitHub login, markdown support, reactions built-in.
Cons: requires GitHub account to comment, tied to GitHub Discussions.

## Option B: Supabase Comments (Full Control)

If you want custom UI and already have Supabase:

### The Table

```sql
create table comments (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade,
  slug text not null,
  body text not null,
  author_name text,
  author_avatar text,
  created_at timestamptz default now()
);

-- RLS
alter table comments enable row level security;

create policy "Anyone can read comments"
  on comments for select using (true);

create policy "Authenticated users can comment"
  on comments for insert
  with check (auth.uid() = user_id);

create policy "Users can delete own comments"
  on comments for delete
  using (auth.uid() = user_id);
```

### The Component

```tsx
"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

interface Comment {
  id: string;
  body: string;
  author_name: string;
  author_avatar: string;
  created_at: string;
  user_id: string;
}

export function Comments({ slug }: { slug: string }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [body, setBody] = useState("");
  const [user, setUser] = useState<any>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    // Load comments
    supabase
      .from("comments")
      .select("*")
      .eq("slug", slug)
      .order("created_at", { ascending: true })
      .then(({ data }) => setComments(data || []));

    // Check auth
    supabase.auth.getUser().then(({ data }) => setUser(data.user));
  }, [slug]);

  const submit = async () => {
    if (!body.trim() || !user) return;
    setSubmitting(true);

    const { data, error } = await supabase.from("comments").insert({
      user_id: user.id,
      slug,
      body: body.trim(),
      author_name: user.user_metadata.user_name || "Anonymous",
      author_avatar: user.user_metadata.avatar_url || "",
    }).select().single();

    if (!error && data) {
      setComments([...comments, data]);
      setBody("");
    }
    setSubmitting(false);
  };

  return (
    <section className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-semibold mb-4">Comments</h3>

      {/* Comment list */}
      <div className="space-y-4 mb-6">
        {comments.map((c) => (
          <div key={c.id} className="flex gap-3">
            <img src={c.author_avatar} className="w-8 h-8 rounded-full" alt="" />
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{c.author_name}</span>
                <span className="text-xs text-gray-400">
                  {new Date(c.created_at).toLocaleDateString()}
                </span>
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">{c.body}</p>
            </div>
          </div>
        ))}
        {comments.length === 0 && (
          <p className="text-sm text-gray-400">No comments yet. Be the first!</p>
        )}
      </div>

      {/* Comment form */}
      {user ? (
        <div className="flex gap-3">
          <img src={user.user_metadata.avatar_url} className="w-8 h-8 rounded-full" alt="" />
          <div className="flex-1">
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Leave a comment..."
              className="w-full p-3 text-sm border rounded-lg resize-none bg-white dark:bg-gray-800 dark:border-gray-600"
              rows={3}
            />
            <button
              onClick={submit}
              disabled={!body.trim() || submitting}
              className="mt-2 px-4 py-1.5 text-sm bg-teal-600 text-white rounded hover:bg-teal-700 disabled:opacity-50"
            >
              {submitting ? "Posting..." : "Post Comment"}
            </button>
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-500">
          <button
            onClick={() => supabase.auth.signInWithOAuth({ provider: "github" })}
            className="text-teal-600 hover:underline"
          >
            Login with GitHub
          </button>
          {" "}to leave a comment.
        </p>
      )}
    </section>
  );
}
```

## Reactions (Likes/Upvotes)

A simpler engagement signal — one click, no text:

```sql
create table reactions (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade,
  slug text not null,
  emoji text default '👍',
  created_at timestamptz default now(),
  unique(user_id, slug, emoji)  -- one reaction per type per user per page
);

alter table reactions enable row level security;
create policy "Anyone can read" on reactions for select using (true);
create policy "Auth users can react" on reactions for insert with check (auth.uid() = user_id);
create policy "Users can unreact" on reactions for delete using (auth.uid() = user_id);
```

```tsx
"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

const EMOJIS = ["👍", "🔥", "💡", "🎉"];

export function Reactions({ slug }: { slug: string }) {
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [userReactions, setUserReactions] = useState<string[]>([]);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Get counts
    supabase
      .from("reactions")
      .select("emoji")
      .eq("slug", slug)
      .then(({ data }) => {
        const c: Record<string, number> = {};
        data?.forEach(r => { c[r.emoji] = (c[r.emoji] || 0) + 1; });
        setCounts(c);
      });

    // Get user's reactions
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
      if (data.user) {
        supabase
          .from("reactions")
          .select("emoji")
          .eq("slug", slug)
          .eq("user_id", data.user.id)
          .then(({ data: r }) => {
            setUserReactions(r?.map(x => x.emoji) || []);
          });
      }
    });
  }, [slug]);

  const toggle = async (emoji: string) => {
    if (!user) return;
    if (userReactions.includes(emoji)) {
      await supabase.from("reactions").delete()
        .eq("user_id", user.id).eq("slug", slug).eq("emoji", emoji);
      setUserReactions(userReactions.filter(e => e !== emoji));
      setCounts({ ...counts, [emoji]: (counts[emoji] || 1) - 1 });
    } else {
      await supabase.from("reactions").insert({ user_id: user.id, slug, emoji });
      setUserReactions([...userReactions, emoji]);
      setCounts({ ...counts, [emoji]: (counts[emoji] || 0) + 1 });
    }
  };

  return (
    <div className="flex gap-2 mt-6">
      {EMOJIS.map(emoji => (
        <button
          key={emoji}
          onClick={() => toggle(emoji)}
          className={`px-3 py-1.5 rounded-full text-sm border transition ${
            userReactions.includes(emoji)
              ? "bg-teal-50 border-teal-300 dark:bg-teal-900/30 dark:border-teal-700"
              : "border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
          }`}
        >
          {emoji} {counts[emoji] || 0}
        </button>
      ))}
    </div>
  );
}
```

## Putting It All Together

At the bottom of every chapter page:

```tsx
<Reactions slug={`${series}/${fileSlug}`} />
<Comments slug={`${series}/${fileSlug}`} />
<ChapterComplete slug={`${series}/${fileSlug}`} />
```

The reader finishes a chapter, reacts with 🔥, leaves a comment, marks it complete. All persisted. All free.

---

## Series Complete (For Real This Time)

| Part | Chapters | What You Built |
|------|----------|---------------|
| Build | 0–7 | Static blog with interactive components |
| Polish | 8–11 | Dark mode, mobile, performance |
| Understand | 12–15 | JS, React, Hooks, TypeScript |
| Backend | 16–19 | Supabase: views, auth, progress, comments |

From a blank folder to a full interactive learning platform with user accounts, progress tracking, and community features. Still hosted on GitHub Pages. Still free.

The only limit now is content. Write more. Ship more. The platform handles the rest.
