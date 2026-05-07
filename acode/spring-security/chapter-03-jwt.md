# Chapter 3: Session Stolen on Public WiFi

[← Chapter 2: Passwords in Plain Text](chapter-02-passwords.md) | [Chapter 4: Expired Tokens Still Work →](chapter-04-token-lifecycle.md)

---

## The Vulnerability

The pen tester's finding:

> **HIGH: Session Hijacking**
> Intercepted a session cookie (`JSESSIONID`) on an unencrypted coffee shop WiFi network. Replayed it from a different machine. Got full access to the victim's account. Session is server-side — no way to invalidate it without restarting the server.

The problem with server-side sessions:
- Session state stored in memory — doesn't scale horizontally
- Cookie-based — vulnerable to interception if not HTTPS-only
- Hard to invalidate across multiple server instances
- Doesn't work well for API clients (mobile apps, SPAs, third-party integrations)

Jess's directive:

> "Go stateless. JWT tokens. The server doesn't store session state. Each request carries its own proof of identity."

---

## JWT: Self-Contained Tokens

A JWT (JSON Web Token) has three parts:

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJtZXJjaGFudEBleGFtcGxlLmNvbSIsInJvbGVzIjpbIk1FUkNIQU5UIl0sImlhdCI6MTcxMDUwMDAwMCwiZXhwIjoxNzEwNTAzNjAwfQ.signature
│                      │                                                                                                                                    │
└── Header             └── Payload (claims)                                                                                                                  └── Signature
```

- **Header**: Algorithm used (`HS256`, `RS256`)
- **Payload**: Claims — who the user is, what roles they have, when it expires
- **Signature**: Proves the token wasn't tampered with (signed with a secret key)

The server doesn't store anything. It verifies the signature on each request. If valid → trust the claims.

---

## Add JWT Dependencies

```groovy
// build.gradle
implementation 'io.jsonwebtoken:jjwt-api:0.12.5'
runtimeOnly 'io.jsonwebtoken:jjwt-impl:0.12.5'
runtimeOnly 'io.jsonwebtoken:jjwt-jackson:0.12.5'
```

---

## The JWT Service

```java
// src/main/java/com/vaultpay/security/JwtService.java
package com.vaultpay.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.util.Date;
import java.util.List;
import java.util.function.Function;

@Service
public class JwtService {

    private final SecretKey signingKey;
    private final long expirationMs;

    public JwtService(
            @Value("${jwt.secret}") String secret,
            @Value("${jwt.expiration-ms:3600000}") long expirationMs) {
        // Key must be at least 256 bits for HS256
        this.signingKey = Keys.hmacShaKeyFor(secret.getBytes());
        this.expirationMs = expirationMs;
    }

    public String generateToken(UserDetails userDetails) {
        List<String> roles = userDetails.getAuthorities().stream()
            .map(Object::toString)
            .toList();

        return Jwts.builder()
            .subject(userDetails.getUsername())
            .claim("roles", roles)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expirationMs))
            .signWith(signingKey)
            .compact();
    }

    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public boolean isTokenValid(String token, UserDetails userDetails) {
        String username = extractUsername(token);
        return username.equals(userDetails.getUsername()) && !isTokenExpired(token);
    }

    private boolean isTokenExpired(String token) {
        Date expiration = extractClaim(token, Claims::getExpiration);
        return expiration.before(new Date());
    }

    private <T> T extractClaim(String token, Function<Claims, T> resolver) {
        Claims claims = Jwts.parser()
            .verifyWith(signingKey)
            .build()
            .parseSignedClaims(token)
            .getPayload();
        return resolver.apply(claims);
    }
}
```

### Configuration

```yaml
# application.yml
jwt:
  # In production: use a 256-bit random key from a secrets manager
  # NEVER commit this to source control
  secret: ${JWT_SECRET:this-is-a-development-key-that-must-be-at-least-32-bytes-long}
  expiration-ms: 3600000  # 1 hour
```

---

## The JWT Authentication Filter

This filter intercepts every request, extracts the JWT from the `Authorization` header, validates it, and sets the security context:

```java
// src/main/java/com/vaultpay/security/JwtAuthenticationFilter.java
package com.vaultpay.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    public JwtAuthenticationFilter(JwtService jwtService, UserDetailsService userDetailsService) {
        this.jwtService = jwtService;
        this.userDetailsService = userDetailsService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain filterChain) throws ServletException, IOException {

        String authHeader = request.getHeader("Authorization");

        // No token → skip this filter, let the chain continue
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        String token = authHeader.substring(7);  // Remove "Bearer " prefix

        try {
            String username = jwtService.extractUsername(token);

            // Only authenticate if not already authenticated in this request
            if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                UserDetails userDetails = userDetailsService.loadUserByUsername(username);

                if (jwtService.isTokenValid(token, userDetails)) {
                    UsernamePasswordAuthenticationToken authToken =
                        new UsernamePasswordAuthenticationToken(
                            userDetails, null, userDetails.getAuthorities());
                    authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));

                    SecurityContextHolder.getContext().setAuthentication(authToken);
                }
            }
        } catch (Exception e) {
            // Invalid token — don't authenticate, let the request continue unauthenticated
            // The authorization rules will reject it if the endpoint requires auth
        }

        filterChain.doFilter(request, response);
    }
}
```

---

## Wire It Into the Security Config

```java
// Updated SecurityConfig.java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtFilter;

    public SecurityConfig(JwtAuthenticationFilter jwtFilter) {
        this.jwtFilter = jwtFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            // Stateless — no server-side sessions
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            // Disable CSRF for stateless API (tokens are not cookies)
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            // Add JWT filter before the default authentication filter
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
```

Key changes:
- **`SessionCreationPolicy.STATELESS`** — no `JSESSIONID` cookie, no server-side session
- **CSRF disabled** — CSRF protection is for cookie-based auth; JWT in headers doesn't need it
- **JWT filter added** before Spring's default auth filter

---

## The Login Endpoint

```java
// src/main/java/com/vaultpay/controllers/AuthController.java
package com.vaultpay.controllers;

import com.vaultpay.security.JwtService;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final JwtService jwtService;

    public AuthController(AuthenticationManager authManager, JwtService jwtService) {
        this.authenticationManager = authManager;
        this.jwtService = jwtService;
    }

    @PostMapping("/login")
    public TokenResponse login(@RequestBody LoginRequest request) {
        Authentication auth = authenticationManager.authenticate(
            new UsernamePasswordAuthenticationToken(request.email(), request.password())
        );

        UserDetails userDetails = (UserDetails) auth.getPrincipal();
        String token = jwtService.generateToken(userDetails);

        return new TokenResponse(token);
    }

    record LoginRequest(String email, String password) {}
    record TokenResponse(String accessToken) {}
}
```

Don't forget the `AuthenticationManager` bean:

```java
@Bean
public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
    return config.getAuthenticationManager();
}
```

---

## Usage

```bash
# Login — get a token
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "merchant@vaultpay.com", "password": "SecureP@ss123"}'

# Response:
# {"accessToken": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOi..."}

# Use the token
curl http://localhost:8080/api/merchants/123 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOi..."
```

---

## Testing JWT Authentication

```java
@SpringBootTest
@AutoConfigureMockMvc
class JwtAuthenticationTest {

    @Autowired private MockMvc mockMvc;
    @Autowired private JwtService jwtService;

    @Test
    void validToken_grantsAccess() throws Exception {
        UserDetails user = User.builder()
            .username("merchant@test.com")
            .password("ignored")
            .roles("MERCHANT")
            .build();
        String token = jwtService.generateToken(user);

        mockMvc.perform(get("/api/merchants/123")
                .header("Authorization", "Bearer " + token))
            .andExpect(status().isOk());
    }

    @Test
    void noToken_returns401() throws Exception {
        mockMvc.perform(get("/api/merchants/123"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void tamperedToken_returns401() throws Exception {
        String token = jwtService.generateToken(/* ... */);
        String tampered = token.substring(0, token.length() - 5) + "XXXXX";

        mockMvc.perform(get("/api/merchants/123")
                .header("Authorization", "Bearer " + tampered))
            .andExpect(status().isUnauthorized());
    }
}
```

---

## Report to Jess

> **Pen test finding: session hijacking — fixed:**
> - Switched to stateless JWT authentication — no server-side sessions
> - No `JSESSIONID` cookie to intercept
> - Tokens are short-lived (1 hour) and signed with HMAC-SHA256
> - Tampered tokens rejected (signature verification fails)
> - Token in `Authorization` header — not vulnerable to CSRF
>
> The coffee shop attack? The intercepted cookie no longer exists. Tokens in headers aren't sent automatically by browsers.

Jess: "But what happens when a token is stolen? It's valid for an hour. And what about after the user logs out — can they still use the old token?"

---

## What You Learned

- **Server-side sessions** don't scale and are vulnerable to cookie theft
- **JWT** is stateless — the token carries all identity information, signed by the server
- **`SessionCreationPolicy.STATELESS`** disables session creation entirely
- **The JWT filter** extracts the token, validates the signature, and sets the security context
- **CSRF is disabled** for stateless APIs — CSRF attacks exploit cookies, not `Authorization` headers
- **Token structure**: header + payload (claims) + signature
- **Never store secrets in code** — use environment variables or a secrets manager
- **`OncePerRequestFilter`** ensures the filter runs exactly once per request
- The login endpoint is the only place credentials are exchanged — after that, only tokens

---

[Next: Chapter 4 — "Expired Tokens Still Work" →](chapter-04-token-lifecycle.md)
