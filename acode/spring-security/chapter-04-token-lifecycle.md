# Chapter 4: Expired Tokens Still Work

[← Chapter 3: Session Stolen on Public WiFi](chapter-03-jwt.md) | [Chapter 5: User A Sees User B's Data →](chapter-05-method-security.md)

---

## The Vulnerability

> **HIGH: No Token Expiration Enforcement**
> JWT tokens have an `exp` claim set to 24 hours. But even after a user "logs out," the token remains valid. A stolen token works until it naturally expires. There's no revocation mechanism.

A user logs out. They feel safe. But the token they used 5 minutes ago? Still works. For 23 hours and 55 minutes.

---

## Short-Lived Access Tokens + Refresh Tokens

The solution: two tokens with different lifetimes.

| Token | Lifetime | Purpose | Storage |
|---|---|---|---|
| Access Token | 15 minutes | Authenticate API requests | Memory (JS variable) |
| Refresh Token | 7 days | Get new access tokens | HttpOnly cookie or secure storage |

```java
// src/main/java/com/vaultpay/security/TokenService.java
package com.vaultpay.security;

import org.springframework.stereotype.Service;
import java.util.UUID;

@Service
public class TokenService {

    private final JwtService jwtService;
    private final RefreshTokenRepository refreshTokenRepository;

    public TokenPair generateTokenPair(UserDetails userDetails) {
        String accessToken = jwtService.generateToken(userDetails, Duration.ofMinutes(15));
        String refreshToken = UUID.randomUUID().toString();

        // Store refresh token in DB (so we can revoke it)
        refreshTokenRepository.save(new RefreshToken(
            refreshToken,
            userDetails.getUsername(),
            Instant.now().plus(Duration.ofDays(7))
        ));

        return new TokenPair(accessToken, refreshToken);
    }

    public TokenPair refresh(String refreshToken) {
        RefreshToken stored = refreshTokenRepository.findByToken(refreshToken)
            .orElseThrow(() -> new InvalidTokenException("Invalid refresh token"));

        if (stored.getExpiresAt().isBefore(Instant.now())) {
            refreshTokenRepository.delete(stored);
            throw new InvalidTokenException("Refresh token expired");
        }

        // Rotate: delete old refresh token, issue new pair
        refreshTokenRepository.delete(stored);

        UserDetails user = userDetailsService.loadUserByUsername(stored.getUsername());
        return generateTokenPair(user);
    }

    public void revokeAllTokens(String username) {
        refreshTokenRepository.deleteAllByUsername(username);
    }
}
```

---

## The Refresh Endpoint

```java
@PostMapping("/api/auth/refresh")
public TokenResponse refresh(@RequestBody RefreshRequest request) {
    TokenPair pair = tokenService.refresh(request.refreshToken());
    return new TokenResponse(pair.accessToken(), pair.refreshToken());
}

@PostMapping("/api/auth/logout")
public ResponseEntity<Void> logout(@AuthenticationPrincipal UserDetails user) {
    tokenService.revokeAllTokens(user.getUsername());
    return ResponseEntity.noContent().build();
}

record RefreshRequest(String refreshToken) {}
record TokenResponse(String accessToken, String refreshToken) {}
```

---

## Token Revocation: The Blocklist

For immediate revocation (user changes password, account compromised), maintain a blocklist of revoked access tokens:

```java
@Service
public class TokenBlocklistService {

    private final RedisTemplate<String, String> redis;

    public void blockToken(String token, Instant expiration) {
        Duration ttl = Duration.between(Instant.now(), expiration);
        if (!ttl.isNegative()) {
            redis.opsForValue().set("blocked:" + token, "revoked", ttl);
        }
    }

    public boolean isBlocked(String token) {
        return Boolean.TRUE.equals(redis.hasKey("blocked:" + token));
    }
}
```

Add the check to the JWT filter:

```java
if (jwtService.isTokenValid(token, userDetails) && !blocklistService.isBlocked(token)) {
    // Set authentication...
}
```

The blocklist entry auto-expires when the token would have expired anyway (TTL = token's remaining lifetime). No unbounded growth.

---

## The Flow

```
  Login:
  POST /api/auth/login → {accessToken (15min), refreshToken (7d)}

  API calls:
  GET /api/merchants/123 + Authorization: Bearer <accessToken>

  Token expired:
  POST /api/auth/refresh + {refreshToken} → {new accessToken, new refreshToken}

  Logout:
  POST /api/auth/logout → deletes all refresh tokens + blocks current access token

  Password change:
  → revoke all refresh tokens + block all active access tokens
```

---

## Testing Token Lifecycle

```java
@Test
void expiredAccessToken_returns401() throws Exception {
    String token = jwtService.generateToken(user, Duration.ofMillis(-1)); // Already expired

    mockMvc.perform(get("/api/merchants/123")
            .header("Authorization", "Bearer " + token))
        .andExpect(status().isUnauthorized());
}

@Test
void revokedToken_returns401() throws Exception {
    String token = jwtService.generateToken(user, Duration.ofHours(1));
    blocklistService.blockToken(token, Instant.now().plus(Duration.ofHours(1)));

    mockMvc.perform(get("/api/merchants/123")
            .header("Authorization", "Bearer " + token))
        .andExpect(status().isUnauthorized());
}

@Test
void refreshToken_issuesNewPair() throws Exception {
    TokenPair original = tokenService.generateTokenPair(user);

    TokenPair refreshed = tokenService.refresh(original.refreshToken());

    assertThat(refreshed.accessToken()).isNotEqualTo(original.accessToken());
    assertThat(refreshed.refreshToken()).isNotEqualTo(original.refreshToken());
}
```

---

## Report to Jess

> **Token lifecycle implemented:**
> - Access tokens: 15 minutes (short-lived, limits damage window)
> - Refresh tokens: 7 days, stored in DB, rotated on use
> - Logout revokes all refresh tokens + blocks current access token
> - Token blocklist in Redis with auto-expiring TTL
> - Password change invalidates all sessions immediately
>
> Stolen token? Valid for max 15 minutes. After logout? Immediately invalid.

---

## What You Learned

- **Short-lived access tokens** (15 min) limit the damage window of a stolen token
- **Refresh tokens** are long-lived but stored server-side — revocable
- **Token rotation** — issue a new refresh token on each refresh (detect reuse = compromise)
- **Blocklist** for immediate revocation — Redis with TTL matching token expiration
- **Logout** = revoke refresh tokens + block access token
- The tradeoff: stateless (no DB check per request) vs revocable (DB check per request). Blocklist is the middle ground.

---

[Next: Chapter 5 — "User A Sees User B's Data" →](chapter-05-method-security.md)
