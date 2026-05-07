# Chapter 6: Send Results to the Pharmacy's SFTP

[← Chapter 5: Poll the FTP Server](chapter-05-inbound-adapters.md) | [Chapter 7: Retry and Dead-Letter →](chapter-07-error-handling.md)

---

## The Task

Miriam:

> "Prescriptions need to go to PharmaCo's SFTP server. They expect one JSON file per prescription in `/inbound/prescriptions/`. If the upload fails, we need to know immediately — not discover it when a patient doesn't get their medication."

Inbound adapters *read* from external systems. **Outbound adapters** *write* to them.

---

## Outbound Adapters: Sending Messages Out

```java
// src/main/java/com/medibridge/flows/PharmacyOutboundFlow.java
package com.medibridge.flows;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.sftp.dsl.Sftp;
import org.springframework.integration.sftp.session.DefaultSftpSessionFactory;

@Configuration
public class PharmacyOutboundFlow {

    @Bean
    public DefaultSftpSessionFactory pharmacySftpFactory() {
        DefaultSftpSessionFactory factory = new DefaultSftpSessionFactory();
        factory.setHost("sftp.pharmaco.com");
        factory.setPort(22);
        factory.setUser("medibridge-push");
        factory.setPrivateKey(new ClassPathResource("keys/pharmaco_rsa"));
        factory.setAllowUnknownKeys(false);
        return factory;
    }

    @Bean
    public IntegrationFlow prescriptionOutboundFlow(DefaultSftpSessionFactory pharmacySftpFactory) {
        return IntegrationFlow.from("prescriptionOutboundChannel")
            .handle(Sftp.outboundAdapter(pharmacySftpFactory)
                .remoteDirectory("/inbound/prescriptions")
                .fileNameGenerator(msg -> {
                    String rxId = msg.getHeaders().get("prescriptionId", String.class);
                    return rxId + ".json";
                })
                .autoCreateDirectory(true)
                .temporaryFileSuffix(".tmp"))  // Write as .tmp, rename when complete
            .get();
    }
}
```

### The `.tmp` Trick

`temporaryFileSuffix(".tmp")` means the file is uploaded as `RX-001.json.tmp` and renamed to `RX-001.json` only after the upload completes. This prevents the pharmacy's system from reading a half-written file.

---

## Gateways: Request-Reply Pattern

Outbound adapters are fire-and-forget. But sometimes you need a response — "did the upload succeed?" or "what's the tracking number?"

A **gateway** provides request-reply semantics:

```java
// src/main/java/com/medibridge/gateways/PrescriptionGateway.java
package com.medibridge.gateways;

import org.springframework.integration.annotation.Gateway;
import org.springframework.integration.annotation.MessagingGateway;
import org.springframework.messaging.handler.annotation.Header;

@MessagingGateway
public interface PrescriptionGateway {

    @Gateway(requestChannel = "prescriptionOutboundChannel")
    void sendPrescription(String prescriptionJson,
                          @Header("prescriptionId") String rxId);
}
```

Usage from a service:

```java
@Service
public class PrescriptionService {

    private final PrescriptionGateway gateway;

    public PrescriptionService(PrescriptionGateway gateway) {
        this.gateway = gateway;
    }

    public void dispatchPrescription(Prescription rx) {
        String json = objectMapper.writeValueAsString(rx);
        gateway.sendPrescription(json, rx.getId());
        // If this returns without exception, the message was sent successfully
        // If the SFTP upload fails, an exception propagates here
    }
}
```

---

## Outbound Gateway (Request-Reply with External System)

When you need a response from the external system:

```java
// HTTP outbound gateway — send a request, get a response
@Bean
public IntegrationFlow insuranceClaimFlow() {
    return IntegrationFlow.from("claimChannel")
        .handle(Http.outboundGateway("https://api.insurance.com/claims")
            .httpMethod(HttpMethod.POST)
            .expectedResponseType(String.class)
            .mappedRequestHeaders("Authorization", "Content-Type"))
        .handle((payload, headers) -> {
            // payload is the HTTP response body
            System.out.println("Claim submitted: " + payload);
            return payload;
        })
        .get();
}
```

| Component | Direction | Response? |
|---|---|---|
| Outbound Adapter | Send only | No — fire and forget |
| Outbound Gateway | Send and receive | Yes — waits for response |

---

## Multiple Outbound Destinations

Some messages need to go to multiple systems:

```java
@Bean
public IntegrationFlow multiDestinationFlow() {
    return IntegrationFlow.from("processedPrescriptionChannel")
        // Send to pharmacy SFTP
        .publishSubscribeChannel(pubsub -> pubsub
            .subscribe(sf -> sf
                .handle(Sftp.outboundAdapter(pharmacySftpFactory)
                    .remoteDirectory("/inbound/prescriptions")))
            .subscribe(sf -> sf
                // Also send to audit log
                .handle(Jdbc.outboundAdapter(dataSource,
                    "INSERT INTO audit_log (message_id, type, payload, sent_at) " +
                    "VALUES (:headers[id], 'PRESCRIPTION', :payload, NOW())")))
            .subscribe(sf -> sf
                // Also notify the patient via webhook
                .handle(Http.outboundAdapter("https://notify.medibridge.com/patient")
                    .httpMethod(HttpMethod.POST)))
        )
        .get();
}
```

`publishSubscribeChannel` sends the same message to all subscribers. Each subscriber processes independently.

---

## Detecting Failures

The outbound adapter throws an exception if the SFTP upload fails. But in an async flow, who catches it?

```java
@Bean
public IntegrationFlow prescriptionWithErrorHandling(DefaultSftpSessionFactory pharmacySftpFactory) {
    return IntegrationFlow.from("prescriptionOutboundChannel")
        .handle(Sftp.outboundAdapter(pharmacySftpFactory)
                .remoteDirectory("/inbound/prescriptions")
                .fileNameGenerator(msg -> msg.getHeaders().get("prescriptionId") + ".json")
                .temporaryFileSuffix(".tmp"),
            // Configure error handling on this endpoint
            e -> e.advice(retryAdvice()))
        .get();
}

@Bean
public RequestHandlerRetryAdvice retryAdvice() {
    RequestHandlerRetryAdvice advice = new RequestHandlerRetryAdvice();
    RetryTemplate retryTemplate = RetryTemplate.builder()
        .maxAttempts(3)
        .fixedBackoff(5000)  // 5 seconds between retries
        .build();
    advice.setRetryTemplate(retryTemplate);
    advice.setRecoveryCallback(context -> {
        // After 3 failures, send to error channel
        MessagingException ex = (MessagingException) context.getLastThrowable();
        errorChannel.send(ex.getFailedMessage());
        return null;
    });
    return advice;
}
```

We'll dive deeper into error handling in Chapter 7. For now: retries + fallback to error channel.

---

## Testing Outbound Flows

```java
@SpringBootTest
@SpringIntegrationTest
class PharmacyOutboundFlowTest {

    @Autowired
    private PrescriptionGateway gateway;

    // Use embedded SFTP server for testing
    @Container
    static GenericContainer<?> sftpContainer = new GenericContainer<>("atmoz/sftp:latest")
        .withExposedPorts(22)
        .withCommand("medibridge:test:::inbound/prescriptions");

    @Test
    void shouldUploadPrescriptionToSftp() {
        String prescription = """
            {
              "id": "RX-001",
              "patient": "P-12345",
              "medication": "Amoxicillin 500mg",
              "quantity": 21
            }
            """;

        gateway.sendPrescription(prescription, "RX-001");

        // Verify file exists on SFTP
        // Connect to test container and check /inbound/prescriptions/RX-001.json
    }

    @Test
    void shouldThrowOnConnectionFailure() {
        sftpContainer.stop();

        assertThatThrownBy(() ->
            gateway.sendPrescription("{}", "RX-FAIL"))
            .isInstanceOf(MessagingException.class);
    }
}
```

---

## Report to Miriam

> **Outbound SFTP implemented:**
> - Prescriptions uploaded to PharmaCo's SFTP as individual JSON files
> - `.tmp` suffix prevents reading half-written files
> - Gateway interface provides clean API for application code
> - Retry advice: 3 attempts with 5-second backoff before failing
> - Publish-subscribe for multi-destination delivery (pharmacy + audit + notification)
>
> If the upload fails, we know within 15 seconds (3 retries × 5s). Not 3 days later.

Miriam: "Good. But 'retry 3 times then give up' isn't enough. What happens to the message after it gives up? Right now it vanishes. Compliance Carl needs every failed message accounted for."

---

## What You Learned

- **Outbound adapters** write messages to external systems (SFTP, HTTP, JDBC, JMS)
- **Outbound gateways** send AND receive — request-reply with external systems
- **`temporaryFileSuffix`** prevents consumers from reading incomplete files
- **Messaging gateways** hide integration infrastructure behind a simple Java interface
- **Publish-subscribe channels** send the same message to multiple subscribers
- **Retry advice** wraps an endpoint with retry logic — configurable attempts and backoff
- Adapters are fire-and-forget; gateways are request-reply
- Always test with embedded/containerized infrastructure (Testcontainers)
- Failed outbound messages need a destination — they can't just vanish

---

[Next: Chapter 7 — "Retry and Dead-Letter" →](chapter-07-error-handling.md)
