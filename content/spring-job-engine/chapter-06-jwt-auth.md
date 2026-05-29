# Chapter 6: JWT Authentication

[← Chapter 5: Priority & Pause](/blog/spring-job-engine/chapter-05-priority-pause) | [Chapter 7: Audit →](/blog/spring-job-engine/chapter-07-audit)

---

## The Story

Anyone can submit jobs. Anyone can cancel them. The security team is not happy. You need: login, tokens, and role-based access.

## Step 1: JWT Token Provider

```java
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
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtTokenProvider tokenProvider;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain chain) throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            String token = header.substring(7);
            try {
                Claims claims = tokenProvider.parseToken(token);
                var auth = new UsernamePasswordAuthenticationToken(
                    claims.getSubject(),
                    null,
                    List.of(new SimpleGrantedAuthority("ROLE_" + claims.get("role")))
                );
                SecurityContextHolder.getContext().setAuthentication(auth);
            } catch (JwtException e) {
                response.setStatus(401);
                return;
            }
        }
        chain.doFilter(request, response);
    }
}
```

## Step 3: Security Configuration

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

## Step 4: Login Endpoint

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

## Step 5: Getting Current User in Jobs

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

## Step 6: Role-Based Access

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
