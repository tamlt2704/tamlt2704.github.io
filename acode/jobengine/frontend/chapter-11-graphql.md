# Chapter 11: REST Is Chatty — GraphQL

[← Chapter 10: Mobile](chapter-10-mobile.md) | [Chapter 12: Ship It →](chapter-12-deploy.md)

---

## The Problem

The job list page makes 3 requests: `GET /jobs`, `GET /stats`, `GET /workers`. The job detail page makes 2 more: `GET /jobs/:id`, `GET /audit?entityId=:id`. The DAG page makes 3: the workflow, the jobs, the edges.

Every page is a waterfall of REST calls. On mobile with a slow connection, the dashboard takes 4 seconds to load. Old Greg: "You're over-fetching. The job list doesn't need the full audit trail. And you're under-fetching — you need 3 calls to render one page."

GraphQL solves both: ask for exactly what you need, in one request.

## What You'll Build

- **Apollo Client setup** — connect to a GraphQL endpoint on the backend
- **Queries** — `useQuery` to fetch jobs with exactly the fields you need
- **Mutations** — `useMutation` for cancel, pause, resume with cache updates
- **Subscriptions** — replace SSE with GraphQL subscriptions for real-time updates
- **Fragments** — reusable field selections across queries
- **Cache management** — Apollo's normalized cache, optimistic updates

## Key Concepts

- **GraphQL vs REST** — when each is better, not "GraphQL is always better"
- **Apollo Client** — `useQuery`, `useMutation`, `useSubscription`
- **Schema-first thinking** — the query defines the shape of the response
- **Normalized cache** — Apollo stores entities by ID, updates propagate automatically
- **Code generation** — `graphql-codegen` to generate TypeScript types from the schema
- **Error handling** — partial data, network errors, GraphQL errors

---

[← Chapter 10: Mobile](chapter-10-mobile.md) | [Chapter 12: Ship It →](chapter-12-deploy.md)
