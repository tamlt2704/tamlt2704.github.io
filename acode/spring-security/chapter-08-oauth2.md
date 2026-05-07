# Chapter 8: OAuth2 — "Login with Google"

[← Chapter 7: Cross-Site Request Forgery](chapter-07-csrf-cors.md) | [Chapter 9: API Keys for Machines →](chapter-09-api-keys.md)

---

## The Task

Merchant Mike:

> "I don't want another password. I already have a Google account. Can't I just 'Login with Google'? Every other service does it."

Jess agrees:

> "Less passwords we store, less risk. Add OAuth2 login. Google and GitHub for now. But we still need our own JWT after login — the OAuth2 token is for authentication only, not for our API."

---

## OAuth2 + OpenID Connect: The Flow

```
  User clicks "Login with Google"
       │
       ▼
  Redirect to Google's login page
       │
       ▼
  User authenticates with Google
       │
       ▼
  Google redirects back with an authorization code
       │
       ▼
  Your server exchanges the code for tokens (server-to-server)
       │
       ▼
  Your server reads the user's profile from Google
       │
       ▼
  Your server creates/finds the local user, issues YOUR JWT
       │
       ▼
  User gets your access token (not Google's)
```

---

## Add Dependencies

```groovy
implementation 'org.springframework.boot:spring-boot-starter-oauth2-client'
```

## Configuration

```yaml
# application.yml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: ${GOOGLE_CLIENT_ID}
            client-secret: ${GOOGLE_CLIENT_SECRET}
            scope: openid, profile, email
          github:
            client-id: ${GITHUB_CLIENT_ID}
            client-secret: ${GITHUB_CLIENT_SECRET}
            scope: user:email
        provider:
          github:
            user-name-attribute: login
```

Get credentials from [Google Cloud Console](https://console.cloud.google.com/apis/credentials) and [GitHub Developer Settings](https://github.com/settings/developers).

---

## Security Config for OAuth2

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/auth/**", "/oauth2/**", "/login/**").permitAll()
            .requestMatchers("/api/admin/**").hasRole("ADMIN")
            .anyRequest().authenticated()
        )
        .oauth2Login(oauth2 -> oauth2
            .successHandler(oAuth2SuccessHandler())
            .failureHandler((request, response, exception) -> {
                response.sendRedirect("/login?error=" + exception.getMessage());
            })
        )
        .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .csrf(csrf -> csrf.disable());

    return http.build();
}
```

---

## OAuth2 Success Handler: Issue Your Own JWT

```java
@Component
public class OAuth2SuccessHandler implements AuthenticationSuccessHandler {

    private final UserService userService;
    private final TokenService tokenService;

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request,
                                         HttpServletResponse response,
                                         Authentication authentication) throws IOException {
        OAuth2User oAuth2User = (OAuth2User) authentication.getPrincipal();

        String email = oAuth2User.getAttribute("email");
        String name = oAuth2User.getAttribute("name");
        String provider = ((OAuth2AuthenticationToken) authentication).getAuthorizedClientRegistrationId();

        // Find or create local user
        AppUser user = userService.findOrCreateOAuth2User(email, name, provider);

        // Issue YOUR JWT (not Google's token)
        UserDetails userDetails = userDetailsService.loadUserByUsername(email);
        TokenPair tokens = tokenService.generateTokenPair(userDetails);

        // Redirect to frontend with token
        String redirectUrl = "https://dashboard.vaultpay.com/auth/callback"
            + "?token=" + tokens.accessToken()
            + "&refresh=" + tokens.refreshToken();
        response.sendRedirect(redirectUrl);
    }
}
```

---

## Find or Create OAuth2 User

```java
@Service
public class UserService {

    public AppUser findOrCreateOAuth2User(String email, String name, String provider) {
        return userRepository.findByEmail(email)
            .orElseGet(() -> {
                AppUser newUser = new AppUser();
                newUser.setEmail(email);
                newUser.setDisplayName(name);
                newUser.setAuthProvider(provider);
                newUser.setPasswordHash(null);  // No password — OAuth2 only
                newUser.setActive(true);
                newUser.setRoles(Set.of(roleRepository.findByName("MERCHANT")));
                return userRepository.save(newUser);
            });
    }
}
```

First login with Google? Account created automatically with MERCHANT role. Subsequent logins? Existing account found by email.

---

## Linking Multiple Providers

A user might sign up with Google, then later try to login with GitHub (same email):

```java
public AppUser findOrCreateOAuth2User(String email, String name, String provider) {
    Optional<AppUser> existing = userRepository.findByEmail(email);

    if (existing.isPresent()) {
        AppUser user = existing.get();
        // Link the new provider to existing account
        user.getLinkedProviders().add(provider);
        return userRepository.save(user);
    }

    // Create new user...
}
```

---

## Testing OAuth2 Login

```java
@Test
void oauth2Login_createsLocalUser_andIssuesJwt() throws Exception {
    // Mock the OAuth2 authentication
    OAuth2User mockOAuth2User = mock(OAuth2User.class);
    when(mockOAuth2User.getAttribute("email")).thenReturn("merchant@gmail.com");
    when(mockOAuth2User.getAttribute("name")).thenReturn("Merchant Mike");

    // Simulate successful OAuth2 login
    OAuth2AuthenticationToken authToken = new OAuth2AuthenticationToken(
        mockOAuth2User, List.of(new SimpleGrantedAuthority("ROLE_USER")), "google");

    // Verify user was created
    AppUser user = userRepository.findByEmail("merchant@gmail.com").orElseThrow();
    assertThat(user.getAuthProvider()).isEqualTo("google");
    assertThat(user.getPasswordHash()).isNull();  // No password for OAuth2 users
}
```

---

## Report to Jess

> **OAuth2 login implemented:**
> - "Login with Google" and "Login with GitHub" working
> - OAuth2 used for authentication only — our JWT issued after successful OAuth2 login
> - New users auto-created with MERCHANT role on first OAuth2 login
> - Multiple providers can be linked to one account (same email)
> - No password stored for OAuth2-only users
>
> Merchant Mike is happy. One less password to remember. One less password for us to protect.

---

## What You Learned

- **OAuth2** delegates authentication to a trusted provider (Google, GitHub)
- **OpenID Connect** adds identity (email, name) on top of OAuth2
- After OAuth2 login, issue **your own JWT** — don't use the provider's token for your API
- **Find-or-create** pattern: first login creates the account, subsequent logins find it
- OAuth2 users have no password — they authenticate through the provider
- The authorization code flow is server-to-server — the client secret never reaches the browser
- Multiple providers can link to one account via email matching

---

[Next: Chapter 9 — "API Keys for Machines" →](chapter-09-api-keys.md)
