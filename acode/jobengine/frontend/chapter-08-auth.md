# Chapter 8: Who Are You? — Authentication & Protected Routes

[← Chapter 7: The Pipeline View](chapter-07-dag-visualization.md) | [Chapter 9: Performance →](chapter-09-performance.md)

---

## The Problem

The dashboard is public. Anyone on the network can see jobs, cancel them, resurrect dead ones. The backend now requires JWT auth (Chapter 9 backend), but the frontend sends no token. Every request returns 401.

## What You'll Build

- **Login page** — username/password form, calls `POST /auth/login`, stores JWT
- **Auth context** — `useAuth()` hook that provides `user`, `token`, `login()`, `logout()`
- **Protected routes** — redirect to `/login` if not authenticated
- **Token storage** — `localStorage` vs `sessionStorage` vs memory (tradeoffs)
- **Auto-refresh** — refresh the token before it expires
- **Role-based UI** — hide the "Delete" button if you're not ADMIN, disable "Submit" if you're VIEWER
- **Logout** — clear token, redirect to login

## Key Concepts

- **React Router** — `<Route>`, `<Navigate>`, `useNavigate`, route guards
- **Context + Provider pattern** — `AuthProvider` wrapping the app
- **JWT handling** — decode payload (without verifying), check expiry
- **`Authorization: Bearer` header** — attach token to every fetch call
- **Role-based rendering** — `{user.role === "ADMIN" && <DeleteButton />}`
- **Interceptors** — centralized fetch wrapper that adds auth headers and handles 401

---

[← Chapter 7: The Pipeline View](chapter-07-dag-visualization.md) | [Chapter 9: Performance →](chapter-09-performance.md)
