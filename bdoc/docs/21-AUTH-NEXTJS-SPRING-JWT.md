# Chapter 21: Authentication — Next.js Frontend + Spring Boot JWT Backend

## What you'll learn

- How JWT (JSON Web Tokens) authentication works end-to-end
- Building a Spring Boot backend with login/register/refresh endpoints
- Storing and managing tokens securely in Next.js
- Protected routes and middleware in Next.js
- Token refresh flow (silent refresh before expiry)
- Auth context and hooks for React components
- Security best practices (where to store tokens, CSRF, XSS)

---

## PART 1: How JWT Authentication Works

## 21.1 The flow

```
┌──────────┐                         ┌──────────────┐
│  Next.js │                         │  Spring Boot │
│ (browser)│                         │   (API)      │
└────┬─────┘                         └──────┬───────┘
     │                                      │
     │ 1. POST /api/auth/login              │
     │    { email, password }               │
     ├─────────────────────────────────────►│
     │                                      │ Validate credentials
     │                                      │ Generate JWT tokens
     │ 2. Response:                         │
     │    { accessToken, refreshToken }     │
     │◄─────────────────────────────────────┤
     │                                      │
     │ 3. Store tokens                      │
     │    (httpOnly cookie or memory)       │
     │                                      │
     │ 4. GET /api/algorithms (protected)   │
     │    Authorization: Bearer <token>     │
     ├─────────────────────────────────────►│
     │                                      │ Verify JWT signature
     │                                      │ Extract user from token
     │ 5. Response: { data }               │
     │◄─────────────────────────────────────┤
     │                                      │
     │ 6. Token expires (e.g. 15 min)      │
     │                                      │
     │ 7. POST /api/auth/refresh            │
     │    { refreshToken }                  │
     ├─────────────────────────────────────►│
     │                                      │ Verify refresh token
     │ 8. New { accessToken }              │ Issue new access token
     │◄─────────────────────────────────────┤
     │                                      │
```

## 21.2 JWT structure

A JWT has three parts separated by dots: `header.payload.signature`

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNjk5MDAwMDAwLCJleHAiOjE2OTkwMDA5MDB9.abc123signature
```

```json
// Header (algorithm + type)
{ "alg": "HS256", "typ": "JWT" }

// Payload (claims — user data + expiry)
{
  "sub": "user@example.com",
  "iat": 1699000000,
  "exp": 1699000900,     // expires in 15 minutes
  "roles": ["USER"]
}

// Signature (verifies the token wasn't tampered with)
HMACSHA256(base64(header) + "." + base64(payload), SECRET_KEY)
```

> **Key insight:** The payload is NOT encrypted — anyone can decode it (it's just base64). The signature proves the server issued it. NEVER put sensitive data (passwords, secrets) in the payload.

## 21.3 Two-token strategy

| Token | Lifetime | Purpose | Storage |
|-------|----------|---------|---------|
| Access Token | 15 minutes | Authenticate API requests | Memory (JS variable) or httpOnly cookie |
| Refresh Token | 7 days | Get new access tokens | httpOnly cookie (server-side) |

**Why two tokens?**
- Short-lived access token limits damage if stolen (expires in 15 min)
- Long-lived refresh token avoids forcing login every 15 min
- Refresh token is stored more securely (httpOnly cookie — JS can't read it)

---

## PART 2: Spring Boot Backend

## 21.4 Dependencies (pom.xml)

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt-api</artifactId>
        <version>0.12.6</version>
    </dependency>
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt-impl</artifactId>
        <version>0.12.6</version>
        <scope>runtime</scope>
    </dependency>
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt-jackson</artifactId>
        <version>0.12.6</version>
        <scope>runtime</scope>
    </dependency>
    <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
        <scope>runtime</scope>
    </dependency>
</dependencies>
```

## 21.5 User entity

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String password;  // BCrypt hashed

    @Column(nullable = false)
    private String name;

    @Enumerated(EnumType.STRING)
    private Role role = Role.USER;

    // getters, setters, constructors
}

public enum Role {
    USER, ADMIN
}
```

## 21.6 JWT utility service

```java
@Service
public class JwtService {
    @Value("${jwt.secret}")
    private String secretKey;

    @Value("${jwt.access-token-expiration}")
    private long accessTokenExpiration;  // 900000 = 15 minutes

    @Value("${jwt.refresh-token-expiration}")
    private long refreshTokenExpiration; // 604800000 = 7 days

    private SecretKey getSigningKey() {
        byte[] keyBytes = Decoders.BASE64.decode(secretKey);
        return Keys.hmacShaKeyFor(keyBytes);
    }

    public String generateAccessToken(User user) {
        return buildToken(user, accessTokenExpiration);
    }

    public String generateRefreshToken(User user) {
        return buildToken(user, refreshTokenExpiration);
    }

    private String buildToken(User user, long expiration) {
        return Jwts.builder()
                .subject(user.getEmail())
                .claim("name", user.getName())
                .claim("role", user.getRole().name())
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + expiration))
                .signWith(getSigningKey())
                .compact();
    }

    public String extractEmail(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public boolean isTokenValid(String token, UserDetails userDetails) {
        final String email = extractEmail(token);
        return email.equals(userDetails.getUsername()) && !isTokenExpired(token);
    }

    private boolean isTokenExpired(String token) {
        return extractClaim(token, Claims::getExpiration).before(new Date());
    }

    private <T> T extractClaim(String token, Function<Claims, T> resolver) {
        final Claims claims = Jwts.parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
        return resolver.apply(claims);
    }
}
```

## 21.7 Authentication controller

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthenticationManager authManager;
    private final JwtService jwtService;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    // Constructor injection...

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@RequestBody @Valid RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            return ResponseEntity.badRequest().build();
        }

        User user = new User();
        user.setEmail(request.getEmail());
        user.setName(request.getName());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        userRepository.save(user);

        String accessToken = jwtService.generateAccessToken(user);
        String refreshToken = jwtService.generateRefreshToken(user);

        return ResponseEntity.ok(new AuthResponse(accessToken, refreshToken, user.getName(), user.getEmail()));
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody @Valid LoginRequest request) {
        authManager.authenticate(
            new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword())
        );

        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow();

        String accessToken = jwtService.generateAccessToken(user);
        String refreshToken = jwtService.generateRefreshToken(user);

        return ResponseEntity.ok(new AuthResponse(accessToken, refreshToken, user.getName(), user.getEmail()));
    }

    @PostMapping("/refresh")
    public ResponseEntity<AuthResponse> refresh(@RequestBody RefreshRequest request) {
        try {
            String email = jwtService.extractEmail(request.getRefreshToken());
            User user = userRepository.findByEmail(email).orElseThrow();

            // Verify refresh token is still valid
            UserDetails userDetails = new CustomUserDetails(user);
            if (!jwtService.isTokenValid(request.getRefreshToken(), userDetails)) {
                return ResponseEntity.status(401).build();
            }

            String newAccessToken = jwtService.generateAccessToken(user);
            return ResponseEntity.ok(new AuthResponse(newAccessToken, request.getRefreshToken(), user.getName(), user.getEmail()));
        } catch (Exception e) {
            return ResponseEntity.status(401).build();
        }
    }
}
```

## 21.8 JWT authentication filter

```java
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {
        final String authHeader = request.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        final String token = authHeader.substring(7);
        final String email = jwtService.extractEmail(token);

        if (email != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails userDetails = userDetailsService.loadUserByUsername(email);

            if (jwtService.isTokenValid(token, userDetails)) {
                UsernamePasswordAuthenticationToken authToken =
                        new UsernamePasswordAuthenticationToken(
                                userDetails, null, userDetails.getAuthorities()
                        );
                authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }

        filterChain.doFilter(request, response);
    }
}
```

## 21.9 Security configuration

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtAuthFilter jwtAuthFilter;
    private final UserDetailsService userDetailsService;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())  // Disabled for JWT (stateless)
            .cors(cors -> cors.configurationSource(corsConfig()))
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfig() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("http://localhost:3000")); // Next.js dev
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);
        return request -> config;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }
}
```

## 21.10 application.yml

```yaml
jwt:
  secret: ${JWT_SECRET:your-256-bit-secret-key-here-must-be-at-least-32-chars}
  access-token-expiration: 900000     # 15 minutes
  refresh-token-expiration: 604800000 # 7 days

spring:
  datasource:
    url: jdbc:h2:mem:authdb
    driver-class-name: org.h2.Driver
  jpa:
    hibernate:
      ddl-auto: create-drop
```



---

## PART 3: Next.js Frontend

## 21.11 API client with token management

Create `lib/api.ts`:

```ts
type Tokens = {
  accessToken: string;
  refreshToken: string;
};

let tokens: Tokens | null = null;
let refreshPromise: Promise<string> | null = null;

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export function setTokens(newTokens: Tokens) {
  tokens = newTokens;
}

export function clearTokens() {
  tokens = null;
}

export function getAccessToken(): string | null {
  return tokens?.accessToken || null;
}

/**
 * Refresh the access token using the refresh token.
 * Deduplicates concurrent refresh attempts.
 */
async function refreshAccessToken(): Promise<string> {
  if (!tokens?.refreshToken) {
    throw new Error("No refresh token");
  }

  // Deduplicate: if a refresh is already in flight, wait for it
  if (refreshPromise) return refreshPromise;

  refreshPromise = fetch(`${API_URL}/api/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refreshToken: tokens.refreshToken }),
  })
    .then(async (res) => {
      if (!res.ok) throw new Error("Refresh failed");
      const data = await res.json();
      tokens = { accessToken: data.accessToken, refreshToken: data.refreshToken };
      return data.accessToken;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

/**
 * Authenticated fetch wrapper.
 * Automatically attaches Bearer token and handles 401 → refresh → retry.
 */
export async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const url = `${API_URL}${path}`;

  // First attempt
  let res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(tokens?.accessToken && { Authorization: `Bearer ${tokens.accessToken}` }),
      ...options.headers,
    },
  });

  // If 401 and we have a refresh token, try refreshing
  if (res.status === 401 && tokens?.refreshToken) {
    try {
      const newAccessToken = await refreshAccessToken();

      // Retry the original request with new token
      res = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${newAccessToken}`,
          ...options.headers,
        },
      });
    } catch {
      // Refresh failed — user must log in again
      clearTokens();
      window.location.href = "/login";
      throw new Error("Session expired");
    }
  }

  return res;
}
```

**Key design decisions:**
- Tokens in memory (not localStorage) — XSS can't steal them
- Deduplicated refresh — multiple 401s don't trigger multiple refresh calls
- Automatic retry — the original request is retried transparently after refresh
- Hard redirect on refresh failure — forces re-login

## 21.12 Auth context + provider

Create `context/AuthContext.tsx`:

```tsx
"use client";

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { setTokens, clearTokens, apiFetch } from "@/lib/api";

type User = {
  email: string;
  name: string;
};

type AuthContextType = {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for saved session on mount
  useEffect(() => {
    const savedUser = sessionStorage.getItem("user");
    const savedTokens = sessionStorage.getItem("tokens");

    if (savedUser && savedTokens) {
      setUser(JSON.parse(savedUser));
      setTokens(JSON.parse(savedTokens));
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.message || "Login failed");
    }

    const data = await res.json();
    const tokens = { accessToken: data.accessToken, refreshToken: data.refreshToken };
    const userData = { email: data.email, name: data.name };

    setTokens(tokens);
    setUser(userData);

    // Persist for page refreshes (sessionStorage — cleared when tab closes)
    sessionStorage.setItem("tokens", JSON.stringify(tokens));
    sessionStorage.setItem("user", JSON.stringify(userData));
  }, []);

  const register = useCallback(async (name: string, email: string, password: string) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.message || "Registration failed");
    }

    const data = await res.json();
    const tokens = { accessToken: data.accessToken, refreshToken: data.refreshToken };
    const userData = { email: data.email, name: data.name };

    setTokens(tokens);
    setUser(userData);

    sessionStorage.setItem("tokens", JSON.stringify(tokens));
    sessionStorage.setItem("user", JSON.stringify(userData));
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
    sessionStorage.removeItem("tokens");
    sessionStorage.removeItem("user");
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
```

## 21.13 Add AuthProvider to root layout

```tsx
// app/layout.tsx
import { AuthProvider } from "@/context/AuthContext";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <Navbar />
          <main>{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
```

## 21.14 Login page

Create `app/login/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await login(email, password);
      router.push("/algorithms");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Welcome back</CardTitle>
          <CardDescription>Sign in to your account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Signing in..." : "Sign in"}
            </Button>

            <p className="text-sm text-center text-muted-foreground">
              Don't have an account?{" "}
              <Link href="/register" className="text-primary hover:underline">
                Sign up
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
```

## 21.15 Protected route wrapper

Create `components/ProtectedRoute.tsx`:

```tsx
"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  if (!user) return null;

  return <>{children}</>;
}
```

Use it in protected pages:

```tsx
// app/dashboard/page.tsx
import ProtectedRoute from "@/components/ProtectedRoute";

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div>Secret content only for logged-in users</div>
    </ProtectedRoute>
  );
}
```

## 21.16 Next.js Middleware — server-side route protection

For a more robust approach, use Next.js middleware to check auth BEFORE the page renders:

```ts
// middleware.ts (project root)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PROTECTED_ROUTES = ["/dashboard", "/settings", "/algorithms/saved"];
const AUTH_ROUTES = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if user has a session token (stored as cookie)
  const token = request.cookies.get("session-token")?.value;
  const isAuthenticated = !!token;

  // Redirect unauthenticated users away from protected routes
  if (PROTECTED_ROUTES.some((route) => pathname.startsWith(route))) {
    if (!isAuthenticated) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("redirect", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  // Redirect authenticated users away from login/register
  if (AUTH_ROUTES.some((route) => pathname.startsWith(route))) {
    if (isAuthenticated) {
      return NextResponse.redirect(new URL("/algorithms", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/settings/:path*", "/algorithms/saved/:path*", "/login", "/register"],
};
```

> **Middleware vs client-side protection:**
> - Middleware runs on the server BEFORE any HTML is sent — no flash of protected content
> - Client-side `ProtectedRoute` shows a loading spinner then redirects — slight flash possible
> - Use both: middleware for hard protection, `ProtectedRoute` for graceful UX

## 21.17 Updating the navbar with auth state

```tsx
"use client";

import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

function UserMenu() {
  const { user, logout } = useAuth();

  if (!user) {
    return (
      <div className="flex gap-2">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/login">Sign in</Link>
        </Button>
        <Button size="sm" asChild>
          <Link href="/register">Sign up</Link>
        </Button>
      </div>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="gap-2">
          <div className="h-6 w-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold">
            {user.name.charAt(0).toUpperCase()}
          </div>
          <span className="hidden sm:inline">{user.name}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <div className="px-2 py-1.5">
          <p className="text-sm font-medium">{user.name}</p>
          <p className="text-xs text-muted-foreground">{user.email}</p>
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/dashboard">Dashboard</Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href="/settings">Settings</Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={logout} className="text-red-600">
          Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```



---

## PART 4: Security Best Practices

## 21.18 Where to store tokens — the security tradeoff

| Storage | XSS safe? | CSRF safe? | Persists refresh? | Complexity |
|---------|-----------|------------|-------------------|------------|
| **Memory (JS variable)** | ✅ Can't be stolen by XSS | ✅ No cookie = no CSRF | ❌ Lost on refresh | Low |
| **sessionStorage** | ❌ XSS can read it | ✅ No cookie | ✅ Survives refresh | Low |
| **localStorage** | ❌ XSS can read it | ✅ No cookie | ✅ Survives close | Low |
| **httpOnly cookie** | ✅ JS can't read it | ❌ Needs CSRF protection | ✅ Persistent | Higher |

**Recommended approach (what we built):**
- Access token in **memory** (safest against XSS)
- Refresh token in **sessionStorage** (survives page refresh, cleared when tab closes)
- For higher security: use **httpOnly cookies** via a BFF (Backend-For-Frontend) pattern

## 21.19 The BFF pattern (highest security)

Instead of the browser talking directly to Spring Boot, add a thin Next.js API route as a proxy:

```
Browser → Next.js API Route (BFF) → Spring Boot
         (sets httpOnly cookie)     (issues JWT)
```

```ts
// app/api/auth/login/route.ts (Next.js API route)
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const body = await request.json();

  // Forward to Spring Boot
  const res = await fetch("http://localhost:8080/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    return NextResponse.json({ error: "Login failed" }, { status: 401 });
  }

  const data = await res.json();

  // Set tokens as httpOnly cookies (browser JS can't read these)
  const response = NextResponse.json({
    user: { name: data.name, email: data.email },
  });

  response.cookies.set("access-token", data.accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 900, // 15 minutes
    path: "/",
  });

  response.cookies.set("refresh-token", data.refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 7 * 24 * 60 * 60, // 7 days
    path: "/",
  });

  return response;
}
```

```ts
// app/api/proxy/[...path]/route.ts — proxy all API calls
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
  const accessToken = request.cookies.get("access-token")?.value;
  const path = params.path.join("/");

  const res = await fetch(`http://localhost:8080/api/${path}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
  });

  if (res.status === 401) {
    // Try refresh
    const refreshToken = request.cookies.get("refresh-token")?.value;
    if (refreshToken) {
      // ... refresh logic, set new cookie, retry
    }
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const data = await res.json();
  return NextResponse.json(data);
}
```

**BFF advantages:**
- Tokens NEVER touch browser JavaScript (immune to XSS)
- httpOnly + Secure + SameSite cookies
- CORS is simple (same origin)
- Can add rate limiting, logging at the BFF layer

**BFF disadvantage:**
- Extra hop (browser → Next.js → Spring Boot)
- More code to maintain
- Doesn't work with `output: "export"` (needs a server)

## 21.20 CORS configuration

Spring Boot must allow requests from your Next.js origin:

```java
// In SecurityConfig.java
@Bean
public CorsConfigurationSource corsConfig() {
    CorsConfiguration config = new CorsConfiguration();

    // Development
    config.setAllowedOrigins(List.of(
        "http://localhost:3000",     // Next.js dev
        "https://yourdomain.com"    // Production
    ));

    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(List.of("*"));
    config.setAllowCredentials(true);  // Required for cookies
    config.setMaxAge(3600L);           // Preflight cache

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", config);
    return source;
}
```

> **`setAllowCredentials(true)`** is required if you're sending cookies or Authorization headers. Without it, browsers strip credentials from cross-origin requests.

## 21.21 Security checklist

```
□ Passwords hashed with BCrypt (never stored plain)
□ JWT secret is strong (256+ bits) and stored in environment variable
□ Access tokens expire quickly (15 min)
□ Refresh tokens can be revoked (store in DB, check on refresh)
□ HTTPS in production (tokens in transit are encrypted)
□ CORS whitelist only YOUR origins (not *)
□ Rate limit auth endpoints (prevent brute force)
□ Validate input (email format, password length)
□ Don't expose stack traces in error responses
□ Log failed login attempts (detect attacks)
□ Set Secure + SameSite on cookies
□ Use httpOnly cookies (or memory) — never localStorage for tokens
```

## 21.22 Token refresh — silent background refresh

Instead of waiting for a 401, proactively refresh before the token expires:

```tsx
// In AuthProvider, set up a timer
useEffect(() => {
  if (!tokens?.accessToken) return;

  // Decode the token to get expiry (without verifying — just reading)
  const payload = JSON.parse(atob(tokens.accessToken.split(".")[1]));
  const expiresAt = payload.exp * 1000; // Convert to milliseconds
  const refreshAt = expiresAt - 60000;  // Refresh 1 minute before expiry
  const delay = refreshAt - Date.now();

  if (delay <= 0) {
    // Already expired or about to — refresh now
    refreshAccessToken();
    return;
  }

  const timer = setTimeout(() => {
    refreshAccessToken();
  }, delay);

  return () => clearTimeout(timer);
}, [tokens?.accessToken]);
```

This means the user NEVER sees a 401 error — the token is always fresh.

## 21.23 Full project structure

```
# Next.js Frontend
app/
├── layout.tsx                  ← AuthProvider wraps everything
├── page.tsx                    ← Public landing page
├── login/page.tsx              ← Login form
├── register/page.tsx           ← Registration form
├── dashboard/page.tsx          ← Protected page
├── algorithms/page.tsx         ← Protected visualiser
└── api/                        ← BFF routes (optional)
    └── auth/
        ├── login/route.ts
        ├── register/route.ts
        └── refresh/route.ts
components/
├── ProtectedRoute.tsx
├── Navbar.tsx                  ← Shows user menu or sign-in button
└── ui/                         ← shadcn components
context/
└── AuthContext.tsx              ← Auth state + login/logout/register
lib/
├── api.ts                      ← Fetch wrapper with auto-refresh
└── utils.ts
middleware.ts                   ← Route protection (server-side)

# Spring Boot Backend
src/main/java/com/example/auth/
├── config/
│   └── SecurityConfig.java
├── controller/
│   └── AuthController.java
├── entity/
│   └── User.java
├── repository/
│   └── UserRepository.java
├── security/
│   ├── JwtService.java
│   ├── JwtAuthFilter.java
│   └── CustomUserDetails.java
└── dto/
    ├── LoginRequest.java
    ├── RegisterRequest.java
    ├── RefreshRequest.java
    └── AuthResponse.java
```

## Summary

✅ You understand the full JWT auth flow (login → token → request → refresh)
✅ You built Spring Boot endpoints: register, login, refresh with JWT
✅ You configured Spring Security for stateless JWT authentication
✅ You built a Next.js auth context with login/logout/register
✅ You created an API client that auto-refreshes tokens on 401
✅ You know how to protect routes (middleware + client-side)
✅ You understand token storage security (memory vs cookie vs localStorage)
✅ You know the BFF pattern for maximum security
✅ You can add silent background refresh (proactive, no 401s)

## Key takeaways

**JWT is stateless.** The server doesn't store sessions — the token IS the session. This makes it horizontally scalable (any server can verify any token) but harder to revoke (you can't "log out" a token — it's valid until it expires).

**Two tokens solve the UX vs security tension.** Short access token (secure — limits breach window) + long refresh token (UX — no constant re-login).

**Store tokens where JS can't reach them.** Memory or httpOnly cookies. localStorage is convenient but any XSS vulnerability exposes every user's token.

**The BFF pattern is the gold standard** for sensitive apps. The browser never sees the tokens — they live entirely in server-side cookies managed by Next.js API routes.

---

→ [Back to Chapter 20: shadcn/ui Navbar & Search](./20-SHADCN-NAVBAR-SEARCH-LAYOUT.md)
