# Chapter 6: JWT Authentication

[← Chapter 5: Priority & Pause](/blog/spring-job-engine/chapter-05-priority-pause) | [Chapter 7: Audit →](/blog/spring-job-engine/chapter-07-audit)

---

## The Story

Anyone can submit jobs. Anyone can cancel them. The security team is not happy. You need: login, tokens, and role-based access.

## Step 1: JWT Token Provider

### Why JWT?

Traditional session-based auth stores state on the server (session ID → user). JWT is **stateless** — all user info lives inside the token itself:

```
┌─────────────────────────────────────────────────────┐
│  Header          │  Payload           │  Signature  │
│  {"alg":"HS256"} │  {"sub":"alice",   │  HMAC(      │
│                  │   "role":"ADMIN",  │   header +  │
│                  │   "exp":17000...}  │   payload,  │
│                  │                    │   secret)   │
└─────────────────────────────────────────────────────┘
```

**Why use JWT over sessions for a job engine:**

| Concern        | Session                                 | JWT                                       |
| -------------- | --------------------------------------- | ----------------------------------------- |
| Scalability    | Sticky sessions or shared store (Redis) | Any server can validate — no shared state |
| Microservices  | Must propagate session across services  | Token travels in header, self-contained   |
| Stateless REST | Violates REST principles                | Fits naturally — server stores nothing    |
| Performance    | DB/Redis lookup per request             | Just verify signature (CPU only)          |

**The tradeoff:** You can't revoke a JWT before it expires (unless you maintain a blacklist, which reintroduces state). For a job engine, short-lived tokens (24h) + refresh tokens is a good balance.

### How the flow works:

1. User calls `POST /api/auth/login` with credentials
2. Server validates, returns a signed JWT
3. Client sends `Authorization: Bearer <token>` on every request
4. Server verifies signature — no DB lookup needed
5. Token contains user email + role → used for access control

```java
// security/JwtTokenProvider.java
@Component
public class JwtTokenProvider {

    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.expiration:86400000}")  // 24h
    private long expiration;

    public String generateToken(String email, String role) {
        return Jwts.builder()
            .subject(email)
            .claim("role", role)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expiration))
            .signWith(Keys.hmacShaKeyFor(secret.getBytes()))
            .compact();
    }
```

### What are Claims?

Claims are key-value pairs stored in the JWT payload. They're the **data** the token carries.

**Registered claims** (standard, predefined by the JWT spec):

| Claim | Method          | Meaning                                              |
| ----- | --------------- | ---------------------------------------------------- |
| `sub` | `.subject()`    | Subject — who this token is about (user email/ID)    |
| `iat` | `.issuedAt()`   | Issued at — when the token was created               |
| `exp` | `.expiration()` | Expires — when the token becomes invalid             |
| `iss` | `.issuer()`     | Issuer — who created the token (e.g., "job-engine")  |
| `aud` | `.audience()`   | Audience — who the token is intended for             |
| `nbf` | `.notBefore()`  | Not before — token is invalid before this time       |
| `jti` | `.id()`         | JWT ID — unique identifier to prevent replay attacks |

**Custom claims** (your own data, added via `.claim(key, value)`):

```java
.claim("role", "ADMIN")           // user's role
.claim("department", "risk")      // business context
.claim("permissions", List.of("submit", "cancel"))  // fine-grained access
```

**Important rules:**

- Claims are **Base64-encoded, not encrypted** — anyone can decode and read them. Never put passwords or secrets in claims.
- Keep claims small — the token travels in every HTTP header. Large tokens = wasted bandwidth.
- The signature guarantees claims haven't been tampered with, but doesn't hide them.

```java
    public Claims parseToken(String token) {
        return Jwts.parser()
            .verifyWith(Keys.hmacShaKeyFor(secret.getBytes()))
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }
}
```

## Step 2: Auth Filter

```java
// security/JwtAuthFilter.java

// OncePerRequestFilter guarantees this filter runs exactly ONCE per HTTP request.
// Without it, a filter can execute multiple times if the request is forwarded
// or dispatched internally (e.g., error handling, async dispatch).
//
// It's called BEFORE your controller — part of the Spring Security filter chain:
//   HTTP Request → ... → JwtAuthFilter → ... → SecurityContext check → Controller
//
// If the token is valid, we set the SecurityContext so downstream code
// (controllers, @PreAuthorize) knows who the user is.
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtTokenProvider tokenProvider;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain chain) throws ServletException, IOException {
        // 1. Extract the Authorization header
        String header = request.getHeader("Authorization");

        if (header != null && header.startsWith("Bearer ")) {
            // 2. Strip "Bearer " prefix to get the raw token
            String token = header.substring(7);
            try {
                // 3. Verify signature + parse claims (throws if expired or tampered)
                Claims claims = tokenProvider.parseToken(token);

                // 4. Create an Authentication object with user identity + role
                var auth = new UsernamePasswordAuthenticationToken(
                    claims.getSubject(),       // principal (email)
                    null,                      // credentials (not needed, token already verified)
                    List.of(new SimpleGrantedAuthority("ROLE_" + claims.get("role")))
                );

                // 5. Store in SecurityContext — now accessible via @AuthenticationPrincipal
                SecurityContextHolder.getContext().setAuthentication(auth);
            } catch (JwtException e) {
                // Invalid/expired token — reject immediately
                response.setStatus(401);
                return;
            }
        }
        // 6. Continue the filter chain (next filter or controller)
        //    If no token was present, request proceeds unauthenticated
        //    (SecurityConfig decides if that's allowed for this endpoint)
        chain.doFilter(request, response);
    }
}
```

### How SecurityContextHolder Works

`SecurityContextHolder` is a **ThreadLocal-based storage** — it holds the current user's identity for the duration of a single request:

```
Thread-1 (Request A):  SecurityContext → { user: "alice@co.com", role: ADMIN }
Thread-2 (Request B):  SecurityContext → { user: "bob@co.com", role: USER }
Thread-3 (Request C):  SecurityContext → { empty, unauthenticated }
```

Each thread has its own isolated copy. No locking, no shared state.

**Lifecycle of a request:**

1. Request arrives → `SecurityContextHolder` is empty
2. `JwtAuthFilter` runs → calls `.setAuthentication(auth)` → context now has user info
3. Controller runs → reads context to know who's calling
4. Response sent → Spring clears the context automatically

**How to read it in your code:**

```java
// In any Spring-managed bean (controller, service, etc.)
String email = SecurityContextHolder.getContext()
    .getAuthentication().getName();

// Or use Spring's shortcut in controller parameters:
@GetMapping("/me")
public String me(@AuthenticationPrincipal String email) {
    return email;
}
```

**Why ThreadLocal?** HTTP servers reuse threads from a pool. ThreadLocal ensures Request A's user doesn't leak into Request B on the same thread — Spring clears it after each request completes.

## Step 3: Security Configuration

> **Note:** This replaces the starter SecurityConfig from Chapter 1. The full version adds JWT filter, method security, and role-based access.

```java
@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    private final JwtAuthFilter jwtFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(c -> c.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(a -> a
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/health").permitAll()
                .requestMatchers("/api/jobs/**").authenticated()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### BCrypt, Salt & Pepper

**Salt** — a random value generated per password and stored alongside the hash. BCrypt does this automatically — you don't manage it yourself:

```
$2a$10$N9qo8uLOickgx2ZMRZoMye  ←── algorithm + cost + salt (first 29 chars)
IjZAgcfl7p92ldGxad68LJZdL17lhWy  ←── the actual hash
```

Every call to `encode("same-password")` produces a different hash because the salt is random. `matches()` extracts the salt from the stored hash to verify.

**Pepper** — a secret key applied to all passwords _before_ hashing. Unlike salt, it's not stored in the database — it lives in config/env. If the DB is leaked, hashes are useless without the pepper.

> **Note:** The plain `BCryptPasswordEncoder` bean above is shown first for simplicity. The pepper version below is the recommended production approach — it adds an extra layer of defense against database leaks.

```java
@Bean
public PasswordEncoder passwordEncoder(@Value("${auth.pepper}") String pepper) {
    return new PasswordEncoder() {
        private final BCryptPasswordEncoder bcrypt = new BCryptPasswordEncoder();

        @Override
        public String encode(CharSequence raw) {
            return bcrypt.encode(raw + pepper);
        }

        @Override
        public boolean matches(CharSequence raw, String encoded) {
            return bcrypt.matches(raw + pepper, encoded);
        }
    };
}
```

```yaml
# application.yml
auth:
  pepper: ${AUTH_PEPPER} # from environment variable, never commit to git
```

| Concept    | Stored where                           | Protects against                                       |
| ---------- | -------------------------------------- | ------------------------------------------------------ |
| **Salt**   | In the hash itself (auto by BCrypt)    | Rainbow tables, identical passwords having same hash   |
| **Pepper** | Environment variable / secrets manager | Database leaks — attacker can't brute-force without it |

## Step 4: Login Endpoint

```java
// model/User.java
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String password;  // BCrypt hash

    private String role;  // "ADMIN", "USER"

    // getters, setters
}
```

```java
// repository/UserRepository.java
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
}
```

```java
// controller/LoginRequest.java
public record LoginRequest(String email, String password) {}
```

This is the **token issuer** — the only endpoint that creates JWTs. Here's how it fits in the full auth flow:

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│  Client  │──POST──▶│AuthController│──token──▶│   Client     │
│          │ /login  │ (this class) │          │ stores token │
└──────────┘         └──────────────┘         └──────┬───────┘
                                                      │
     Every subsequent request:                        │
     Authorization: Bearer <token>                    ▼
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│  Client  │──GET───▶│ JwtAuthFilter│──valid──▶│  Controller  │
│          │ /api/*  │ (verifies)   │          │ (your code)  │
└──────────┘         └──────────────┘         └──────────────┘
```

- **AuthController** = issues tokens (login). Called once.
- **JwtAuthFilter** = verifies tokens. Called on every request.

The controller validates credentials (email + password) against the database, then calls `tokenProvider.generateToken()` to create a signed JWT. After this, the server forgets about the user — no session stored. The client must send the token back on every future request.

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final UserRepository userRepo;
    private final PasswordEncoder encoder;
    private final JwtTokenProvider tokenProvider;

    @PostMapping("/login")
    public Map<String, String> login(@RequestBody LoginRequest request) {
        User user = userRepo.findByEmail(request.email())
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED));

        if (!encoder.matches(request.password(), user.getPassword())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED);
        }

        String token = tokenProvider.generateToken(user.getEmail(), user.getRole());
        return Map.of("token", token, "email", user.getEmail());
    }
}
```

## Step 5: Token Refresh

Access tokens expire (24h in our case). Instead of forcing users to log in again, we issue a **refresh token** — a long-lived token used solely to get a new access token.

### Why two tokens?

```
┌─────────────────────────────────────────────────────────────┐
│  Access Token          │  Refresh Token                     │
│  Short-lived (24h)     │  Long-lived (7 days)               │
│  Sent on every request │  Sent only to /api/auth/refresh    │
│  Stateless (no DB)     │  Stored in DB (revocable)          │
│  If stolen: limited    │  If stolen: revoke it in DB        │
│  damage window         │                                    │
└─────────────────────────────────────────────────────────────┘
```

**The flow:**

1. User logs in → gets both `accessToken` and `refreshToken`
2. Client uses `accessToken` for API calls
3. When `accessToken` expires (401 response), client calls `POST /api/auth/refresh`
4. Server validates the refresh token, issues a new access token
5. Optionally rotates the refresh token too (more secure)

### Refresh Token Entity

```java
@Entity
@Table(name = "refresh_tokens")
public class RefreshToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String token;

    @Column(nullable = false)
    private String email;

    @Column(nullable = false)
    private Instant expiresAt;

    private boolean revoked;
}
```

```java
public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {
    Optional<RefreshToken> findByTokenAndRevokedFalse(String token);
    void deleteByEmail(String email);  // revoke all on logout
}
```

### Generating Refresh Tokens

```java
@Service
public class RefreshTokenService {

    @Value("${jwt.refresh-expiration:604800000}")  // 7 days
    private long refreshExpiration;

    private final RefreshTokenRepository refreshTokenRepo;

    public RefreshToken createRefreshToken(String email) {
        RefreshToken rt = new RefreshToken();
        rt.setToken(UUID.randomUUID().toString());
        rt.setEmail(email);
        rt.setExpiresAt(Instant.now().plusMillis(refreshExpiration));
        rt.setRevoked(false);
        return refreshTokenRepo.save(rt);
    }

    public RefreshToken verifyAndRotate(String token) {
        RefreshToken rt = refreshTokenRepo.findByTokenAndRevokedFalse(token)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid refresh token"));

        if (rt.getExpiresAt().isBefore(Instant.now())) {
            refreshTokenRepo.delete(rt);
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Refresh token expired");
        }

        // Rotate: revoke old, issue new (prevents reuse attacks)
        rt.setRevoked(true);
        refreshTokenRepo.save(rt);

        return createRefreshToken(rt.getEmail());
    }

    @Transactional
    public void revokeAllForUser(String email) {
        refreshTokenRepo.deleteByEmail(email);
    }
}
```

### Updated Auth Controller

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final UserRepository userRepo;
    private final PasswordEncoder encoder;
    private final JwtTokenProvider tokenProvider;
    private final RefreshTokenService refreshTokenService;

    @PostMapping("/login")
    public Map<String, String> login(@RequestBody LoginRequest request) {
        User user = userRepo.findByEmail(request.email())
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED));

        if (!encoder.matches(request.password(), user.getPassword())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED);
        }

        String accessToken = tokenProvider.generateToken(user.getEmail(), user.getRole());
        RefreshToken refreshToken = refreshTokenService.createRefreshToken(user.getEmail());

        return Map.of(
            "accessToken", accessToken,
            "refreshToken", refreshToken.getToken(),
            "email", user.getEmail()
        );
    }

    @PostMapping("/refresh")
    public Map<String, String> refresh(@RequestBody Map<String, String> request) {
        String token = request.get("refreshToken");

        RefreshToken newRefreshToken = refreshTokenService.verifyAndRotate(token);

        User user = userRepo.findByEmail(newRefreshToken.getEmail())
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED));

        String accessToken = tokenProvider.generateToken(user.getEmail(), user.getRole());

        return Map.of(
            "accessToken", accessToken,
            "refreshToken", newRefreshToken.getToken()
        );
    }

    @PostMapping("/logout")
    public void logout(@AuthenticationPrincipal String email) {
        refreshTokenService.revokeAllForUser(email);
    }
}
```

### Client-Side: Automatic Refresh

On the frontend, intercept 401 responses and retry with a fresh token:

```javascript
// api.js — axios interceptor example
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const { data } = await api.post("/api/auth/refresh", {
        refreshToken: localStorage.getItem("refreshToken"),
      });

      localStorage.setItem("accessToken", data.accessToken);
      localStorage.setItem("refreshToken", data.refreshToken);

      originalRequest.headers.Authorization = `Bearer ${data.accessToken}`;
      return api(originalRequest);
    }

    return Promise.reject(error);
  },
);
```

### Security Considerations

| Strategy                                                            | What it prevents                                              |
| ------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Token rotation** (issue new refresh token each time)              | Stolen refresh token reuse — old one is revoked               |
| **Short access token TTL** (24h)                                    | Limits damage window if access token is stolen                |
| **DB-backed refresh tokens**                                        | Can revoke on logout, password change, or suspicious activity |
| **HttpOnly cookie** for refresh token (alternative to localStorage) | XSS can't steal the refresh token                             |

---

## Step 6: Getting Current User in Jobs

```java
// In JobService
public Job submit(JobRequest request) {
    String user = SecurityContextHolder.getContext()
        .getAuthentication().getName();  // email from JWT

    Job job = new Job();
    job.setSubmittedBy(user);
    // ...
}
```

## Step 7: Role-Based Access

```java
@PreAuthorize("hasRole('ADMIN') or @jobService.isOwner(#id, authentication.name)")
@PostMapping("/api/jobs/{id}/cancel")
public Job cancelJob(@PathVariable String id) {
    // Only admin or the job owner can cancel
}
```

Users can only cancel their own jobs. Admins can cancel anything.

---

[Chapter 7: Audit Trail →](/blog/spring-job-engine/chapter-07-audit)
