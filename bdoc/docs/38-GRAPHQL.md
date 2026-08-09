# Chapter 38: GraphQL — Query Exactly What You Need

## What you'll learn

- What GraphQL is and how it differs from REST
- Schema design: types, queries, mutations, subscriptions
- Writing queries and mutations (the client perspective)
- Building a GraphQL API with Spring Boot (server)
- Consuming GraphQL in Next.js (client)
- Resolvers, DataLoaders, and the N+1 problem
- Pagination, filtering, and error handling
- Authentication and authorisation in GraphQL
- When to use GraphQL vs REST

---

## PART 1: Fundamentals

## 38.1 The problem GraphQL solves

**REST problem: over-fetching and under-fetching**

```
REST: GET /api/users/123
Response: { id, name, email, phone, address, avatar, bio, createdAt, settings... }
→ You only needed name and email. Wasted bandwidth.

REST: GET /api/users/123/posts
REST: GET /api/users/123/followers
REST: GET /api/users/123/notifications
→ Three round trips to build one page. Slow.
```

**GraphQL solution: ask for exactly what you need in one request**

```graphql
query {
  user(id: "123") {
    name
    email
    posts(first: 5) {
      title
      createdAt
    }
    followersCount
  }
}
```

One request, one response, only the fields you asked for.

## 38.2 GraphQL vs REST

| Aspect | REST | GraphQL |
|--------|------|---------|
| Endpoints | Multiple (`/users`, `/posts`, `/comments`) | Single (`/graphql`) |
| Data shape | Server decides response shape | Client decides what fields to fetch |
| Over-fetching | Common (get all fields even if you need 2) | Impossible (you specify every field) |
| Under-fetching | Common (need multiple requests) | Rare (nested queries in one request) |
| Versioning | `/api/v1/`, `/api/v2/` | Evolve schema (add fields, deprecate old ones) |
| Caching | Easy (HTTP cache by URL) | Harder (single URL, need query-level cache) |
| File upload | Simple (multipart) | Complex (spec exists but awkward) |
| Real-time | WebSocket/SSE (custom) | Subscriptions (built-in) |
| Tooling | Postman, curl | GraphiQL, Apollo Studio, Playground |

## 38.3 Core concepts

```
┌─────────────────────────────────────────────────────────────┐
│                      SCHEMA                                  │
│  (contract between client and server)                        │
│                                                              │
│  Types:     what data looks like (User, Post, Comment)       │
│  Queries:   what you can READ (getUser, listPosts)           │
│  Mutations: what you can WRITE (createPost, deleteUser)      │
│  Subscriptions: what you can LISTEN to (newMessage)          │
└─────────────────────────────────────────────────────────────┘
         │ defined by server
         ▼
┌─────────────────────────────────────────────────────────────┐
│                     RESOLVERS                                │
│  (functions that fetch data for each field)                   │
│                                                              │
│  Query.user(id) → fetch from DB                              │
│  User.posts    → fetch posts for this user                   │
│  Post.author   → fetch author for this post                  │
└─────────────────────────────────────────────────────────────┘
         │ requested by client
         ▼
┌─────────────────────────────────────────────────────────────┐
│                      QUERY                                   │
│  (client request — "give me this shape of data")             │
│                                                              │
│  query { user(id: "1") { name, posts { title } } }           │
└─────────────────────────────────────────────────────────────┘
```

---

## PART 2: Schema Design

## 38.4 Type system

```graphql
# schema.graphql

# Object types (your domain entities)
type User {
  id: ID!                    # ! means non-nullable
  name: String!
  email: String!
  avatar: String
  bio: String
  posts: [Post!]!            # list of non-null Posts (list itself non-null)
  followers: [User!]!
  followersCount: Int!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  published: Boolean!
  author: User!
  comments: [Comment!]!
  tags: [String!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Comment {
  id: ID!
  text: String!
  author: User!
  post: Post!
  createdAt: DateTime!
}

# Enum types
enum PostStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

enum SortOrder {
  ASC
  DESC
}

# Input types (for mutations — what the client sends)
input CreatePostInput {
  title: String!
  content: String!
  tags: [String!]
  published: Boolean = false    # default value
}

input UpdatePostInput {
  title: String
  content: String
  tags: [String!]
  published: Boolean
}

input PostFilter {
  authorId: ID
  published: Boolean
  tags: [String!]
  search: String
}

# Pagination
type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PostEdge {
  node: Post!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# Custom scalars
scalar DateTime
scalar JSON
```

## 38.5 Queries and Mutations

```graphql
# Root query type — entry points for reading data
type Query {
  # Single item
  user(id: ID!): User
  post(id: ID!): Post

  # Lists with filtering and pagination
  posts(
    filter: PostFilter
    first: Int = 10
    after: String
    orderBy: String = "createdAt"
    order: SortOrder = DESC
  ): PostConnection!

  # Search
  search(query: String!, limit: Int = 20): [SearchResult!]!

  # Current user (from auth context)
  me: User
}

# Root mutation type — entry points for writing data
type Mutation {
  # Auth
  login(email: String!, password: String!): AuthPayload!
  register(name: String!, email: String!, password: String!): AuthPayload!

  # Posts
  createPost(input: CreatePostInput!): Post!
  updatePost(id: ID!, input: UpdatePostInput!): Post!
  deletePost(id: ID!): Boolean!
  publishPost(id: ID!): Post!

  # Comments
  addComment(postId: ID!, text: String!): Comment!
  deleteComment(id: ID!): Boolean!

  # Social
  followUser(userId: ID!): User!
  unfollowUser(userId: ID!): User!
}

# Subscriptions — real-time updates
type Subscription {
  postPublished: Post!
  commentAdded(postId: ID!): Comment!
  userOnlineStatus(userId: ID!): Boolean!
}

# Response types
type AuthPayload {
  token: String!
  user: User!
}

union SearchResult = User | Post | Comment
```

---

## PART 3: Client Queries

## 38.6 Writing queries

```graphql
# Simple query
query GetUser {
  user(id: "123") {
    name
    email
    avatar
  }
}

# Query with variables (parameterised — reusable)
query GetUser($userId: ID!) {
  user(id: $userId) {
    name
    email
    posts(first: 5) {
      title
      createdAt
    }
  }
}
# Variables: { "userId": "123" }

# Multiple queries in one request
query DashboardData {
  me {
    name
    avatar
  }
  posts(first: 10, filter: { published: true }) {
    edges {
      node {
        title
        createdAt
        author {
          name
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }
}

# Fragments — reusable field selections
fragment PostPreview on Post {
  id
  title
  createdAt
  author {
    name
    avatar
  }
  tags
}

query Feed {
  posts(first: 20) {
    edges {
      node {
        ...PostPreview
        content    # additional fields beyond fragment
      }
    }
  }
}
```

## 38.7 Mutations

```graphql
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    id
    title
    content
    published
    createdAt
  }
}
# Variables:
# {
#   "input": {
#     "title": "GraphQL is Great",
#     "content": "Here's why...",
#     "tags": ["graphql", "api"],
#     "published": true
#   }
# }

mutation Login($email: String!, $password: String!) {
  login(email: $email, password: $password) {
    token
    user {
      id
      name
    }
  }
}
```

---

## PART 4: Spring Boot Server

## 38.8 Setup

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-graphql</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  graphql:
    graphiql:
      enabled: true    # interactive playground at /graphiql
    schema:
      locations: classpath:graphql/   # where .graphqls files live
```

Place your schema at `src/main/resources/graphql/schema.graphqls`.

## 38.9 Resolvers (Controllers)

```java
@Controller
public class PostController {

    private final PostService postService;

    // Query resolver: posts(filter, first, after, orderBy, order)
    @QueryMapping
    public PostConnection posts(
            @Argument PostFilter filter,
            @Argument int first,
            @Argument String after,
            @Argument String orderBy,
            @Argument SortOrder order
    ) {
        return postService.getPosts(filter, first, after, orderBy, order);
    }

    // Query resolver: post(id)
    @QueryMapping
    public Post post(@Argument String id) {
        return postService.getPost(id)
                .orElseThrow(() -> new NotFoundException("Post not found: " + id));
    }

    // Mutation resolver: createPost(input)
    @MutationMapping
    public Post createPost(@Argument CreatePostInput input, @AuthenticationPrincipal User user) {
        return postService.createPost(input, user);
    }

    // Mutation resolver: deletePost(id)
    @MutationMapping
    public boolean deletePost(@Argument String id, @AuthenticationPrincipal User user) {
        return postService.deletePost(id, user);
    }

    // Field resolver: Post.author (resolves the author for each post)
    @SchemaMapping(typeName = "Post", field = "author")
    public User author(Post post) {
        return userService.getUser(post.getAuthorId());
    }

    // Field resolver: Post.comments
    @SchemaMapping(typeName = "Post", field = "comments")
    public List<Comment> comments(Post post) {
        return commentService.getCommentsForPost(post.getId());
    }
}
```

## 38.10 DataLoader — solving the N+1 problem

```java
// ❌ N+1 problem: fetching posts, then 1 query per post to get author
// 10 posts → 1 + 10 = 11 queries!

// Query 1: SELECT * FROM posts LIMIT 10
// Query 2: SELECT * FROM users WHERE id = 1   (author of post 1)
// Query 3: SELECT * FROM users WHERE id = 2   (author of post 2)
// ...
// Query 11: SELECT * FROM users WHERE id = 10  (author of post 10)

// ✅ DataLoader: batch all author fetches into ONE query
// Query 1: SELECT * FROM posts LIMIT 10
// Query 2: SELECT * FROM users WHERE id IN (1, 2, 3, ..., 10)  ← ONE query!
```

```java
@Configuration
public class DataLoaderConfig {

    @Bean
    public BatchLoaderRegistry batchLoaderRegistry(UserService userService) {
        return new BatchLoaderRegistry() {
            @Override
            public void registerBatchLoaders(BatchLoaderRegistry registry) {
                registry.forTypePair(String.class, User.class)
                    .registerBatchLoader((userIds, env) ->
                        Flux.fromIterable(userService.getUsersByIds(userIds))
                    );
            }
        };
    }
}

// Use in resolver
@Controller
public class PostController {

    @SchemaMapping(typeName = "Post", field = "author")
    public CompletableFuture<User> author(Post post, DataLoader<String, User> userDataLoader) {
        return userDataLoader.load(post.getAuthorId());
        // DataLoader batches all .load() calls in the same request
        // into one userService.getUsersByIds([id1, id2, ...]) call
    }
}
```

## 38.11 Error handling

```java
@ControllerAdvice
public class GraphQLExceptionHandler {

    @GraphQlExceptionHandler
    public GraphQLError handleNotFound(NotFoundException ex) {
        return GraphQLError.newError()
            .errorType(ErrorType.NOT_FOUND)
            .message(ex.getMessage())
            .build();
    }

    @GraphQlExceptionHandler
    public GraphQLError handleValidation(ConstraintViolationException ex) {
        return GraphQLError.newError()
            .errorType(ErrorType.BAD_REQUEST)
            .message("Validation failed")
            .extensions(Map.of("violations",
                ex.getConstraintViolations().stream()
                    .map(v -> Map.of("field", v.getPropertyPath().toString(), "message", v.getMessage()))
                    .toList()
            ))
            .build();
    }

    @GraphQlExceptionHandler
    public GraphQLError handleAuth(AccessDeniedException ex) {
        return GraphQLError.newError()
            .errorType(ErrorType.UNAUTHORIZED)
            .message("You don't have permission to perform this action")
            .build();
    }
}
```

GraphQL error response format:
```json
{
  "data": { "post": null },
  "errors": [
    {
      "message": "Post not found: 999",
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["post"],
      "extensions": { "errorType": "NOT_FOUND" }
    }
  ]
}
```

> **GraphQL ALWAYS returns 200 OK** (even on errors). Errors are in the response body, not the HTTP status code.

---

## PART 5: Next.js Client

## 38.12 Fetch GraphQL from Next.js (simple)

```ts
// lib/graphql.ts
const GRAPHQL_URL = process.env.NEXT_PUBLIC_GRAPHQL_URL || "http://localhost:8080/graphql";

export async function graphqlFetch<T>(
  query: string,
  variables?: Record<string, unknown>,
  token?: string
): Promise<T> {
  const res = await fetch(GRAPHQL_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify({ query, variables }),
  });

  const json = await res.json();

  if (json.errors) {
    throw new Error(json.errors[0].message);
  }

  return json.data;
}
```

```tsx
// app/posts/page.tsx (Server Component — fetches at build/request time)
import { graphqlFetch } from "@/lib/graphql";

const GET_POSTS = `
  query GetPosts($first: Int!, $after: String) {
    posts(first: $first, after: $after, filter: { published: true }) {
      edges {
        node {
          id
          title
          createdAt
          author { name avatar }
          tags
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
      totalCount
    }
  }
`;

export default async function PostsPage() {
  const data = await graphqlFetch<{ posts: PostConnection }>(GET_POSTS, { first: 10 });

  return (
    <div>
      <h1>Posts ({data.posts.totalCount})</h1>
      {data.posts.edges.map(({ node: post }) => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>By {post.author.name}</p>
        </article>
      ))}
    </div>
  );
}
```

## 38.13 With Apollo Client (full-featured)

```bash
npm install @apollo/client graphql
```

```tsx
// lib/apollo.ts
"use client";

import { ApolloClient, InMemoryCache, HttpLink, from } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";

const httpLink = new HttpLink({
  uri: process.env.NEXT_PUBLIC_GRAPHQL_URL,
});

const authLink = setContext((_, { headers }) => {
  const token = sessionStorage.getItem("token");
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
    },
  };
});

export const apolloClient = new ApolloClient({
  link: from([authLink, httpLink]),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          posts: {
            // Cursor-based pagination merge
            keyArgs: ["filter"],
            merge(existing, incoming) {
              if (!existing) return incoming;
              return {
                ...incoming,
                edges: [...existing.edges, ...incoming.edges],
              };
            },
          },
        },
      },
    },
  }),
});
```

```tsx
// components/PostList.tsx
"use client";

import { useQuery, useMutation, gql } from "@apollo/client";

const GET_POSTS = gql`
  query GetPosts($first: Int!, $after: String) {
    posts(first: $first, after: $after) {
      edges {
        node {
          id
          title
          author { name }
        }
      }
      pageInfo { hasNextPage, endCursor }
    }
  }
`;

const DELETE_POST = gql`
  mutation DeletePost($id: ID!) {
    deletePost(id: $id)
  }
`;

export default function PostList() {
  const { data, loading, error, fetchMore } = useQuery(GET_POSTS, {
    variables: { first: 10 },
  });

  const [deletePost] = useMutation(DELETE_POST, {
    refetchQueries: [{ query: GET_POSTS, variables: { first: 10 } }],
  });

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div>
      {data.posts.edges.map(({ node: post }) => (
        <div key={post.id}>
          <h3>{post.title}</h3>
          <button onClick={() => deletePost({ variables: { id: post.id } })}>
            Delete
          </button>
        </div>
      ))}

      {data.posts.pageInfo.hasNextPage && (
        <button onClick={() => fetchMore({
          variables: { after: data.posts.pageInfo.endCursor },
        })}>
          Load More
        </button>
      )}
    </div>
  );
}
```

---

## PART 6: Best Practices

## 38.14 Pagination — Cursor vs Offset

```graphql
# ❌ Offset-based (breaks with real-time data — items shift when new data is inserted)
posts(limit: 10, offset: 20)

# ✅ Cursor-based (stable — uses opaque cursor pointing to last item)
posts(first: 10, after: "abc123cursor")
```

Cursor is typically a base64-encoded ID or timestamp. Client doesn't know what it contains — just passes it back for "next page."

## 38.15 When to use GraphQL vs REST

**Use GraphQL when:**
- Multiple clients need different data shapes (mobile app needs less than web)
- Frontend team needs to iterate without waiting for backend changes
- Complex nested relationships (user → posts → comments → author)
- You want strong typing and self-documenting API

**Use REST when:**
- Simple CRUD with predictable responses
- File upload/download is primary use case
- You need aggressive HTTP caching (CDN cache by URL)
- Your team is small and frontend/backend are tightly coupled
- Webhook/callback integrations (third parties expect REST)

**Use both:**
- REST for simple public API / webhooks / file operations
- GraphQL for complex frontend data needs

## 38.16 Security considerations

```java
// 1. Query depth limiting (prevent deeply nested attacks)
@Bean
public RuntimeWiringConfigurer depthLimiter() {
    return wiringBuilder -> wiringBuilder
        .queryComplexity(new MaxQueryDepthInstrumentation(10)); // max 10 levels deep
}

// 2. Query complexity/cost analysis
// Assign cost per field, reject queries exceeding budget
// Post.comments costs 10, User.posts costs 5, scalar fields cost 1
// Budget: 100 per query

// 3. Rate limiting (per query, not just per request)
// A single GraphQL request can be equivalent to 100 REST requests

// 4. Disable introspection in production
spring.graphql.schema.introspection.enabled=false

// 5. Input validation (same as REST — validate everything)
```

---

## Summary

✅ GraphQL fundamentals: schema, types, queries, mutations, subscriptions
✅ Schema design: object types, enums, inputs, connections (pagination), unions
✅ Writing queries: variables, fragments, nested selections, multiple queries in one request
✅ Spring Boot server: @QueryMapping, @MutationMapping, @SchemaMapping, DataLoaders
✅ N+1 problem: DataLoader batches individual fetches into one bulk query
✅ Error handling: GraphQLError with extensions, always HTTP 200
✅ Next.js client: simple fetch wrapper + Apollo Client (cache, pagination, mutations)
✅ Best practices: cursor pagination, depth limiting, when to use GraphQL vs REST

## Key takeaways

**GraphQL is a contract between frontend and backend.** The schema defines what's possible. The client chooses what it needs. The server resolves exactly what's asked for.

**DataLoader is non-negotiable.** Without it, every nested field triggers a separate database query (N+1). With it, all queries at the same depth are batched automatically.

**GraphQL doesn't replace REST — it complements it.** Use GraphQL where clients need flexibility (complex UIs with varying data needs). Use REST where simplicity and caching matter (public APIs, webhooks, file uploads).

**The schema IS your API documentation.** GraphQL is self-documenting via introspection. Tools like GraphiQL let developers explore the API interactively — no Swagger/OpenAPI setup needed.

---

→ [Back to Chapter 37: Java Collections](./37-JAVA-COLLECTIONS.md)
