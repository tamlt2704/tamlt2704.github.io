# Chapter 5: Poll the FTP Server Every 5 Minutes

[← Chapter 4: Split a Batch File](chapter-04-splitters.md) | [Chapter 6: Send Results to the Pharmacy →](chapter-06-outbound-adapters.md)

---

## The Disaster

The lab system doesn't write to a local folder. It uploads batch files to an FTP server at `ftp.labcorp.internal`. The ESB polled it every 5 minutes.

You set up the FTP adapter. It works. Files flow in. Then Monday morning: the same batch file gets processed 47 times. 47 copies of every lab result. Dr. Patel's inbox explodes.

The problem: the FTP adapter polls, sees the file, processes it, polls again — and the file is still there. FTP doesn't have a "mark as read" concept. Without deduplication, every poll reprocesses every file.

---

## FTP Inbound Adapter

First, add the dependency:

```groovy
// build.gradle
implementation 'org.springframework.integration:spring-integration-ftp'
```

```java
// src/main/java/com/medibridge/flows/FtpInboundFlow.java
package com.medibridge.flows;

import org.apache.commons.net.ftp.FTPFile;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.dsl.Pollers;
import org.springframework.integration.ftp.dsl.Ftp;
import org.springframework.integration.ftp.session.DefaultFtpSessionFactory;

import java.io.File;

@Configuration
public class FtpInboundFlow {

    @Bean
    public DefaultFtpSessionFactory ftpSessionFactory() {
        DefaultFtpSessionFactory factory = new DefaultFtpSessionFactory();
        factory.setHost("ftp.labcorp.internal");
        factory.setPort(21);
        factory.setUsername("medibridge");
        factory.setPassword("${FTP_PASSWORD}");  // From environment/secrets
        return factory;
    }

    @Bean
    public IntegrationFlow ftpInboundFlow(DefaultFtpSessionFactory ftpSessionFactory) {
        return IntegrationFlow
            .from(Ftp.inboundAdapter(ftpSessionFactory)
                    .remoteDirectory("/outbound/labs")
                    .localDirectory(new File("local-ftp-staging/labs"))
                    .autoCreateLocalDirectory(true)
                    .patternFilter("*.hl7")
                    .deleteRemoteFiles(true),  // Remove from FTP after download
                e -> e.poller(Pollers.fixedDelay(300_000)))  // Every 5 minutes
            .transform(Files.toStringTransformer())
            .channel("rawLabChannel")
            .get();
    }
}
```

### The Flow

```
  FTP Server (/outbound/labs/*.hl7)
       │
       │  poll every 5 min
       ▼
  [FTP Inbound Adapter] — downloads to local staging
       │
       ▼
  [File → String transformer]
       │
       ▼
  rawLabChannel → (existing transform/route/split flows)
```

---

## The Duplicate Problem: Idempotent Receivers

`deleteRemoteFiles(true)` helps — but what if the download succeeds and the delete fails? Or the app crashes between download and processing? The file stays on FTP, gets downloaded again next poll.

Solution: **idempotent receiver** — track which files you've already seen.

```java
@Bean
public IntegrationFlow ftpIdempotentFlow(DefaultFtpSessionFactory ftpSessionFactory) {
    return IntegrationFlow
        .from(Ftp.inboundAdapter(ftpSessionFactory)
                .remoteDirectory("/outbound/labs")
                .localDirectory(new File("local-ftp-staging/labs"))
                .autoCreateLocalDirectory(true)
                .patternFilter("*.hl7")
                // Use a metadata store to track seen files
                .localFilter(new FileSystemPersistentAcceptOnceFileListFilter(
                    new PropertiesPersistingMetadataStore(), "ftp-lab-files")),
            e -> e.poller(Pollers.fixedDelay(300_000)))
        .transform(Files.toStringTransformer())
        .channel("rawLabChannel")
        .get();
}
```

The `AcceptOnceFileListFilter` remembers filenames it has already processed. Even if the file reappears (FTP delete failed, or someone re-uploads it), it won't be processed again.

### Persistent Metadata Store

The in-memory filter resets on restart. For production, use a persistent store:

```java
@Bean
public MetadataStore metadataStore(DataSource dataSource) {
    JdbcMetadataStore store = new JdbcMetadataStore(dataSource);
    store.setTablePrefix("INT_");
    return store;
}
```

This stores "seen file" records in a database table. Survives restarts.

---

## SFTP: The Secure Version

Most real systems use SFTP (SSH File Transfer Protocol), not plain FTP:

```groovy
// build.gradle
implementation 'org.springframework.integration:spring-integration-sftp'
```

```java
@Bean
public DefaultSftpSessionFactory sftpSessionFactory() {
    DefaultSftpSessionFactory factory = new DefaultSftpSessionFactory();
    factory.setHost("sftp.labcorp.internal");
    factory.setPort(22);
    factory.setUser("medibridge");
    factory.setPrivateKey(new ClassPathResource("keys/medibridge_rsa"));
    factory.setPrivateKeyPassphrase("${SFTP_KEY_PASSPHRASE}");
    factory.setAllowUnknownKeys(false);
    factory.setKnownHostsResource(new ClassPathResource("keys/known_hosts"));
    return factory;
}

@Bean
public IntegrationFlow sftpInboundFlow(DefaultSftpSessionFactory sftpFactory) {
    return IntegrationFlow
        .from(Sftp.inboundAdapter(sftpFactory)
                .remoteDirectory("/outbound/labs")
                .localDirectory(new File("local-sftp-staging/labs"))
                .autoCreateLocalDirectory(true)
                .patternFilter("*.hl7"),
            e -> e.poller(Pollers.fixedDelay(300_000)))
        .transform(Files.toStringTransformer())
        .channel("rawLabChannel")
        .get();
}
```

Same pattern, different transport. The downstream flow doesn't change at all — it just receives messages on `rawLabChannel` regardless of whether they came from FTP, SFTP, or a local folder.

---

## Pollers: Controlling the Rhythm

```java
// Fixed delay: wait 5 minutes AFTER the last poll completes
Pollers.fixedDelay(300_000)

// Fixed rate: poll every 5 minutes regardless of how long processing takes
Pollers.fixedRate(300_000)

// Cron: poll at specific times
Pollers.cron("0 */5 * * * *")  // Every 5 minutes

// With max messages per poll (backpressure)
Pollers.fixedDelay(300_000).maxMessagesPerPoll(10)
// Only process 10 files per poll — prevents overwhelming downstream

// With error handling
Pollers.fixedDelay(300_000)
    .errorChannel("pollerErrorChannel")
```

**`fixedDelay` vs `fixedRate`**: Use `fixedDelay` when you don't want polls to overlap. If processing takes 3 minutes and the delay is 5 minutes, the next poll starts 5 minutes after the previous one *finishes* (8 minutes total). `fixedRate` would start the next poll 5 minutes after the previous one *started* (potentially overlapping).

---

## Other Inbound Adapters

Spring Integration has adapters for many sources:

```java
// HTTP (webhook receiver)
IntegrationFlow.from(Http.inboundChannelAdapter("/api/webhooks/lab-results")
        .requestMapping(m -> m.methods(HttpMethod.POST))
        .requestPayloadType(String.class))
    .channel("rawLabChannel")
    .get();

// JMS (message queue)
IntegrationFlow.from(Jms.messageDrivenChannelAdapter(connectionFactory)
        .destination("lab.results.queue"))
    .channel("rawLabChannel")
    .get();

// JDBC (poll a database table)
IntegrationFlow.from(Jdbc.inboundAdapter(dataSource,
        "SELECT * FROM pending_results WHERE processed = false")
        .updateSql("UPDATE pending_results SET processed = true WHERE id = :id"),
    e -> e.poller(Pollers.fixedDelay(60_000)))
    .channel("rawLabChannel")
    .get();

// Mail (poll an inbox)
IntegrationFlow.from(Mail.imapInboundAdapter(
        "imaps://user:pass@mail.example.com/INBOX")
        .searchTermStrategy(new UnseenSearchTermStrategy()),
    e -> e.poller(Pollers.fixedDelay(60_000)))
    .channel("rawLabChannel")
    .get();
```

The pattern is always the same: adapter polls external system → creates `Message` → sends to channel. Downstream flows don't care where the message came from.

---

## Testing with Embedded FTP

```java
// src/test/java/com/medibridge/flows/FtpInboundFlowTest.java
@SpringBootTest
@SpringIntegrationTest
class FtpInboundFlowTest {

    // Use FakeFtpServer for testing
    private FakeFtpServer ftpServer;

    @BeforeEach
    void startFtp() {
        ftpServer = new FakeFtpServer();
        ftpServer.addUserAccount(new UserAccount("medibridge", "test", "/"));
        FileSystem fs = new UnixFakeFileSystem();
        fs.add(new FileEntry("/outbound/labs/batch001.hl7", "MSH|^~\\&|LAB..."));
        ftpServer.setFileSystem(fs);
        ftpServer.setServerControlPort(0);  // Random port
        ftpServer.start();
    }

    @AfterEach
    void stopFtp() {
        ftpServer.stop();
    }

    @Test
    void shouldDownloadAndProcessFtpFile() {
        // Trigger a poll manually in test
        // Verify message arrives on rawLabChannel
    }
}
```

Add test dependency:

```groovy
testImplementation 'org.mockftpserver:MockFtpServer:3.1.0'
```

---

## Report to Miriam

> **FTP polling implemented:**
> - SFTP inbound adapter polls `/outbound/labs/` every 5 minutes
> - Idempotent receiver prevents duplicate processing (persistent metadata store)
> - Files deleted from remote after successful download
> - `maxMessagesPerPoll(10)` prevents overwhelming downstream flows
> - Same `rawLabChannel` — downstream flows unchanged
>
> The 47-duplicate incident? Impossible now. Metadata store remembers every file.

Miriam: "Now the other direction. The pharmacy needs results pushed to their SFTP server. And if the push fails, we need to know about it — not discover it 3 days later."

---

## What You Learned

- **Inbound adapters** connect external systems to your message flows (FTP, SFTP, HTTP, JMS, JDBC, Mail)
- **Pollers** control when adapters check for new data (`fixedDelay`, `fixedRate`, `cron`)
- **Idempotent receivers** prevent duplicate processing — track "seen" files in a metadata store
- **Persistent metadata store** (JDBC) survives application restarts
- **`deleteRemoteFiles(true)`** removes files after download — but isn't sufficient alone (crashes between download and delete)
- **`maxMessagesPerPoll`** provides backpressure — don't overwhelm downstream
- The adapter pattern decouples transport from processing — swap FTP for SFTP or HTTP without changing downstream flows
- Always test with embedded/fake servers — don't depend on real infrastructure in tests

---

[Next: Chapter 6 — "Send Results to the Pharmacy" →](chapter-06-outbound-adapters.md)
