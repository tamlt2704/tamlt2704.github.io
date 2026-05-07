# Chapter 2: Passwords Stored in Plain SHA-1

[← Chapter 1: Anyone Can Access Any Endpoint](chapter-01-filter-chain.md) | [Chapter 3: Session Stolen on Public WiFi →](chapter-03-jwt.md)

---

## The Vulnerability

The pen tester's second finding:

> **HIGH: Weak Password Storage**
> Passwords are stored as unsalted SHA-1 hashes. A leaked database dump would expose all passwords within hours using rainbow tables. SHA-1 is not a password hashing algorithm — it's a checksum.

The current code:

```java
// ❌ How passwords are stored today
String hashedPassword = DigestUtils.sha1Hex(rawPassword);
// Result: "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8" (this is "password")
// Rainbow table lookup: instant crack
```

---

## Why SHA-1 (and MD5, SHA-256) Are Wrong for Passwords

Fast hashes are designed to be fast. That's the problem.

| Algorithm | Hashes/second (modern GPU) | Time to crack "password123" |
|---|---|---|
| SHA-1 | 10 billion | < 1 second |
| SHA-256 | 5 billion | < 1 second |
| BCrypt (cost 12) | 13,000 | 77,000 seconds (~21 hours) |

Password hashing algorithms are intentionally **slow**. They make brute-force attacks computationally expensive.

---

## BCrypt: The Right Way

```java
// src/main/java/com/vaultpay/config/SecurityConfig.java
package com.vaultpay.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);  // Cost factor 12 (~250ms per hash)
    }
}
```

BCrypt:
- Includes a random **salt** automatically (no two hashes of the same password are identical)
- Has a configurable **cost factor** (higher = slower = more secure)
- Is designed to be slow on GPUs (memory-hard)

```java
PasswordEncoder encoder = new BCryptPasswordEncoder(12);

String hash1 = encoder.encode("password123");
// "$2a$12$LJ3m4sMKfRzl5Gk0YTh.4OQKp7HxMfLqEjNzBKvGhU5OhJXK3Xyq"

String hash2 = encoder.encode("password123");
// "$2a$12$9Xk2VJfRnMhRqGkZ5tL8XeWzYpN3hKjF7mQvB4cR6dS1eT2uW0xYz"
// Different! Because the salt is different each time.

encoder.matches("password123", hash1);  // true
encoder.matches("wrong", hash1);        // false
```

---

## UserDetailsService: Loading Users

Spring Security needs to know how to find users. You implement `UserDetailsService`:

```java
// src/main/java/com/vaultpay/security/VaultPayUserDetailsService.java
package com.vaultpay.security;

import com.vaultpay.entities.AppUser;
import com.vaultpay.repositories.UserRepository;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class VaultPayUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    public VaultPayUserDetailsService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        AppUser appUser = userRepository.findByEmail(email)
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + email));

        List<SimpleGrantedAuthority> authorities = appUser.getRoles().stream()
            .map(role -> new SimpleGrantedAuthority("ROLE_" + role.getName()))
            .toList();

        return User.builder()
            .username(appUser.getEmail())
            .password(appUser.getPasswordHash())  // BCrypt hash from DB
            .authorities(authorities)
            .accountLocked(!appUser.isActive())
            .build();
    }
}
```

### The User Entity

```java
// src/main/java/com/vaultpay/entities/AppUser.java
package com.vaultpay.entities;

import jakarta.persistence.*;
import java.util.Set;

@Entity
@Table(name = "app_users")
public class AppUser {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String passwordHash;

    @Column(nullable = false)
    private boolean active = true;

    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id"))
    private Set<Role> roles;

    // Getters, setters...
}
```

---

## Registration: Hashing on the Way In

```java
// src/main/java/com/vaultpay/services/UserService.java
package com.vaultpay.services;

import com.vaultpay.entities.AppUser;
import com.vaultpay.repositories.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public AppUser register(String email, String rawPassword) {
        // Validate password strength
        if (rawPassword.length() < 8) {
            throw new IllegalArgumentException("Password must be at least 8 characters");
        }

        // Hash the password — never store raw
        String hash = passwordEncoder.encode(rawPassword);

        AppUser user = new AppUser();
        user.setEmail(email);
        user.setPasswordHash(hash);
        user.setActive(true);

        return userRepository.save(user);
    }
}
```

The raw password exists only in memory, briefly. It's hashed immediately and the hash is stored. Even if the database leaks, attackers get BCrypt hashes — which take years to crack.

---

## Migration: SHA-1 → BCrypt

You can't decrypt SHA-1 hashes to re-hash them. Strategy: **migrate on login**.

```java
// src/main/java/com/vaultpay/security/PasswordMigrationService.java
package com.vaultpay.security;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class PasswordMigrationService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public void migrateIfNeeded(AppUser user, String rawPassword) {
        // If the stored hash doesn't start with "$2a$" it's not BCrypt
        if (!user.getPasswordHash().startsWith("$2a$")) {
            // Re-hash with BCrypt
            String newHash = passwordEncoder.encode(rawPassword);
            user.setPasswordHash(newHash);
            userRepository.save(user);
        }
    }
}
```

Use a `DelegatingPasswordEncoder` to handle both formats during migration:

```java
@Bean
public PasswordEncoder passwordEncoder() {
    Map<String, PasswordEncoder> encoders = Map.of(
        "bcrypt", new BCryptPasswordEncoder(12),
        "sha1", new MessageDigestPasswordEncoder("SHA-1")  // Legacy support
    );
    DelegatingPasswordEncoder delegating = new DelegatingPasswordEncoder("bcrypt", encoders);
    delegating.setDefaultPasswordEncoderForMatches(new BCryptPasswordEncoder(12));
    return delegating;
}
```

Stored hashes look like `{bcrypt}$2a$12$...` or `{sha1}5baa61e4...`. The prefix tells Spring which encoder to use for verification. New passwords always use BCrypt.

---

## Account Lockout: Brute-Force Protection

```java
// src/main/java/com/vaultpay/security/LoginAttemptService.java
package com.vaultpay.security;

import org.springframework.stereotype.Service;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

@Service
public class LoginAttemptService {

    private static final int MAX_ATTEMPTS = 5;
    private final ConcurrentHashMap<String, AtomicInteger> attempts = new ConcurrentHashMap<>();

    public void loginFailed(String email) {
        attempts.computeIfAbsent(email, k -> new AtomicInteger(0)).incrementAndGet();
    }

    public void loginSucceeded(String email) {
        attempts.remove(email);
    }

    public boolean isBlocked(String email) {
        AtomicInteger count = attempts.get(email);
        return count != null && count.get() >= MAX_ATTEMPTS;
    }
}
```

Integrate with the `UserDetailsService`:

```java
@Override
public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
    if (loginAttemptService.isBlocked(email)) {
        throw new LockedException("Account temporarily locked due to too many failed attempts");
    }

    // ... load user as before
}
```

---

## Testing Password Security

```java
@SpringBootTest
class PasswordSecurityTest {

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private UserService userService;

    @Test
    void passwordsAreHashedWithBcrypt() {
        AppUser user = userService.register("test@vaultpay.com", "SecureP@ss123");

        // Stored hash is BCrypt format
        assertThat(user.getPasswordHash()).startsWith("$2a$12$");

        // Raw password is NOT stored
        assertThat(user.getPasswordHash()).isNotEqualTo("SecureP@ss123");

        // Verification works
        assertThat(passwordEncoder.matches("SecureP@ss123", user.getPasswordHash())).isTrue();
        assertThat(passwordEncoder.matches("wrong", user.getPasswordHash())).isFalse();
    }

    @Test
    void samePasswordProducesDifferentHashes() {
        String hash1 = passwordEncoder.encode("password");
        String hash2 = passwordEncoder.encode("password");

        // Different hashes (different salts)
        assertThat(hash1).isNotEqualTo(hash2);

        // Both verify correctly
        assertThat(passwordEncoder.matches("password", hash1)).isTrue();
        assertThat(passwordEncoder.matches("password", hash2)).isTrue();
    }

    @Test
    void accountLocksAfterFiveFailedAttempts() {
        // Simulate 5 failed logins
        for (int i = 0; i < 5; i++) {
            loginAttemptService.loginFailed("victim@test.com");
        }

        assertThat(loginAttemptService.isBlocked("victim@test.com")).isTrue();
    }
}
```

---

## Report to Jess

> **Pen test finding #3 fixed:**
> - All passwords now hashed with BCrypt (cost factor 12)
> - Legacy SHA-1 hashes migrated on next login via `DelegatingPasswordEncoder`
> - Account lockout after 5 failed attempts (brute-force protection)
> - Same password → different hash every time (salted)
> - Even with a full database dump, passwords take years to crack
>
> The SHA-1 hashes? Being migrated to BCrypt as users log in. New registrations are BCrypt from day one.

Jess: "Passwords are safe at rest. But what about in transit? The pen tester intercepted a session cookie on public WiFi and replayed it. We need stateless authentication."

---

## What You Learned

- **Never use fast hashes (SHA-1, MD5, SHA-256) for passwords** — they're checksums, not password storage
- **BCrypt** is intentionally slow, includes a salt, and is GPU-resistant
- **Cost factor** controls how slow BCrypt is — 12 is a good default (~250ms)
- **`PasswordEncoder`** is Spring Security's abstraction — always use it, never hash manually
- **`DelegatingPasswordEncoder`** handles migration between hash formats
- **`UserDetailsService`** is how Spring Security loads users — implement it for your database
- **Account lockout** prevents brute-force attacks — lock after N failed attempts
- Same password → different BCrypt hash (because of random salt) — this is correct
- **Never log or return raw passwords** — hash immediately, forget immediately

---

[Next: Chapter 3 — "Session Stolen on Public WiFi" →](chapter-03-jwt.md)
