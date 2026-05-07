# Chapter 1: Anyone Can Access Any Endpoint

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Passwords in Plain Text →](chapter-02-passwords.md)

---

## The Vulnerability

The pen tester's first finding:

> **CRITICAL: Broken Access Control**
> Any authenticated user can access `/api/admin/dashboard` and `/api/admin/users`. No role check. No authorization. Just "are you logged in?" — and that's it.

The current "security":

```java
// ❌ The old way — checking manually in every controller
@GetMapping("/api/admin/dashboard")
public ResponseEntity<?> dashboard(HttpServletRequest request) {
    if (request.getUserPrincipal() == null) {
        return ResponseEntity.status(401).build();
    }
    // No role check! Any logged-in user sees admin data.
    return ResponseEntity.ok(adminService.getDashboard());
}
```

This is security by wishful thinking. One forgotten `if` statement and the admin panel is wide open.

---

## How Spring Security Works: The Filter Chain

When a request arrives, it passes through a chain of **security filters** before reaching your controller:

```
  HTTP Request
       │
       ▼
  ┌─────────────────────────────────────────┐
  │         Security Filter Chain            │
  │                                         │
  │  [CORS Filter]                          │
  │       ↓                                 │
  │  [CSRF Filter]                          │
  │       ↓                                 │
  │  [Authentication Filter]                │
  │       ↓                                 │
  │  [Authorization Filter]                 │
  │       ↓                                 │
  │  [Exception Translation Filter]         │
  └─────────────────────────────────────────┘
       │
       ▼
  Your Controller (only if all filters pass)
```

You configure this chain declaratively. No manual `if` checks in controllers.

---

## Your First SecurityFilterChain

```java
// src/main/java/com/vaultpay/config/SecurityConfig.java
package com.vaultpay.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                // Public endpoints — no authentication needed
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/auth/login").permitAll()
                .requestMatchers("/api/auth/register").permitAll()

                // Admin endpoints — require ADMIN role
                .requestMatchers("/api/admin/**").hasRole("ADMIN")

                // Everything else — must be authenticated
                .anyRequest().authenticated()
            )
            .httpBasic(basic -> {});  // HTTP Basic for now (we'll switch to JWT in Ch3)

        return http.build();
    }
}
```

### What This Does

| Request | Rule | Result |
|---|---|---|
| `GET /api/public/health` | `permitAll()` | ✓ Anyone can access |
| `POST /api/auth/login` | `permitAll()` | ✓ Anyone can access |
| `GET /api/admin/dashboard` | `hasRole("ADMIN")` | ✗ 403 unless user has ADMIN role |
| `GET /api/merchants/123` | `authenticated()` | ✗ 401 unless logged in |
| `POST /api/transactions` | `authenticated()` | ✗ 401 unless logged in |

**Order matters.** Rules are evaluated top to bottom. The first match wins. Put specific rules before general ones.

---

## Request Matchers: Patterns and Methods

```java
.authorizeHttpRequests(auth -> auth
    // Match by HTTP method + path
    .requestMatchers(HttpMethod.GET, "/api/merchants/**").hasAnyRole("MERCHANT", "ADMIN")
    .requestMatchers(HttpMethod.POST, "/api/merchants").hasRole("ADMIN")

    // Match by path pattern
    .requestMatchers("/api/admin/**").hasRole("ADMIN")

    // Match by multiple patterns
    .requestMatchers("/api/reports/**", "/api/analytics/**").hasRole("ANALYST")

    // Catch-all
    .anyRequest().authenticated()
)
```

### Common Authorization Methods

| Method | Meaning |
|---|---|
| `.permitAll()` | Anyone — no auth needed |
| `.authenticated()` | Must be logged in (any role) |
| `.hasRole("ADMIN")` | Must have `ROLE_ADMIN` authority |
| `.hasAnyRole("ADMIN", "MANAGER")` | Must have one of these roles |
| `.hasAuthority("transaction:write")` | Must have this specific authority |
| `.denyAll()` | Nobody — useful for disabling endpoints |

---

## Testing Security Rules

```java
// src/test/java/com/vaultpay/config/SecurityConfigTest.java
package com.vaultpay.config;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class SecurityConfigTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void publicEndpoints_noAuthRequired() throws Exception {
        mockMvc.perform(get("/api/public/health"))
            .andExpect(status().isOk());
    }

    @Test
    void protectedEndpoints_returns401_whenNotAuthenticated() throws Exception {
        mockMvc.perform(get("/api/merchants/123"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void adminEndpoints_returns403_whenNotAdmin() throws Exception {
        mockMvc.perform(get("/api/admin/dashboard")
                .with(user("merchant@test.com").roles("MERCHANT")))
            .andExpect(status().isForbidden());
    }

    @Test
    void adminEndpoints_returns200_whenAdmin() throws Exception {
        mockMvc.perform(get("/api/admin/dashboard")
                .with(user("admin@test.com").roles("ADMIN")))
            .andExpect(status().isOk());
    }

    @Test
    void merchantEndpoints_accessible_withMerchantRole() throws Exception {
        mockMvc.perform(get("/api/merchants/123")
                .with(user("merchant@test.com").roles("MERCHANT")))
            .andExpect(status().isOk());
    }
}
```

`spring-security-test` provides `.with(user(...))` — inject a mock authenticated user without actually logging in. Test the rules, not the login mechanism.

---

## The Default Behavior: Secure by Default

If you add Spring Security to your project and do nothing else:

- Every endpoint requires authentication
- A random password is generated on startup (printed to console)
- Form login is enabled at `/login`
- HTTP Basic is enabled
- CSRF protection is on
- Session fixation protection is on
- Security headers are added (X-Frame-Options, etc.)

This is **secure by default**. You explicitly open things up — not the other way around.

---

## 401 vs 403: Know the Difference

| Code | Meaning | When |
|---|---|---|
| **401 Unauthorized** | "Who are you?" | No credentials provided, or credentials invalid |
| **403 Forbidden** | "I know who you are, but you can't do this" | Authenticated but lacking required role/authority |

Spring Security handles this automatically:
- No credentials → `AuthenticationEntryPoint` → 401
- Wrong role → `AccessDeniedHandler` → 403

### Custom Error Responses

```java
http
    .exceptionHandling(ex -> ex
        .authenticationEntryPoint((request, response, authException) -> {
            response.setStatus(401);
            response.setContentType("application/json");
            response.getWriter().write("""
                {"error": "unauthorized", "message": "Authentication required"}
                """);
        })
        .accessDeniedHandler((request, response, accessDeniedException) -> {
            response.setStatus(403);
            response.setContentType("application/json");
            response.getWriter().write("""
                {"error": "forbidden", "message": "Insufficient permissions"}
                """);
        })
    );
```

---

## The Controller (Clean — No Security Logic)

```java
// src/main/java/com/vaultpay/controllers/AdminController.java
package com.vaultpay.controllers;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin")
public class AdminController {

    @GetMapping("/dashboard")
    public Map<String, Object> dashboard() {
        // No security check here! The filter chain already verified ADMIN role.
        return Map.of(
            "totalMerchants", 2000,
            "totalTransactions", 1_500_000,
            "revenue", 4_500_000
        );
    }
}
```

The controller is clean. Security is handled by the filter chain. Separation of concerns.

---

## Report to Jess

> **Pen test finding #1 fixed:**
> - `SecurityFilterChain` configured with explicit rules per endpoint
> - Admin endpoints require `ROLE_ADMIN` — non-admins get 403
> - Public endpoints explicitly listed — everything else requires authentication
> - Custom error responses (JSON, no stack traces)
> - Tests prove: unauthenticated → 401, wrong role → 403, correct role → 200
>
> No more `if (user != null)` in controllers. Security is declarative and centralized.

Jess: "Good start. But the users in the database — their passwords are SHA-1 with no salt. If the database leaks, every password is cracked in minutes."

---

## What You Learned

- **SecurityFilterChain** is the central configuration — all security rules in one place
- **Request matchers** define which URLs require which roles/authorities
- **Order matters** — first matching rule wins, put specific before general
- **`permitAll()`** = public, **`authenticated()`** = logged in, **`hasRole()`** = specific role
- **401** = "who are you?", **403** = "you can't do this"
- **Secure by default** — Spring Security locks everything down; you explicitly open things
- **Controllers stay clean** — no security logic in business code
- **`spring-security-test`** provides mock users for testing rules without real authentication
- Always end with `.anyRequest().authenticated()` — don't leave gaps

---

[Next: Chapter 2 — "Passwords in Plain Text" →](chapter-02-passwords.md)
