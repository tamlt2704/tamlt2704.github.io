# Chapter 16: Adding Supabase — Your Free Backend

[← Chapter 15: TypeScript](/blog/nextjs-ghpages/chapter-15-typescript) | [Chapter 17: View Counts →](/blog/nextjs-ghpages/chapter-17-view-counts)

---

## The Missing Piece

Your blog is static. Beautiful, fast, interactive — but stateless. Every visit is a blank slate. You can't track which chapters are popular. You can't save a reader's quiz progress. You can't show "42 people read this."

You need a backend. But you don't want to manage a server.

Supabase gives you a Postgres database, authentication, and an API — all free, all managed. Your static site talks to it directly from the browser.

## What Supabase Is

Think of it as "Firebase but with Postgres." You get:

| Service        | What It Does                   | How You'll Use It                    |
| -------------- | ------------------------------ | ------------------------------------ |
| Database       | Postgres with a REST API       | View counts, user progress, comments |
| Auth           | Login with GitHub/Google/email | User accounts, saved state           |
| Storage        | File uploads                   | User avatars (optional)              |
| Realtime       | Live subscriptions             | Live view counter (optional)         |
| Edge Functions | Serverless code                | Webhook handlers (optional)          |

For our blog, we need: **Database** (view counts, progress) and **Auth** (login).

## Step 1: Create a Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up with GitHub (one click)
3. Click "New Project"
4. Name: `my-blog` (or anything)
5. Database password: generate a strong one, save it somewhere
6. Region: pick the closest to your readers
7. Click "Create new project" — takes ~2 minutes

## Step 2: Get Your Keys

Go to **Project Settings → API**. You need two values:

```
Project URL:  https://abcdefgh.supabase.co
anon key:     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

The `anon` key is safe to expose in client-side code. It only allows operations permitted by your Row Level Security policies (which we'll set up).

## Step 3: Install the Client

```bash
npm install @supabase/supabase-js
```

## Step 4: Create the Client

Create `lib/supabase.ts`:

```typescript
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseKey);
```

## Step 5: Environment Variables

Create `.env.local` (for local development):

```
NEXT_PUBLIC_SUPABASE_URL=https://abcdefgh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
```

The `NEXT_PUBLIC_` prefix makes them available in client-side code. Without it, Next.js keeps them server-only.

Add `.env.local` to `.gitignore` (it should already be there).

## Step 6: GitHub Actions Secrets

For deployment, add the same values as GitHub secrets:

1. Repo → Settings → Secrets and variables → Actions
2. Add `SUPABASE_URL` = your project URL
3. Add `SUPABASE_ANON_KEY` = your anon key

Update `.github/workflows/deploy.yml`:

```yaml
- run: npm run build
  env:
    NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
```

## Step 7: Create Your First Table

Go to **SQL Editor** in the Supabase dashboard. Run:

```sql
-- Page view counter
create table page_views (
  slug text primary key,
  count int default 0,
  last_viewed_at timestamptz default now()
);

-- Function to increment and return count
create or replace function increment_view(page_slug text)
returns int
language sql
as $$
  insert into page_views (slug, count, last_viewed_at)
  values (page_slug, 1, now())
  on conflict (slug)
  do update set
    count = page_views.count + 1,
    last_viewed_at = now()
  returning count;
$$;
```

## Step 8: Row Level Security

RLS is Supabase's permission system. Without it, anyone with your anon key could delete your data.

```sql
-- Enable RLS
alter table page_views enable row level security;

-- Anyone can read view counts
create policy "Public read" on page_views
  for select using (true);

-- Anyone can call the increment function (it uses security definer)
-- The function itself handles insert/update, so we don't need insert/update policies
-- for direct table access from anonymous users
```

For the `increment_view` function, change it to `security definer` so it bypasses RLS:

```sql
create or replace function increment_view(page_slug text)
returns int
language sql
security definer  -- runs with full privileges regardless of caller
as $$
  insert into page_views (slug, count, last_viewed_at)
  values (page_slug, 1, now())
  on conflict (slug)
  do update set
    count = page_views.count + 1,
    last_viewed_at = now()
  returning count;
$$;
```

Now anonymous users can increment views (via the function) and read counts, but can't directly modify or delete rows.

## Test It

In your browser console (or a component):

```javascript
import { supabase } from "@/lib/supabase";

// Increment a view
const { data } = await supabase.rpc("increment_view", { page_slug: "test-page" });
console.log(data); // 1 (first view)

// Read all views
const { data: views } = await supabase.from("page_views").select("*");
console.log(views); // [{ slug: "test-page", count: 1, last_viewed_at: "..." }]
```

If you see data, Supabase is working. Your static site now has a database.

## The Architecture

```
GitHub Pages (static HTML/JS)
    ↓ browser makes API calls
Supabase (managed Postgres + REST API)
    ↓ returns data as JSON
Your React components render it
```

No server to manage. No Docker. No SSH. Just a database with an API, and a static site that calls it.

## Cost

Free tier includes:

- 500MB database storage
- Unlimited API requests
- 50,000 monthly active auth users
- 1GB file storage
- 2 million edge function invocations

For a blog? You'll never pay a cent.

---

## What's Next

Supabase is connected. Chapter 17 builds the view counter component — showing readers how popular each chapter is, with real-time updates.
