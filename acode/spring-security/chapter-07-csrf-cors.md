# Chapter 7: Cross-Site Request Forgery

[← Chapter 6: Admin Panel Accessed by Guessing URL](chapter-06-roles.md) | [Chapter 8: OAuth2 — Login with Google →](chapter-08-oauth2.md)

---

## The Vulnerability

> **HIGH: CSRF on State-Changing Endpoints**
> The pen tester crafted a malicious page that auto-submits a form to `POST /api/transactions`. When an authenticated user visits the page, their browser sends the request with their cookies attached. A transaction is created without the user's knowledge.

> **MEDIUM: CORS Allows All Origins**
> `Access-Control-Allow-Origin: *` means any website can make API calls to your backend. Combined with cookie-based auth, this is catastrophic.

---

## CSRF: The Attack

```html
<!-- Malicious page: evil.com/steal.html -->
<form action="https://api.vaultpay.com/api/transactions" method="POST" id="attack">
  <input type="hidden" name="amount" value="10000" />
  <input type="hidden" name="recipient" value="attacker-account" />
</form>
<script>document.getElementById('attack').submit();</script>
```

If the user is logged in with a cookie-based session, the browser automatically attaches the cookie. The server sees a valid session and processes the transaction.

### Why JWT in Headers Is Immune

Our API uses `Authorization: Bearer <token>` headers. Browsers don't automatically attach custom headers to cross-origin requests. CSRF attacks only work with **automatically-attached credentials** (cookies, HTTP Basic).

```java
// For pure API (JWT in headers): CSRF protection is unnecessary
http.csrf(csrf -> csrf.disable());
```

But if you also serve a web UI with cookie-based sessions (admin dashboard, for example), you need CSRF protection for those routes.

---

## CSRF Protection for Cookie-Based Routes

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .csrf(csrf -> csrf
            // Disable CSRF for stateless API endpoints (JWT auth)
            .ignoringRequestMatchers("/api/**")
            // Enable CSRF for web UI endpoints (cookie auth)
            .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
            .csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler())
        );
    return http.build();
}
```

The `CookieCsrfTokenRepository` sends a CSRF token in a cookie. The frontend reads it and includes it in a header (`X-XSRF-TOKEN`) on state-changing requests. The server verifies they match.

---

## CORS: Who Can Call Your API

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .cors(cors -> cors.configurationSource(corsConfigurationSource()));
    return http.build();
}

@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();

    // Only allow your frontend origins
    config.setAllowedOrigins(List.of(
        "https://dashboard.vaultpay.com",
        "https://merchant.vaultpay.com"
    ));

    // Allow specific methods
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));

    // Allow specific headers
    config.setAllowedHeaders(List.of("Authorization", "Content-Type", "X-XSRF-TOKEN"));

    // Allow credentials (cookies, Authorization header)
    config.setAllowCredentials(true);

    // Cache preflight response for 1 hour
    config.setMaxAge(3600L);

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", config);
    return source;
}
```

### What CORS Prevents

| Request From | Allowed? | Why |
|---|---|---|
| `https://dashboard.vaultpay.com` | ✓ | In allowed origins |
| `https://evil.com` | ✗ | Not in allowed origins |
| `http://localhost:3000` | ✗ | Not in allowed origins (add for dev) |

**Important**: CORS is enforced by the **browser**. API clients (curl, Postman, mobile apps) ignore CORS entirely. It only protects against browser-based attacks.

---

## SameSite Cookies

If you use cookies for anything (refresh tokens, CSRF tokens), set `SameSite`:

```yaml
# application.yml
server:
  servlet:
    session:
      cookie:
        same-site: strict    # Cookie only sent on same-site requests
        secure: true         # Only over HTTPS
        http-only: true      # Not accessible via JavaScript
```

| SameSite Value | Behavior |
|---|---|
| `Strict` | Cookie never sent on cross-site requests (safest) |
| `Lax` | Cookie sent on top-level navigations (GET only) |
| `None` | Cookie always sent (requires `Secure` flag) |

---

## Testing CORS

```java
@Test
void cors_allowsConfiguredOrigin() throws Exception {
    mockMvc.perform(options("/api/merchants")
            .header("Origin", "https://dashboard.vaultpay.com")
            .header("Access-Control-Request-Method", "GET"))
        .andExpect(status().isOk())
        .andExpect(header().string("Access-Control-Allow-Origin", "https://dashboard.vaultpay.com"));
}

@Test
void cors_rejectsUnknownOrigin() throws Exception {
    mockMvc.perform(options("/api/merchants")
            .header("Origin", "https://evil.com")
            .header("Access-Control-Request-Method", "GET"))
        .andExpect(header().doesNotExist("Access-Control-Allow-Origin"));
}
```

---

## Report to Jess

> **CSRF and CORS fixed:**
> - API endpoints (JWT auth): CSRF disabled — tokens in headers aren't vulnerable
> - Web UI endpoints (cookie auth): CSRF token required on state-changing requests
> - CORS restricted to `dashboard.vaultpay.com` and `merchant.vaultpay.com`
> - `Access-Control-Allow-Origin: *` replaced with explicit allowlist
> - Cookies: `SameSite=Strict`, `Secure`, `HttpOnly`
>
> The malicious form attack? Browser blocks the cross-origin request. Even if it didn't, no cookie is sent (SameSite=Strict).

---

## What You Learned

- **CSRF** exploits automatically-attached credentials (cookies) — not `Authorization` headers
- **JWT in headers is CSRF-immune** — browsers don't auto-attach custom headers cross-origin
- **CORS** controls which origins can make browser-based requests to your API
- **`Access-Control-Allow-Origin: *`** is almost always wrong — use an explicit allowlist
- **SameSite cookies** prevent cookies from being sent on cross-site requests
- CORS is browser-enforced — API clients (curl, mobile apps) bypass it entirely
- Defense layers: CORS (browser) + CSRF tokens (server) + SameSite cookies (browser)

---

[Next: Chapter 8 — "OAuth2 — Login with Google" →](chapter-08-oauth2.md)
