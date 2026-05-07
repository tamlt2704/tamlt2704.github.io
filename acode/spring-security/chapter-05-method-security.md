# Chapter 5: User A Sees User B's Data

[← Chapter 4: Expired Tokens Still Work](chapter-04-token-lifecycle.md) | [Chapter 6: Admin Panel Accessed by Guessing URL →](chapter-06-roles.md)

---

## The Vulnerability

> **CRITICAL: Insecure Direct Object Reference (IDOR)**
> Merchant A (ID: 42) calls `GET /api/merchants/43/transactions`. Gets Merchant B's transactions. The endpoint checks "are you authenticated?" but not "are you authorized to see THIS merchant's data?"

This is OWASP #1: Broken Access Control. The URL-level rules from Chapter 1 say "merchants can access `/api/merchants/**`" — but they don't check *which* merchant.

---

## Method-Level Security: @PreAuthorize

Enable method security:

```java
@Configuration
@EnableMethodSecurity  // Enables @PreAuthorize, @PostAuthorize, @Secured
public class MethodSecurityConfig {
}
```

Now protect individual methods:

```java
// src/main/java/com/vaultpay/services/MerchantService.java
@Service
public class MerchantService {

    @PreAuthorize("#merchantId == authentication.principal.merchantId or hasRole('ADMIN')")
    public Merchant getMerchant(Long merchantId) {
        return merchantRepository.findById(merchantId)
            .orElseThrow(() -> new NotFoundException("Merchant not found"));
    }

    @PreAuthorize("#merchantId == authentication.principal.merchantId or hasRole('ADMIN')")
    public List<Transaction> getTransactions(Long merchantId) {
        return transactionRepository.findByMerchantId(merchantId);
    }

    @PreAuthorize("hasRole('ADMIN')")
    public List<Merchant> getAllMerchants() {
        return merchantRepository.findAll();
    }
}
```

The SpEL expression `#merchantId == authentication.principal.merchantId` means: "the merchant ID in the URL must match the logged-in user's merchant ID." Merchant 42 can only see merchant 42's data.

---

## Custom UserDetails with Merchant ID

```java
public class VaultPayUserDetails implements UserDetails {

    private final Long userId;
    private final Long merchantId;  // Which merchant this user belongs to
    private final String email;
    private final String password;
    private final Collection<? extends GrantedAuthority> authorities;

    // Constructor, getters...

    public Long getMerchantId() {
        return merchantId;
    }
}
```

Update the `UserDetailsService` to include `merchantId` in the principal.

---

## @PostAuthorize: Check After Execution

Sometimes you need to load the object first, then check ownership:

```java
@PostAuthorize("returnObject.merchantId == authentication.principal.merchantId or hasRole('ADMIN')")
public Transaction getTransaction(Long transactionId) {
    return transactionRepository.findById(transactionId)
        .orElseThrow(() -> new NotFoundException("Transaction not found"));
}
```

`@PostAuthorize` runs after the method returns. If the check fails, the result is discarded and a 403 is returned. Use when the authorization decision depends on the returned data.

---

## @PreFilter and @PostFilter: Collection Security

```java
@PostFilter("filterObject.merchantId == authentication.principal.merchantId or hasRole('ADMIN')")
public List<Transaction> searchTransactions(TransactionQuery query) {
    return transactionRepository.search(query);
}
```

`@PostFilter` removes items from the returned collection that the user shouldn't see. Useful but be careful — it loads ALL data then filters. For large datasets, filter in the query instead.

---

## Custom Permission Evaluator

For complex authorization logic, create a custom evaluator:

```java
@Component
public class VaultPayPermissionEvaluator implements PermissionEvaluator {

    @Override
    public boolean hasPermission(Authentication auth, Object target, Object permission) {
        if (target instanceof Merchant merchant) {
            VaultPayUserDetails user = (VaultPayUserDetails) auth.getPrincipal();
            return merchant.getId().equals(user.getMerchantId())
                || auth.getAuthorities().stream()
                    .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        }
        return false;
    }

    @Override
    public boolean hasPermission(Authentication auth, Serializable targetId,
                                  String targetType, Object permission) {
        // Used with @PreAuthorize("hasPermission(#id, 'Merchant', 'read')")
        if ("Merchant".equals(targetType)) {
            VaultPayUserDetails user = (VaultPayUserDetails) auth.getPrincipal();
            return targetId.equals(user.getMerchantId())
                || auth.getAuthorities().stream()
                    .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        }
        return false;
    }
}
```

Usage:

```java
@PreAuthorize("hasPermission(#merchantId, 'Merchant', 'read')")
public Merchant getMerchant(Long merchantId) {
    return merchantRepository.findById(merchantId).orElseThrow();
}
```

---

## Testing IDOR Protection

```java
@Test
void merchant42_cannotAccessMerchant43_data() throws Exception {
    // Merchant 42's token
    String token = generateTokenForMerchant(42L);

    // Try to access merchant 43's transactions
    mockMvc.perform(get("/api/merchants/43/transactions")
            .header("Authorization", "Bearer " + token))
        .andExpect(status().isForbidden());
}

@Test
void merchant42_canAccessOwnData() throws Exception {
    String token = generateTokenForMerchant(42L);

    mockMvc.perform(get("/api/merchants/42/transactions")
            .header("Authorization", "Bearer " + token))
        .andExpect(status().isOk());
}

@Test
void admin_canAccessAnyMerchantData() throws Exception {
    String token = generateTokenForAdmin();

    mockMvc.perform(get("/api/merchants/43/transactions")
            .header("Authorization", "Bearer " + token))
        .andExpect(status().isOk());
}
```

---

## Report to Jess

> **IDOR vulnerability fixed:**
> - `@PreAuthorize` checks ownership on every data-access method
> - Merchant 42 can only see merchant 42's data — enforced at the service layer
> - Admins bypass ownership checks (explicit in the SpEL expression)
> - Custom `PermissionEvaluator` for complex authorization logic
> - Tests prove: cross-merchant access → 403
>
> The pen tester's IDOR attack? Returns 403 now. Every time.

---

## What You Learned

- **URL-level security** (Chapter 1) checks "can this role access this path?" — not "can this user access this specific resource"
- **Method-level security** (`@PreAuthorize`) checks ownership and fine-grained permissions
- **SpEL expressions** access the authentication principal, method parameters, and return values
- **`@PostAuthorize`** checks after execution — useful when authorization depends on the returned data
- **`@PostFilter`** removes unauthorized items from collections (use sparingly on large datasets)
- **Custom `PermissionEvaluator`** encapsulates complex authorization logic
- **IDOR** is OWASP #1 — always verify the authenticated user owns the requested resource
- Defense in depth: URL rules + method security + query-level filtering

---

[Next: Chapter 6 — "Admin Panel Accessed by Guessing URL" →](chapter-06-roles.md)
