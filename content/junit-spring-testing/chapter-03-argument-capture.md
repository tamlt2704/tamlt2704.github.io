# Argument Capture

ArgumentCaptor lets you capture arguments passed to mock methods for detailed verification — useful when objects are constructed inside the method under test.

## Class Under Test

```java
package com.example.service;

public class UserRegistrationService {

    private final UserRepository userRepository;
    private final EmailService emailService;

    public UserRegistrationService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }

    public void register(String name, String email) {
        User user = new User(name, email);
        user.setRole("MEMBER");
        userRepository.save(user);
        emailService.sendWelcome(new EmailMessage(email, "Welcome " + name, "Your account is ready."));
    }

    public void registerBatch(java.util.List<String> emails) {
        for (String email : emails) {
            emailService.sendWelcome(new EmailMessage(email, "Welcome", "Batch registration."));
        }
    }
}
```

```java
package com.example.service;

public class EmailMessage {
    private final String to;
    private final String subject;
    private final String body;

    public EmailMessage(String to, String subject, String body) {
        this.to = to;
        this.subject = subject;
        this.body = body;
    }

    public String getTo() { return to; }
    public String getSubject() { return subject; }
    public String getBody() { return body; }
}
```

## Capturing a Single Argument

```java
package com.example.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class UserRegistrationServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private EmailService emailService;

    @InjectMocks
    private UserRegistrationService service;

    @Captor
    private ArgumentCaptor<User> userCaptor;

    @Captor
    private ArgumentCaptor<EmailMessage> emailCaptor;

    @Test
    void register_capturesUserWithCorrectRole() {
        service.register("Alice", "alice@test.com");

        verify(userRepository).save(userCaptor.capture());

        User captured = userCaptor.getValue();
        assertEquals("Alice", captured.getName());
        assertEquals("alice@test.com", captured.getEmail());
        assertEquals("MEMBER", captured.getRole());
    }

    @Test
    void register_capturesEmailMessage() {
        service.register("Bob", "bob@test.com");

        verify(emailService).sendWelcome(emailCaptor.capture());

        EmailMessage captured = emailCaptor.getValue();
        assertEquals("bob@test.com", captured.getTo());
        assertEquals("Welcome Bob", captured.getSubject());
        assertEquals("Your account is ready.", captured.getBody());
    }
}
```

## Capturing Multiple Invocations with getAllValues

```java
package com.example.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class UserRegistrationBatchTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private EmailService emailService;

    @InjectMocks
    private UserRegistrationService service;

    @Captor
    private ArgumentCaptor<EmailMessage> emailCaptor;

    @Test
    void registerBatch_capturesAllEmails() {
        service.registerBatch(List.of("a@test.com", "b@test.com", "c@test.com"));

        verify(emailService, times(3)).sendWelcome(emailCaptor.capture());

        List<EmailMessage> allMessages = emailCaptor.getAllValues();
        assertEquals(3, allMessages.size());
        assertEquals("a@test.com", allMessages.get(0).getTo());
        assertEquals("b@test.com", allMessages.get(1).getTo());
        assertEquals("c@test.com", allMessages.get(2).getTo());
    }
}
```

## Capturing in Void Methods

For void methods, no stubbing is needed — just `verify()` with the captor:

```java
@Test
void register_capturesUserInVoidMethod() {
    service.register("Charlie", "charlie@test.com");

    // userRepository.save() is void — capture works directly
    verify(userRepository).save(userCaptor.capture());

    assertEquals("Charlie", userCaptor.getValue().getName());
}
```

## Key Points

- `@Captor` annotation is cleaner than inline `ArgumentCaptor.forClass(...)`
- `capture()` is used inside `verify()`, not inside `when()`
- `getValue()` returns the last captured value
- `getAllValues()` returns all captured values across multiple invocations
- Works with void methods — just `verify()` and `capture()`

[prev: Mockito](/blog/junit-spring-testing/chapter-02-mockito) | [next: Lenient Stubbing](/blog/junit-spring-testing/chapter-04-lenient)
