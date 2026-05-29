# Production

[prev: ActiveMQ Artemis Specifics](/blog/activemq/chapter-06-artemis)

## Clustering

### Artemis: Live/Backup Pairs

Artemis uses a primary (live) and backup (slave) architecture for high availability:

**Shared Store** — Both nodes access the same storage (shared filesystem or JDBC):

```xml
<!-- Live node -->
<ha-policy>
  <shared-store>
    <primary>
      <failover-on-shutdown>true</failover-on-shutdown>
    </primary>
  </shared-store>
</ha-policy>

<!-- Backup node -->
<ha-policy>
  <shared-store>
    <backup>
      <failback>true</failback>
      <allow-failback>true</allow-failback>
    </backup>
  </shared-store>
</ha-policy>
```

**Replication** — Backup replicates journal from live over the network (no shared storage needed):

```xml
<!-- Live node -->
<ha-policy>
  <replication>
    <primary>
      <group-name>pair-1</group-name>
      <vote-on-replication-failure>true</vote-on-replication-failure>
    </primary>
  </replication>
</ha-policy>

<!-- Backup node -->
<ha-policy>
  <replication>
    <backup>
      <group-name>pair-1</group-name>
      <allow-failback>true</allow-failback>
    </backup>
  </replication>
</ha-policy>
```

| Approach     | Pros                     | Cons                            |
| ------------ | ------------------------ | ------------------------------- |
| Shared Store | Simple, fast failover    | Requires shared filesystem      |
| Replication  | No shared storage needed | Network overhead, quorum needed |

### Classic: Network of Brokers

Classic uses a network of brokers for scaling and HA:

```xml
<!-- activemq.xml -->
<networkConnectors>
  <networkConnector name="bridge"
    uri="static:(tcp://broker2:61616)"
    duplex="true"
    decreaseNetworkConsumerPriority="true"
    networkTTL="2"
    dynamicOnly="true"/>
</networkConnectors>
```

Messages are forwarded between brokers based on consumer demand. This provides:

- Horizontal scaling
- Geographic distribution
- Load balancing across brokers

## High Availability

### Client-Side Failover

```properties
# Spring Boot
spring.activemq.broker-url=failover:(tcp://broker1:61616,tcp://broker2:61616)?randomize=true&maxReconnectAttempts=-1
```

### Artemis Cluster with Discovery

```xml
<broadcast-groups>
  <broadcast-group name="bg1">
    <group-address>231.7.7.7</group-address>
    <group-port>9876</group-port>
    <connector-ref>netty-connector</connector-ref>
  </broadcast-group>
</broadcast-groups>

<discovery-groups>
  <discovery-group name="dg1">
    <group-address>231.7.7.7</group-address>
    <group-port>9876</group-port>
    <refresh-timeout>10000</refresh-timeout>
  </discovery-group>
</discovery-groups>

<cluster-connections>
  <cluster-connection name="my-cluster">
    <connector-ref>netty-connector</connector-ref>
    <message-load-balancing>ON_DEMAND</message-load-balancing>
    <discovery-group-ref discovery-group-name="dg1"/>
  </cluster-connection>
</cluster-connections>
```

## Monitoring

### JMX

Both Classic and Artemis expose MBeans:

```java
// Programmatic JMX access
MBeanServerConnection mbsc = JMXConnectorFactory.connect(
    new JMXServiceURL("service:jmx:rmi:///jndi/rmi://localhost:1099/jmxrmi")
).getMBeanServerConnection();

ObjectName queueName = new ObjectName(
    "org.apache.activemq.artemis:broker=\"broker\",component=addresses,address=\"orders\",subcomponent=queues,routing-type=\"anycast\",queue=\"orders\"");
Long messageCount = (Long) mbsc.getAttribute(queueName, "MessageCount");
```

### Hawtio (Artemis)

Hawtio is included with Artemis at http://localhost:8161/console:

- Real-time queue depths
- Connection monitoring
- Message browsing
- Broker configuration

### Prometheus Metrics

**Artemis** — Enable the metrics plugin:

```xml
<!-- broker.xml -->
<metrics>
  <jvm-memory>true</jvm-memory>
  <jvm-gc>true</jvm-gc>
  <jvm-threads>true</jvm-threads>
  <plugin class-name="org.apache.activemq.artemis.core.server.metrics.plugins.ArtemisPrometheusMetricsPlugin"/>
</metrics>
```

Metrics endpoint: http://localhost:8161/metrics

Key metrics to monitor:

- `artemis_message_count` — Messages in queue
- `artemis_messages_added` — Total messages received
- `artemis_messages_acknowledged` — Total consumed
- `artemis_consumer_count` — Active consumers
- `artemis_address_memory_usage` — Memory used by address

**Classic** — Use JMX exporter:

```bash
docker run -d --name activemq-classic \
  -p 61616:61616 -p 8161:8161 -p 9090:9090 \
  -e ACTIVEMQ_OPTS="-javaagent:/opt/jmx_exporter.jar=9090:/opt/config.yaml" \
  apache/activemq-classic:latest
```

## Security

### JAAS Authentication

**Artemis** (login.config):

```
activemq {
  org.apache.activemq.artemis.spi.core.security.jaas.PropertiesLoginModule required
    org.apache.activemq.jaas.properties.user="artemis-users.properties"
    org.apache.activemq.jaas.properties.role="artemis-roles.properties";
};
```

artemis-users.properties:

```
admin=ENC(encrypted_password)
producer=producer_pass
consumer=consumer_pass
```

artemis-roles.properties:

```
admin=admin
producers=producer
consumers=consumer
```

### Role-Based Authorization (Artemis)

```xml
<security-settings>
  <security-setting match="#">
    <permission type="createDurableQueue" roles="admin"/>
    <permission type="deleteDurableQueue" roles="admin"/>
    <permission type="createNonDurableQueue" roles="admin,producers,consumers"/>
    <permission type="send" roles="admin,producers"/>
    <permission type="consume" roles="admin,consumers"/>
    <permission type="browse" roles="admin,consumers"/>
    <permission type="manage" roles="admin"/>
  </security-setting>
  <security-setting match="orders.#">
    <permission type="send" roles="order-producers"/>
    <permission type="consume" roles="order-consumers"/>
  </security-setting>
</security-settings>
```

### LDAP Integration

```
activemq {
  org.apache.activemq.artemis.spi.core.security.jaas.LDAPLoginModule required
    initialContextFactory="com.sun.jndi.ldap.LdapCtxFactory"
    connectionURL="ldap://ldap-server:389"
    connectionUsername="cn=admin,dc=example,dc=com"
    connectionPassword="admin_pass"
    userBase="ou=users,dc=example,dc=com"
    userSearchMatching="(uid={0})"
    roleBase="ou=groups,dc=example,dc=com"
    roleName="cn"
    roleSearchMatching="(member={0})";
};
```

### SSL/TLS

```xml
<acceptor name="ssl">
  tcp://0.0.0.0:61617?sslEnabled=true;keyStorePath=/etc/artemis/broker.ks;keyStorePassword=changeit;trustStorePath=/etc/artemis/client-truststore.jks;trustStorePassword=changeit;needClientAuth=true
</acceptor>
```

Client connection:

```properties
spring.artemis.broker-url=tcp://broker:61617?sslEnabled=true&trustStorePath=/path/to/truststore.jks&trustStorePassword=changeit
```

## Performance Tuning

### Prefetch Size

Controls how many messages are pushed to the consumer before acknowledgment:

```
# Classic — low prefetch for fair distribution
tcp://localhost:61616?jms.prefetchPolicy.queuePrefetch=1

# High prefetch for throughput
tcp://localhost:61616?jms.prefetchPolicy.queuePrefetch=1000
```

Artemis equivalent (consumer-window-size in bytes):

```xml
<address-setting match="orders">
  <default-consumer-window-size>1048576</default-consumer-window-size> <!-- 1MB -->
</address-setting>
```

### Async Send

Send messages without waiting for broker acknowledgment (risk: message loss on crash):

```java
// Classic
ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory();
factory.setUseAsyncSend(true);

// Artemis — enabled by default for non-persistent messages
// For persistent: set confirmationWindowSize
factory.setConfirmationWindowSize(1048576); // 1MB
```

### Flow Control

Prevent producers from overwhelming the broker:

**Artemis**:

```xml
<address-setting match="#">
  <max-size-bytes>100M</max-size-bytes>
  <address-full-policy>BLOCK</address-full-policy>
</address-setting>
```

**Classic** (producer flow control):

```xml
<systemUsage>
  <memoryUsage><memoryUsage percentOfJvmHeap="70"/></memoryUsage>
  <storeUsage><storeUsage limit="10 gb"/></storeUsage>
  <tempUsage><tempUsage limit="5 gb"/></tempUsage>
</systemUsage>
```

### JVM Tuning

```bash
# Artemis JVM settings (artemis.profile)
JAVA_ARGS="-Xms2g -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# Classic
ACTIVEMQ_OPTS="-Xms1g -Xmx1g -XX:+UseG1GC"
```

## Capacity Planning

### Sizing Guidelines

| Factor       | Consideration                      |
| ------------ | ---------------------------------- |
| Message rate | Messages/second in and out         |
| Message size | Average and max payload size       |
| Retention    | How long unprocessed messages stay |
| Consumers    | Number and processing speed        |
| Persistence  | Disk I/O requirements              |

### Disk Calculation

```
Daily storage = messages_per_second * avg_message_size * seconds_per_day
             = 1000 msg/s * 1KB * 86400
             = ~82 GB/day (if no consumption)
```

### Memory Sizing

- Artemis: `max-size-bytes` per address controls when paging kicks in
- Classic: `memoryUsage` controls total broker memory
- Rule of thumb: 2-4 GB heap for moderate workloads, more for high-throughput

### Monitoring Thresholds

| Metric       | Warning  | Critical  |
| ------------ | -------- | --------- |
| Queue depth  | > 10,000 | > 100,000 |
| Consumer lag | > 5 min  | > 30 min  |
| Memory usage | > 70%    | > 90%     |
| Disk usage   | > 70%    | > 85%     |

## Exercises

1. **HA setup**: Deploy an Artemis live/backup pair using Docker. Send messages to the live node, kill it, and verify the backup takes over and messages are preserved.

2. **Security**: Configure JAAS authentication with two roles (producer, consumer). Verify that a producer cannot consume and a consumer cannot send.

3. **Monitoring**: Enable Prometheus metrics on Artemis. Send a burst of messages and observe queue depth, message rate, and memory usage in a Grafana dashboard.

4. **Performance test**: Use the Artemis CLI producer/consumer to benchmark throughput. Test with different prefetch sizes, message sizes, and persistence modes. Document the results.

5. **Capacity planning**: Given a requirement of 5000 messages/second with 2KB average size and 1-hour retention, calculate the required disk space and memory. Configure the broker accordingly.
