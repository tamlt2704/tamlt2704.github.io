# LockSmith: A Spring Security Survival Story

You've built REST APIs. You've deployed to production. You thought security was just "add a login page" and move on.

Then **Jess**, the security lead at **VaultPay** — a fintech startup that processes payments for 2,000 merchants — sends you a message:

> "We got pen-tested last week. The report is 47 pages. Someone accessed another merchant's transactions by changing the ID in the URL. Someone else bypassed the admin panel by guessing the endpoint. A third person stole a session token from a coffee shop WiFi. You start Monday."

You show up. The codebase has one security measure: `if (user != null)` before each controller method. The password column in the database is SHA-1 with no salt. The JWT secret is `"secret"`. The CORS policy is `*`.

Your mission: lock it down. Layer by layer, vulnerability by vulnerability.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Backend Developer | "I know Spring Boot. Security is just annotations, right?" |
| **Jess** | Security Lead | Thinks in attack vectors. Reads CVEs for fun. |
| **The Pen Tester** | External Auditor | Found 23 vulnerabilities in 4 hours. Left sarcastic comments. |
| **Merchant Mike** | API Consumer | "Why do I need an API key AND a token AND MFA?" |
| **The Hacker** | Threat Actor | Patient. Creative. Reads your error messages carefully. |
| **OWASP Top 10** | The Checklist | The ten ways your app will get owned if you're not careful. |

---

## The Tools

Everything runs on your laptop. No cloud needed.

| Tool | What It Does |
|---|---|
| **Java 21** | The language |
| **Spring Boot 3.3+** | Application framework |
| **Spring Security 6.3+** | Authentication, authorization, protection |
| **Nimbus JOSE+JWT** | JWT creation and validation |
| **Bcrypt** | Password hashing |
| **Testcontainers** | Integration tests with real databases |
| **OWASP ZAP** | Security scanning (optional) |

---

## How to Read This

Every chapter follows the same loop:

```
  💥 A vulnerability is exploited (pen test finding)
   │
   ▼
  🤔 You understand the attack vector
   │
   ▼
  🛡️  You implement the Spring Security defense
   │
   ▼
  ✓  You write a test that proves the attack no longer works
   │
   ▼
  💥 Next vulnerability
```

No concept shows up before you need it. You won't hear about CSRF until someone forges a request. You won't touch OAuth2 until Merchant Mike needs API access without sharing his password.

The attacks come first. The defenses follow.

---

## The Roadmap

| Ch | The Vulnerability | What You Learn |
|---|---|---|
| 1 | Anyone can access any endpoint | SecurityFilterChain, request matchers, permit/deny |
| 2 | Passwords stored in plain SHA-1 | UserDetailsService, PasswordEncoder, BCrypt |
| 3 | Session stolen on public WiFi | Stateless JWT authentication, token structure |
| 4 | Expired tokens still work | Token expiration, refresh tokens, revocation |
| 5 | User A sees User B's data | Method security, @PreAuthorize, SpEL expressions |
| 6 | Admin panel accessed by guessing URL | Role hierarchy, authority-based access control |
| 7 | Cross-site request forgery | CSRF protection, SameSite cookies, CORS |
| 8 | OAuth2 — "Login with Google" | OAuth2 login, OpenID Connect, social providers |
| 9 | API keys for machine-to-machine | Multiple auth mechanisms, filter chain ordering |
| 10 | The pen test passes | Security headers, rate limiting, audit logging |

---

## Prerequisites

Three things: Java 21, a terminal, and an HTTP client.

### Java 21 (Amazon Corretto)

```bash
# Windows (winget)
winget install Amazon.Corretto.21

# macOS
brew install --cask corretto21

# Linux
curl -LO https://corretto.aws/downloads/latest/amazon-corretto-21-x64-linux-jdk.tar.gz
tar -xzf amazon-corretto-21-x64-linux-jdk.tar.gz
export JAVA_HOME=$(pwd)/amazon-corretto-21.*
```

### Project Setup

```bash
mkdir locksmith && cd locksmith
```

`build.gradle`:

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.3.0'
    id 'io.spring.dependency-management' version '1.1.5'
}

group = 'com.vaultpay'
version = '1.0.0'

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-security'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'

    runtimeOnly 'com.h2database:h2'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.springframework.security:spring-security-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}

tasks.named('test') {
    useJUnitPlatform()
}
```

`settings.gradle`:

```groovy
rootProject.name = 'locksmith'
```

### The Starting Point

```java
// src/main/java/com/vaultpay/LockSmithApplication.java
package com.vaultpay;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class LockSmithApplication {
    public static void main(String[] args) {
        SpringApplication.run(LockSmithApplication.class, args);
    }
}
```

### Verify

```bash
./gradlew bootRun
```

Spring Security auto-configures with a random password printed to the console. Every endpoint requires authentication. That's the default — secure by default, open by choice.

---

## The Domain

VaultPay processes payments for merchants. The core API:

```
POST   /api/merchants          — register a new merchant
GET    /api/merchants/{id}     — get merchant details
GET    /api/transactions       — list transactions (filtered by merchant)
POST   /api/transactions       — create a transaction
GET    /api/admin/dashboard    — admin-only metrics
POST   /api/admin/users        — create users (admin-only)
```

Right now, none of these are protected properly. The pen test proved it.

---

## The Pen Test Findings (Preview)

| # | Severity | Finding |
|---|---|---|
| 1 | CRITICAL | Any authenticated user can access admin endpoints |
| 2 | CRITICAL | IDOR — changing merchant ID in URL exposes other merchants' data |
| 3 | HIGH | Passwords stored as unsalted SHA-1 |
| 4 | HIGH | JWT tokens never expire |
| 5 | HIGH | No CSRF protection on state-changing endpoints |
| 6 | MEDIUM | Missing security headers (CSP, HSTS, X-Frame-Options) |
| 7 | MEDIUM | Verbose error messages leak internal details |
| 8 | LOW | No rate limiting on login endpoint |
| 9 | LOW | CORS allows all origins |

We'll fix every one of these. By Chapter 10, the pen test passes clean.

---

[Next: Chapter 1 — "Anyone Can Access Any Endpoint" →](chapter-01-filter-chain.md)
