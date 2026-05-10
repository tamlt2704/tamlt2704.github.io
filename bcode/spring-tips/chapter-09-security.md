# Chapter 9: Security Patterns — Modern Spring Security Without the Pain

[← Chapter 8: Actuator](chapter-08-actuator.md) | [Chapter 10: Performance →](chapter-10-performance.md)

---

## The Problem

"Spring Security is powerful but confusing. The old `WebSecurityConfigurerAdapter` is gone. I need JWT auth, CORS that actually works, and method-level permissions."

## SecurityFilterChain — The New Way

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())  // Disable for stateless APIs
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/products/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 ->
                oauth2.jwt(jwt -> jwt.jwtAuthenticationConverter(jwtConverter())))
            .build();
    }

    private JwtAuthenticationConverter jwtConverter() {
        var converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(jwt -> {
            List<String> roles = jwt.getClaimAsStringList("roles");
            if (roles == null) return List.of();
            return roles.stream()
                .map(role -> new SimpleGrantedAuthority("ROLE_" + role))
                .collect(Collectors.toList());
        });
        return converter;
    }
}
```

## JWT Validation — Resource Server

```yaml
# application.yml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.myapp.com
          # OR use jwk-set-uri directly:
          # jwk-set-uri: https://auth.myapp.com/.well-known/jwks.json
```

That's all you need for JWT validation. Spring auto-fetches the public keys and validates tokens.

For self-issued JWTs (no external auth server):

```java
@Configuration
public class JwtConfig {

    @Value("${app.jwt.secret}")
    private String secret;

    @Bean
    public JwtDecoder jwtDecoder() {
        SecretKey key = new SecretKeySpec(secret.getBytes(), "HmacSHA256");
        return NimbusJwtDecoder.withSecretKey(key).build();
    }
}
```

## Method-Level Security

```java
@Configuration
@EnableMethodSecurity  // Enables @PreAuthorize, @PostAuthorize
public class MethodSecurityConfig { }
```

```java
@Service
public class OrderService {

    @PreAuthorize("hasRole('ADMIN')")
    public void deleteOrder(Long id) {
        orderRepository.deleteById(id);
    }

    // Access method arguments in SpEL
    @PreAuthorize("#userId == authentication.principal.claims['sub']")
    public List<Order> getUserOrders(String userId) {
        return orderRepository.findByUserId(userId);
    }

    // Check result after method executes
    @PostAuthorize("returnObject.userId == authentication.principal.claims['sub']")
    public Order getOrder(Long id) {
        return orderRepository.findById(id)
            .orElseThrow(() -> new NotFoundException("Order", id));
    }

    // Custom permission check
    @PreAuthorize("@orderSecurity.canAccess(#id, authentication)")
    public Order getOrderSecure(Long id) {
        return orderRepository.findById(id).orElseThrow();
    }
}

@Component("orderSecurity")
public class OrderSecurityChecker {
    public boolean canAccess(Long orderId, Authentication auth) {
        String userId = ((Jwt) auth.getPrincipal()).getSubject();
        return orderRepository.existsByIdAndUserId(orderId, userId);
    }
}
```

## CORS Configuration

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    return http
        .cors(cors -> cors.configurationSource(corsConfig()))
        // ... rest of config
        .build();
}

private CorsConfigurationSource corsConfig() {
    var config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://myapp.com", "http://localhost:3000"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
    config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
    config.setExposedHeaders(List.of("X-Request-Id"));
    config.setMaxAge(3600L);

    var source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", config);
    return source;
}
```

## Custom Authentication Filter

For API key auth or custom token schemes:

```java
public class ApiKeyAuthFilter extends OncePerRequestFilter {

    private final ApiKeyService apiKeyService;

    public ApiKeyAuthFilter(ApiKeyService apiKeyService) {
        this.apiKeyService = apiKeyService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                     FilterChain chain) throws ServletException, IOException {
        String apiKey = request.getHeader("X-API-Key");

        if (apiKey != null) {
            apiKeyService.validate(apiKey).ifPresent(principal -> {
                var auth = new UsernamePasswordAuthenticationToken(
                    principal, null, principal.getAuthorities());
                SecurityContextHolder.getContext().setAuthentication(auth);
            });
        }

        chain.doFilter(request, response);
    }
}

// Register in SecurityFilterChain
@Bean
public SecurityFilterChain filterChain(HttpSecurity http, ApiKeyService apiKeyService) throws Exception {
    return http
        .addFilterBefore(new ApiKeyAuthFilter(apiKeyService),
            UsernamePasswordAuthenticationFilter.class)
        .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
        .build();
}
```

## Getting the Current User

```java
@RestController
@RequestMapping("/api/me")
public class ProfileController {

    @GetMapping
    public UserProfile getProfile(@AuthenticationPrincipal Jwt jwt) {
        String userId = jwt.getSubject();
        String email = jwt.getClaimAsString("email");
        List<String> roles = jwt.getClaimAsStringList("roles");
        return new UserProfile(userId, email, roles);
    }
}
```

## What You Learned

- **SecurityFilterChain** — lambda DSL replaces `WebSecurityConfigurerAdapter`
- **JWT validation** — one property for external auth, `JwtDecoder` bean for self-issued
- **@PreAuthorize** — SpEL expressions for method-level access control
- **Custom security beans** — `@orderSecurity.canAccess()` in SpEL
- **CORS** — `CorsConfigurationSource` bean with per-path config
- **Custom filters** — `addFilterBefore()` for API keys or custom tokens
- **@AuthenticationPrincipal** — inject the current user directly

---

[← Chapter 8: Actuator](chapter-08-actuator.md) | [Chapter 10: Performance →](chapter-10-performance.md)
