# Chapter 6: Admin Panel Accessed by Guessing URL

[← Chapter 5: User A Sees User B's Data](chapter-05-method-security.md) | [Chapter 7: Cross-Site Request Forgery →](chapter-07-csrf-cors.md)

---

## The Vulnerability

> **CRITICAL: Privilege Escalation**
> The pen tester discovered `/api/admin/users` by guessing common admin paths. A regular merchant user could call `POST /api/admin/users` and create new admin accounts. The endpoint existed but wasn't in the UI — "security through obscurity."

Jess:

> "We need a proper role hierarchy. Admins can do everything. Managers can do most things. Merchants can only access their own data. And the system needs fine-grained permissions — not just roles."

---

## Roles vs Authorities

```java
// ROLE = broad category (who you are)
// AUTHORITY = specific permission (what you can do)

// Roles:
"ROLE_ADMIN"       // Full system access
"ROLE_MANAGER"     // Manage merchants, view reports
"ROLE_MERCHANT"    // Access own data only
"ROLE_SUPPORT"     // Read-only access to any merchant

// Authorities (fine-grained):
"merchant:read"
"merchant:write"
"transaction:read"
"transaction:write"
"transaction:refund"
"user:create"
"user:delete"
"report:generate"
```

---

## Role Hierarchy

An admin should automatically have all permissions a manager has. A manager should have all merchant permissions. Define this explicitly:

```java
@Bean
public RoleHierarchy roleHierarchy() {
    return RoleHierarchyImpl.withRolePrefix("ROLE_")
        .role("ADMIN").implies("MANAGER")
        .role("MANAGER").implies("MERCHANT")
        .role("MANAGER").implies("SUPPORT")
        .build();
}
```

Now `hasRole("MERCHANT")` passes for admins and managers too — without listing every role.

---

## Authority-Based Access Control

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http.authorizeHttpRequests(auth -> auth
        .requestMatchers("/api/auth/**").permitAll()

        // Admin operations
        .requestMatchers(HttpMethod.POST, "/api/admin/users").hasAuthority("user:create")
        .requestMatchers(HttpMethod.DELETE, "/api/admin/users/**").hasAuthority("user:delete")
        .requestMatchers("/api/admin/**").hasRole("ADMIN")

        // Transaction operations
        .requestMatchers(HttpMethod.POST, "/api/transactions/*/refund").hasAuthority("transaction:refund")
        .requestMatchers(HttpMethod.POST, "/api/transactions").hasAuthority("transaction:write")
        .requestMatchers(HttpMethod.GET, "/api/transactions/**").hasAuthority("transaction:read")

        // Reports
        .requestMatchers("/api/reports/**").hasAuthority("report:generate")

        .anyRequest().authenticated()
    );
    return http.build();
}
```

### Assign Authorities to Roles

```java
// In UserDetailsService — map roles to their authorities
private Collection<GrantedAuthority> getAuthorities(Set<Role> roles) {
    Set<GrantedAuthority> authorities = new HashSet<>();

    for (Role role : roles) {
        authorities.add(new SimpleGrantedAuthority("ROLE_" + role.getName()));

        // Add role-specific permissions
        switch (role.getName()) {
            case "ADMIN" -> authorities.addAll(List.of(
                new SimpleGrantedAuthority("user:create"),
                new SimpleGrantedAuthority("user:delete"),
                new SimpleGrantedAuthority("transaction:refund"),
                new SimpleGrantedAuthority("report:generate")
            ));
            case "MANAGER" -> authorities.addAll(List.of(
                new SimpleGrantedAuthority("transaction:refund"),
                new SimpleGrantedAuthority("report:generate")
            ));
            case "MERCHANT" -> authorities.addAll(List.of(
                new SimpleGrantedAuthority("merchant:read"),
                new SimpleGrantedAuthority("merchant:write"),
                new SimpleGrantedAuthority("transaction:read"),
                new SimpleGrantedAuthority("transaction:write")
            ));
        }
    }
    return authorities;
}
```

---

## Include Authorities in JWT

```java
public String generateToken(UserDetails userDetails) {
    List<String> authorities = userDetails.getAuthorities().stream()
        .map(GrantedAuthority::getAuthority)
        .toList();

    return Jwts.builder()
        .subject(userDetails.getUsername())
        .claim("authorities", authorities)  // Include all authorities
        .issuedAt(new Date())
        .expiration(new Date(System.currentTimeMillis() + expirationMs))
        .signWith(signingKey)
        .compact();
}
```

The JWT now carries: `{"authorities": ["ROLE_MERCHANT", "merchant:read", "transaction:write", ...]}`. The filter reconstructs the authorities from the token — no DB lookup needed per request.

---

## Testing Role Hierarchy

```java
@Test
void admin_canCreateUsers() throws Exception {
    mockMvc.perform(post("/api/admin/users")
            .with(user("admin@vaultpay.com").authorities(
                new SimpleGrantedAuthority("ROLE_ADMIN"),
                new SimpleGrantedAuthority("user:create")))
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"email\": \"new@test.com\"}"))
        .andExpect(status().isCreated());
}

@Test
void merchant_cannotCreateUsers() throws Exception {
    mockMvc.perform(post("/api/admin/users")
            .with(user("merchant@vaultpay.com").authorities(
                new SimpleGrantedAuthority("ROLE_MERCHANT")))
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"email\": \"new@test.com\"}"))
        .andExpect(status().isForbidden());
}

@Test
void manager_canRefundTransactions() throws Exception {
    mockMvc.perform(post("/api/transactions/123/refund")
            .with(user("manager@vaultpay.com").authorities(
                new SimpleGrantedAuthority("ROLE_MANAGER"),
                new SimpleGrantedAuthority("transaction:refund"))))
        .andExpect(status().isOk());
}
```

---

## Report to Jess

> **Role hierarchy and authorities implemented:**
> - Three-tier hierarchy: ADMIN → MANAGER → MERCHANT
> - Fine-grained authorities: `transaction:refund`, `user:create`, `report:generate`
> - Admin endpoints require specific authorities, not just the ADMIN role
> - Authorities embedded in JWT — no DB lookup per request
> - "Security through obscurity" replaced with explicit access control
>
> Guessing `/api/admin/users`? Returns 403 for non-admins. Even if they know the URL.

---

## What You Learned

- **Roles** = broad categories (ADMIN, MERCHANT). **Authorities** = specific permissions (transaction:refund)
- **Role hierarchy** — ADMIN implies MANAGER implies MERCHANT (no redundant checks)
- **Authority-based rules** are more precise than role-based — "can refund" vs "is admin"
- Embed authorities in the JWT — avoids DB lookups on every request
- **Security through obscurity is not security** — hidden URLs are still accessible
- Combine URL-level rules (Chapter 1) + method-level rules (Chapter 5) + authority checks for defense in depth

---

[Next: Chapter 7 — "Cross-Site Request Forgery" →](chapter-07-csrf-cors.md)
