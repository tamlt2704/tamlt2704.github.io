# Chapter 10: The Pen Test Passes

[← Chapter 9: API Keys for Machines](chapter-09-api-keys.md)

---

## The Task

Jess schedules the re-test:

> "The pen testers are coming back next week. Let's close every remaining finding: security headers, rate limiting, error message leakage, and audit logging. I want a clean report."

---

## Security Headers

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .headers(headers -> headers
            // Prevent clickjacking
            .frameOptions(frame -> frame.deny())
            // Prevent MIME type sniffing
            .contentTypeOptions(content -> {})
            // Enable HSTS (force HTTPS)
            .httpStrictTransportSecurity(hsts -> hsts
                .includeSubDomains(true)
                .maxAgeInSeconds(31536000))  // 1 year
            // Content Security Policy
            .contentSecurityPolicy(csp ->
                csp.policyDirectives("default-src 'self'; frame-ancestors 'none'"))
            // Prevent information leakage via Referer
            .referrerPolicy(referrer ->
                referrer.policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN))
            // Permissions Policy (disable unnecessary browser features)
            .permissionsPolicy(permissions ->
                permissions.policy("camera=(), microphone=(), geolocation=()"))
        );
    return http.build();
}
```

Response headers after configuration:

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; frame-ancestors 'none'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

---

## Error Message Sanitization

The pen tester noted: error messages leak internal details.

```java
// ❌ Before: leaks internal info
// "Error: org.postgresql.util.PSQLException: relation 'users' does not exist"
// "Error: java.lang.NullPointerException at com.vaultpay.services.MerchantService.java:47"

// ✓ After: generic messages externally, detailed logs internally
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(Exception ex) {
        // Log the full details internally
        log.error("Unhandled exception", ex);

        // Return generic message externally
        return ResponseEntity.status(500).body(
            new ErrorResponse("INTERNAL_ERROR", "An unexpected error occurred"));
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponse> handleAccessDenied(AccessDeniedException ex) {
        // Don't reveal WHY access was denied
        return ResponseEntity.status(403).body(
            new ErrorResponse("FORBIDDEN", "Insufficient permissions"));
    }

    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<ErrorResponse> handleAuthFailure(AuthenticationException ex) {
        // Don't reveal whether the email exists or the password is wrong
        return ResponseEntity.status(401).body(
            new ErrorResponse("UNAUTHORIZED", "Invalid credentials"));
    }

    @ExceptionHandler(NotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(NotFoundException ex) {
        return ResponseEntity.status(404).body(
            new ErrorResponse("NOT_FOUND", "Resource not found"));
    }

    record ErrorResponse(String code, String message) {}
}
```

**Key rule**: Never tell attackers *why* authentication failed. "Invalid credentials" — not "User not found" or "Wrong password."

---

## Rate Limiting

Protect the login endpoint from brute-force attacks:

```java
// src/main/java/com/vaultpay/security/RateLimitFilter.java
@Component
public class RateLimitFilter extends OncePerRequestFilter {

    // Simple in-memory rate limiter (use Redis in production)
    private final Map<String, Deque<Instant>> requestLog = new ConcurrentHashMap<>();
    private static final int MAX_REQUESTS = 10;
    private static final Duration WINDOW = Duration.ofMinutes(1);

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain filterChain) throws ServletException, IOException {

        // Only rate-limit auth endpoints
        if (!request.getRequestURI().startsWith("/api/auth")) {
            filterChain.doFilter(request, response);
            return;
        }

        String clientIp = getClientIp(request);
        Deque<Instant> timestamps = requestLog.computeIfAbsent(clientIp, k -> new ConcurrentLinkedDeque<>());

        // Remove old entries
        Instant cutoff = Instant.now().minus(WINDOW);
        timestamps.removeIf(t -> t.isBefore(cutoff));

        if (timestamps.size() >= MAX_REQUESTS) {
            response.setStatus(429);
            response.setHeader("Retry-After", "60");
            response.getWriter().write("{\"error\": \"Too many requests. Try again in 60 seconds.\"}");
            return;
        }

        timestamps.add(Instant.now());
        filterChain.doFilter(request, response);
    }

    private String getClientIp(HttpServletRequest request) {
        String forwarded = request.getHeader("X-Forwarded-For");
        return forwarded != null ? forwarded.split(",")[0].trim() : request.getRemoteAddr();
    }
}
```

---

## Audit Logging

Compliance needs to know: who did what, when, from where.

```java
@Component
public class SecurityAuditListener {

    private static final Logger audit = LoggerFactory.getLogger("SECURITY_AUDIT");

    @EventListener
    public void onAuthSuccess(AuthenticationSuccessEvent event) {
        String username = event.getAuthentication().getName();
        audit.info("LOGIN_SUCCESS user={}", username);
    }

    @EventListener
    public void onAuthFailure(AbstractAuthenticationFailureEvent event) {
        String username = event.getAuthentication().getName();
        String reason = event.getException().getClass().getSimpleName();
        audit.warn("LOGIN_FAILURE user={} reason={}", username, reason);
    }

    @EventListener
    public void onAccessDenied(AuthorizationDeniedEvent event) {
        audit.warn("ACCESS_DENIED user={} resource={}",
            event.getAuthentication().get().getName(),
            event.getSource());
    }
}
```

Configure a separate audit log file:

```xml
<!-- logback-spring.xml -->
<appender name="AUDIT_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <file>logs/security-audit.log</file>
    <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
        <fileNamePattern>logs/security-audit.%d{yyyy-MM-dd}.log</fileNamePattern>
        <maxHistory>90</maxHistory>
    </rollingPolicy>
    <encoder>
        <pattern>%d{ISO8601} %msg%n</pattern>
    </encoder>
</appender>

<logger name="SECURITY_AUDIT" level="INFO" additivity="false">
    <appender-ref ref="AUDIT_FILE" />
</logger>
```

---

## The Final Security Config

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain apiKeyChain(HttpSecurity http) throws Exception {
        http
            .securityMatcher(request -> request.getHeader("X-API-Key") != null)
            .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
            .addFilterBefore(apiKeyFilter, UsernamePasswordAuthenticationFilter.class)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(csrf -> csrf.disable())
            .headers(headers -> headers.frameOptions(f -> f.deny()));
        return http.build();
    }

    @Bean
    @Order(2)
    public SecurityFilterChain jwtChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(rateLimitFilter, UsernamePasswordAuthenticationFilter.class)
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfig()))
            .headers(headers -> headers
                .frameOptions(f -> f.deny())
                .contentTypeOptions(c -> {})
                .httpStrictTransportSecurity(h -> h.includeSubDomains(true).maxAgeInSeconds(31536000)))
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(jsonAuthEntryPoint())
                .accessDeniedHandler(jsonAccessDeniedHandler()));
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }

    @Bean
    public RoleHierarchy roleHierarchy() {
        return RoleHierarchyImpl.withRolePrefix("ROLE_")
            .role("ADMIN").implies("MANAGER")
            .role("MANAGER").implies("MERCHANT")
            .build();
    }
}
```

---

## The Pen Test Results

| # | Finding | Severity | Status |
|---|---|---|---|
| 1 | Any user accesses admin endpoints | CRITICAL | ✓ Fixed (Ch1: filter chain) |
| 2 | IDOR — access other merchants' data | CRITICAL | ✓ Fixed (Ch5: @PreAuthorize) |
| 3 | Passwords stored as SHA-1 | HIGH | ✓ Fixed (Ch2: BCrypt) |
| 4 | JWT tokens never expire | HIGH | ✓ Fixed (Ch4: 15-min tokens + refresh) |
| 5 | No CSRF protection | HIGH | ✓ Fixed (Ch7: stateless = immune) |
| 6 | Missing security headers | MEDIUM | ✓ Fixed (Ch10: all headers set) |
| 7 | Verbose error messages | MEDIUM | ✓ Fixed (Ch10: generic responses) |
| 8 | No rate limiting on login | LOW | ✓ Fixed (Ch10: 10 req/min) |
| 9 | CORS allows all origins | LOW | ✓ Fixed (Ch7: explicit allowlist) |

**Pen test result: PASS. Zero findings.**

---

## The Complete Security Architecture

```
  Request arrives
       │
       ▼
  [Rate Limit Filter] — 429 if too many requests
       │
       ▼
  [CORS Filter] — reject disallowed origins
       │
       ▼
  [Security Headers] — add protective headers
       │
       ▼
  [Auth Filter] — JWT or API Key
       │
       ├── No credentials → 401
       ├── Invalid credentials → 401
       └── Valid credentials → set SecurityContext
            │
            ▼
       [Authorization] — URL rules (filter chain)
            │
            ├── Wrong role → 403
            └── Correct role → continue
                 │
                 ▼
            [Method Security] — @PreAuthorize
                 │
                 ├── Ownership check fails → 403
                 └── Passes → execute method
                      │
                      ▼
                 [Controller] — business logic
                      │
                      ▼
                 [Audit Log] — record the action
```

---

## Report to Jess

> **Re-test complete. Clean report.**
>
> | Layer | Protection |
> |---|---|
> | Transport | HTTPS + HSTS |
> | Headers | CSP, X-Frame-Options, nosniff |
> | Rate limiting | 10 req/min on auth endpoints |
> | Authentication | JWT (users) + API keys (machines) |
> | Token lifecycle | 15-min access, 7-day refresh, revocation |
> | URL authorization | SecurityFilterChain rules |
> | Method authorization | @PreAuthorize + ownership checks |
> | Password storage | BCrypt (cost 12) |
> | Error handling | Generic messages externally, details in logs |
> | Audit | Every auth event logged with timestamp and IP |
> | CORS | Explicit origin allowlist |
>
> The $47-page pen test report? Zero findings on re-test.

---

## What You Learned (Series Recap)

1. **SecurityFilterChain** — centralized, declarative access rules
2. **BCrypt** — slow, salted password hashing (never SHA-1/MD5)
3. **JWT** — stateless authentication, no server-side sessions
4. **Token lifecycle** — short-lived access + long-lived refresh + revocation
5. **Method security** — `@PreAuthorize` for ownership and fine-grained checks
6. **Role hierarchy** — ADMIN implies MANAGER implies MERCHANT
7. **CSRF/CORS** — understand the attack to choose the right defense
8. **OAuth2** — delegate authentication to trusted providers
9. **API keys** — machine-to-machine auth with scoped permissions
10. **Hardening** — headers, rate limiting, error sanitization, audit logging

---

## Next Steps (If You Keep Going)

- **OAuth2 Resource Server** — validate tokens from an external authorization server
- **Spring Authorization Server** — build your own OAuth2/OIDC provider
- **mTLS** — mutual TLS for service-to-service authentication
- **Vault integration** — secrets management for keys and credentials
- **Security testing automation** — OWASP ZAP in CI/CD pipeline

But that's another series.

---

*Security isn't a feature. It's a property of the system. Every layer matters.*
