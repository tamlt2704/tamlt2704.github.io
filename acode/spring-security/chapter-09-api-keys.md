# Chapter 9: API Keys for Machine-to-Machine

[← Chapter 8: OAuth2 — Login with Google](chapter-08-oauth2.md) | [Chapter 10: The Pen Test Passes →](chapter-10-hardening.md)

---

## The Task

Merchant Mike's developer:

> "I'm building a POS integration. It runs on a server — no browser, no user to log in. I need an API key I can put in my config file. JWT login flows don't work for machines."

Jess:

> "We need multiple authentication mechanisms: JWT for users, API keys for machines. Both must work on the same endpoints. And API keys need scopes — a POS key shouldn't be able to delete the merchant account."

---

## Multiple Authentication Mechanisms

Spring Security supports multiple filter chains, ordered by priority:

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    // Chain 1: API key authentication (checked first for /api/** with X-API-Key header)
    @Bean
    @Order(1)
    public SecurityFilterChain apiKeyFilterChain(HttpSecurity http) throws Exception {
        http
            .securityMatcher(request ->
                request.getHeader("X-API-Key") != null)
            .authorizeHttpRequests(auth -> auth
                .anyRequest().authenticated()
            )
            .addFilterBefore(apiKeyFilter(), UsernamePasswordAuthenticationFilter.class)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(csrf -> csrf.disable());

        return http.build();
    }

    // Chain 2: JWT authentication (default for everything else)
    @Bean
    @Order(2)
    public SecurityFilterChain jwtFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(csrf -> csrf.disable());

        return http.build();
    }
}
```

---

## API Key Model

```java
@Entity
@Table(name = "api_keys")
public class ApiKey {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String keyHash;  // BCrypt hash of the key (never store raw!)

    @Column(nullable = false)
    private String prefix;  // First 8 chars for identification (e.g., "vp_live_")

    @Column(nullable = false)
    private Long merchantId;

    @Column(nullable = false)
    private String name;  // "POS Integration", "Webhook Server"

    @ElementCollection(fetch = FetchType.EAGER)
    private Set<String> scopes;  // ["transaction:read", "transaction:write"]

    @Column(nullable = false)
    private boolean active = true;

    private Instant lastUsedAt;
    private Instant expiresAt;

    // Getters, setters...
}
```

---

## API Key Generation

```java
@Service
public class ApiKeyService {

    private final ApiKeyRepository apiKeyRepository;
    private final PasswordEncoder passwordEncoder;

    public ApiKeyCreationResult createApiKey(Long merchantId, String name, Set<String> scopes) {
        // Generate a random key: vp_live_a1b2c3d4e5f6g7h8i9j0...
        String rawKey = "vp_live_" + generateSecureRandom(32);
        String prefix = rawKey.substring(0, 16);  // For lookup without exposing full key
        String hash = passwordEncoder.encode(rawKey);

        ApiKey apiKey = new ApiKey();
        apiKey.setKeyHash(hash);
        apiKey.setPrefix(prefix);
        apiKey.setMerchantId(merchantId);
        apiKey.setName(name);
        apiKey.setScopes(scopes);
        apiKey.setActive(true);
        apiKey.setExpiresAt(Instant.now().plus(Duration.ofDays(365)));

        apiKeyRepository.save(apiKey);

        // Return the raw key ONCE — it's never stored or retrievable again
        return new ApiKeyCreationResult(rawKey, prefix, scopes);
    }

    private String generateSecureRandom(int length) {
        byte[] bytes = new byte[length];
        new SecureRandom().nextBytes(bytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }
}
```

**Critical**: The raw API key is shown to the user exactly once. After that, only the hash exists. Like a password — if lost, generate a new one.

---

## API Key Authentication Filter

```java
@Component
public class ApiKeyAuthenticationFilter extends OncePerRequestFilter {

    private final ApiKeyRepository apiKeyRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain filterChain) throws ServletException, IOException {

        String apiKeyHeader = request.getHeader("X-API-Key");
        if (apiKeyHeader == null) {
            filterChain.doFilter(request, response);
            return;
        }

        // Find by prefix (first 16 chars) — avoids scanning all keys
        String prefix = apiKeyHeader.substring(0, Math.min(16, apiKeyHeader.length()));
        List<ApiKey> candidates = apiKeyRepository.findByPrefixAndActiveTrue(prefix);

        ApiKey matchedKey = candidates.stream()
            .filter(k -> passwordEncoder.matches(apiKeyHeader, k.getKeyHash()))
            .findFirst()
            .orElse(null);

        if (matchedKey == null || isExpired(matchedKey)) {
            response.setStatus(401);
            response.getWriter().write("{\"error\": \"Invalid API key\"}");
            return;
        }

        // Update last used timestamp (async to not slow down the request)
        matchedKey.setLastUsedAt(Instant.now());
        apiKeyRepository.save(matchedKey);

        // Create authentication with the key's scopes as authorities
        List<SimpleGrantedAuthority> authorities = matchedKey.getScopes().stream()
            .map(SimpleGrantedAuthority::new)
            .toList();

        ApiKeyAuthentication auth = new ApiKeyAuthentication(
            matchedKey.getMerchantId(), matchedKey.getName(), authorities);
        SecurityContextHolder.getContext().setAuthentication(auth);

        filterChain.doFilter(request, response);
    }
}
```

---

## Scoped Access

API keys have limited scopes. A POS key with `["transaction:read", "transaction:write"]` can create transactions but can't delete the merchant account:

```java
@PreAuthorize("hasAuthority('transaction:write')")
@PostMapping("/api/transactions")
public Transaction createTransaction(@RequestBody TransactionRequest request) {
    // Works with both JWT (user has authority) and API key (key has scope)
    return transactionService.create(request);
}

@PreAuthorize("hasAuthority('merchant:delete')")
@DeleteMapping("/api/merchants/{id}")
public void deleteMerchant(@PathVariable Long id) {
    // API key without 'merchant:delete' scope → 403
    merchantService.delete(id);
}
```

The same `@PreAuthorize` works for both JWT users and API keys — because both produce `Authentication` objects with authorities.

---

## API Key Management Endpoints

```java
@RestController
@RequestMapping("/api/keys")
public class ApiKeyController {

    @PostMapping
    @PreAuthorize("hasAuthority('apikey:create')")
    public ApiKeyCreationResult createKey(@RequestBody CreateKeyRequest request,
                                           @AuthenticationPrincipal VaultPayUserDetails user) {
        return apiKeyService.createApiKey(
            user.getMerchantId(), request.name(), request.scopes());
    }

    @GetMapping
    public List<ApiKeySummary> listKeys(@AuthenticationPrincipal VaultPayUserDetails user) {
        // Show prefix, name, scopes, last used — never the full key
        return apiKeyService.listKeysForMerchant(user.getMerchantId());
    }

    @DeleteMapping("/{keyId}")
    public void revokeKey(@PathVariable Long keyId,
                           @AuthenticationPrincipal VaultPayUserDetails user) {
        apiKeyService.revoke(keyId, user.getMerchantId());
    }
}
```

---

## Testing Multiple Auth Mechanisms

```java
@Test
void apiKey_authenticatesSuccessfully() throws Exception {
    ApiKeyCreationResult key = apiKeyService.createApiKey(
        42L, "Test Key", Set.of("transaction:read", "transaction:write"));

    mockMvc.perform(get("/api/transactions")
            .header("X-API-Key", key.rawKey()))
        .andExpect(status().isOk());
}

@Test
void apiKey_withoutScope_returns403() throws Exception {
    ApiKeyCreationResult key = apiKeyService.createApiKey(
        42L, "Read Only", Set.of("transaction:read"));  // No write scope

    mockMvc.perform(post("/api/transactions")
            .header("X-API-Key", key.rawKey())
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"amount\": 100}"))
        .andExpect(status().isForbidden());
}

@Test
void jwt_stillWorksAlongside_apiKeys() throws Exception {
    String token = generateTokenForMerchant(42L);

    mockMvc.perform(get("/api/transactions")
            .header("Authorization", "Bearer " + token))
        .andExpect(status().isOk());
}
```

---

## Report to Jess

> **API key authentication implemented:**
> - Machine-to-machine auth via `X-API-Key` header
> - Keys are BCrypt-hashed (like passwords) — database leak doesn't expose keys
> - Scoped access: each key has specific permissions (not full account access)
> - Multiple filter chains: API key (priority 1) and JWT (priority 2) coexist
> - Key management: create, list, revoke — raw key shown only once
> - Same `@PreAuthorize` annotations work for both auth mechanisms
>
> Merchant Mike's POS integration works. His key can create transactions but can't delete his account.

---

## What You Learned

- **Multiple `SecurityFilterChain` beans** with `@Order` handle different auth mechanisms
- **API keys** are for machines — no login flow, no expiring sessions, just a static credential
- **Hash API keys like passwords** — never store raw keys in the database
- **Prefix-based lookup** avoids scanning all keys on every request
- **Scopes** limit what an API key can do — principle of least privilege
- **Show the raw key once** — after creation, it's unrecoverable (like a password)
- The same `@PreAuthorize` annotations work regardless of auth mechanism — both produce `Authentication` with authorities
- Track `lastUsedAt` — detect unused keys for cleanup

---

[Next: Chapter 10 — "The Pen Test Passes" →](chapter-10-hardening.md)
