# Chapter 9: Authentication — Middleware & Protected Routes

[← Chapter 8: Server Actions](chapter-08-server-actions.md) | [Chapter 10: Image Optimization →](chapter-10-images.md)

---

## The Task

Raj: "Three things. A login page. Protected routes (profile, review form, admin). And if someone visits a protected page without being logged in, redirect them to login — then back to where they were going."

---

## The Login Flow

```
User visits /profile (protected)
  → Middleware checks cookie → no token → redirect to /login?from=/profile
  → User logs in → API returns token → set httpOnly cookie
  → Redirect to /profile (the original destination)
```

---

## Middleware: The Gatekeeper

Middleware runs BEFORE every request. It can redirect, rewrite, or add headers. Perfect for auth guards.

```tsx
// src/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedPaths = ["/profile", "/admin", "/trails/*/review"];

function isProtected(pathname: string): boolean {
  return protectedPaths.some((pattern) => {
    const regex = new RegExp("^" + pattern.replace(/\*/g, "[^/]+") + "(/.*)?$");
    return regex.test(pathname);
  });
}

export function middleware(request: NextRequest) {
  const token = request.cookies.get("token")?.value;

  if (isProtected(request.nextUrl.pathname) && !token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/profile/:path*", "/admin/:path*", "/trails/:slug/review"],
};
```

This runs on the edge (or server) before the page renders. No JavaScript needed. No flash of protected content. The redirect happens at the HTTP level — fast and secure.

---

## The Login Page

```tsx
// src/app/login/page.tsx
import { LoginForm } from "./LoginForm";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Log In" };

export default function LoginPage() {
  return (
    <div className="max-w-sm mx-auto px-6 py-24">
      <h1 className="text-2xl font-bold text-center mb-8">Log in to TrailBlazer</h1>
      <LoginForm />
    </div>
  );
}
```

```tsx
// src/app/login/LoginForm.tsx
"use client";

import { useActionState } from "react";
import { login } from "./actions";
import { useSearchParams } from "next/navigation";

export function LoginForm() {
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("from") || "/";
  const loginWithRedirect = login.bind(null, redirectTo);
  const [state, formAction, isPending] = useActionState(loginWithRedirect, null);

  return (
    <form action={formAction} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Email</label>
        <input
          name="email"
          type="email"
          required
          className="w-full px-4 py-2 rounded-lg border"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Password</label>
        <input
          name="password"
          type="password"
          required
          className="w-full px-4 py-2 rounded-lg border"
        />
      </div>

      {state?.error && <p className="text-red-600 text-sm">{state.error}</p>}

      <button
        type="submit"
        disabled={isPending}
        className="w-full bg-emerald-600 text-white py-2 rounded-lg font-medium
                   hover:bg-emerald-700 disabled:opacity-50"
      >
        {isPending ? "Logging in..." : "Log In"}
      </button>
    </form>
  );
}
```

---

## The Login Server Action

```tsx
// src/app/login/actions.ts
"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export async function login(redirectTo: string, _prev: unknown, formData: FormData) {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  const res = await fetch("http://localhost:4000/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    return { error: "Invalid email or password" };
  }

  const { token } = await res.json();

  // Set httpOnly cookie (can't be read by JavaScript — XSS safe)
  const cookieStore = await cookies();
  cookieStore.set("token", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: "/",
  });

  redirect(redirectTo);
}
```

### Why httpOnly Cookies

| Storage | XSS Safe | Server Readable | Auto-sent |
|---|---|---|---|
| localStorage | ❌ JS can read | ❌ No | ❌ Manual |
| Regular cookie | ❌ JS can read | ✅ Yes | ✅ Yes |
| **httpOnly cookie** | **✅ JS can't read** | **✅ Yes** | **✅ Yes** |

httpOnly cookies can't be stolen by XSS attacks. They're automatically sent with every request. The server (middleware, server components, server actions) can read them. The browser JavaScript cannot.

---

## Reading the User in Server Components

```tsx
// src/lib/auth.ts
import { cookies } from "next/headers";
import type { User } from "@/types";

export async function getCurrentUser(): Promise<User | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get("token")?.value;
  if (!token) return null;

  const res = await fetch("http://localhost:4000/api/users/me", {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!res.ok) return null;
  return res.json();
}
```

```tsx
// src/app/profile/page.tsx
import { getCurrentUser } from "@/lib/auth";
import { redirect } from "next/navigation";

export default async function ProfilePage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login?from=/profile");

  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      <h1 className="text-2xl font-bold">Welcome, {user.name}</h1>
      <p className="text-stone-600 mt-1">{user.email}</p>
    </div>
  );
}
```

No loading state. No flash. The server checks auth, fetches user data, and sends complete HTML. If not authenticated, the redirect happens before any HTML is sent.

---

## Logout

```tsx
// src/app/logout/actions.ts
"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export async function logout() {
  const cookieStore = await cookies();
  cookieStore.delete("token");
  redirect("/");
}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
src/middleware.ts                │ Runs before every matched request
NextResponse.redirect()         │ HTTP redirect (no page render)
cookies().set(name, value, opts)│ Set httpOnly cookie
cookies().get(name)             │ Read cookie value
cookies().delete(name)          │ Remove cookie
config.matcher                  │ Which routes middleware applies to
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The trail pages have placeholder images. They're 4MB each, cause layout shift, and take forever on mobile. Mika: "Fix the images. They look terrible on slow connections."

---

[← Chapter 8: Server Actions](chapter-08-server-actions.md) | [Chapter 10: Image Optimization →](chapter-10-images.md)
