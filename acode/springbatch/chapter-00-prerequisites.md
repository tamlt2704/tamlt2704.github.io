# Chapter 0: Before You Start

[Chapter 1: Your First Job →](chapter-01-first-job.md)

---

## The Story

This is a series about learning Spring Batch — but not the kind where you memorize "a Job has Steps" and move on.

You're a backend developer at **MegaBank Corp.**, a financial institution where legacy systems outnumber employees. Your manager, Director Compliance, lives in spreadsheets and regulatory deadlines. The CTO, Admiral Uptime, hasn't approved downtime since 2021. The DBA, Index Ivan, monitors every query like a hawk. And then there's Brenda from Reconciliation — she has 2 million transactions that need processing every night before the markets open.

Day one on the batch team, Director Compliance walks over:

"We need to reconcile every transaction from yesterday against the partner bank's file. Right now someone runs a SQL script manually at 5 AM. Last Tuesday they forgot. The auditors noticed. Can you automate it?"

You say yes. You have no idea what's coming.

Over the next 9 chapters, you'll build batch processing systems from scratch — the kind that reconcile millions of transactions, generate regulatory reports, migrate data between systems, and calculate end-of-day positions. It'll work perfectly in dev. Then you'll deploy it, and everything will break.

Brenda gets duplicate reconciliation entries. The nightly job runs for 4 hours and nobody can restart it from where it failed. A partner file arrives with 50,000 malformed rows. The month-end report takes so long it overlaps with the next day's processing window. Someone deploys a fix and all the job history disappears.

Each incident teaches you something about chunk processing, fault tolerance, or job orchestration that no tutorial could. You'll fix every bug, write a test that proves the fix, and ship it.

By the end, you'll have production-grade batch jobs with chunked reading/writing, skip/retry logic, restartability, partitioning, job orchestration, scheduling, monitoring, and testing — and you'll understand *why* every configuration choice is there.

## How to Read This

Every chapter is the same loop:

1. Something breaks — Brenda sends an angry email, Admiral Uptime calls a bridge
2. You write a test that reproduces the bug
3. You figure out why it happened
4. You fix it
5. The test goes green

No concept shows up before you need it. You won't hear about `SkipPolicy` until the partner file arrives with garbage rows. You won't touch partitioning until Brenda's 2-million-row file misses the processing window.

The bugs come first. The theory follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Batch Developer | Caffeinated, increasingly paranoid about data integrity |
| **Director Compliance** | Manager | "The auditors are coming in 3 weeks." |
| **Admiral Uptime** | CTO | Zero tolerance for failed nightly runs. Loves dashboards. |
| **Index Ivan** | DBA | "That full table scan is unacceptable." Speaks in execution plans. |
| **Brenda from Reconciliation** | Stakeholder | "2 million rows. Every night. Before 6 AM. No exceptions." |
| **Silent Sysadmin** | Ops | Communicates via PagerDuty alerts. Has never attended a standup. |
| **The Ghost Job** | That one execution | Started last Thursday. Status: STARTED. No one knows why. |

## The Roadmap

| Ch | The Incident | What You Learn |
|---|---|---|
| 1 | You build the first batch job | Project setup, Job/Step/Tasklet basics, job repository |
| 2 | Brenda's file has 2 million rows | Chunk-oriented processing, ItemReader/Processor/Writer |
| 3 | The partner file has garbage rows | Skip logic, SkipPolicy, error handling, listeners |
| 4 | The job fails at row 1.8M and restarts from zero | Restartability, ExecutionContext, checkpointing |
| 5 | The API call fails mid-batch | Retry logic, RetryTemplate, backoff, retry listeners |
| 6 | The 2M-row file misses the 6 AM deadline | Partitioning, multi-threaded steps, parallel flows |
| 7 | Month-end needs 5 jobs in sequence | Job orchestration, flows, conditional logic, deciders |
| 8 | "Who ran what and when?" | JobExplorer, monitoring, metrics, Spring Boot Actuator |
| 9 | Testing without the database | Testing patterns, JobLauncherTestUtils, mocking, integration tests |

## Prerequisites

Three things: Java 21, Gradle, and a terminal.

### Java 21 (Amazon Corretto)

```bash
curl -LO https://corretto.aws/downloads/latest/amazon-corretto-21-x64-linux-jdk.tar.gz
tar -xzf amazon-corretto-21-x64-linux-jdk.tar.gz
sudo mkdir -p /usr/lib/jvm
sudo mv amazon-corretto-21.* /usr/lib/jvm/corretto-21
export JAVA_HOME=/usr/lib/jvm/corretto-21
export PATH=$JAVA_HOME/bin:$PATH
```

Add the `export` lines to your `~/.bashrc` or `~/.zshrc` to make it permanent.

Verify:

```bash
java -version
```

```
openjdk version "21.0.x" ...
```

### Gradle

The project includes a wrapper (`gradlew`). But if you want it globally:

```bash
sdk install gradle
```

### PostgreSQL

Spring Batch needs a database for its job repository (metadata about job executions). The easiest way:

```bash
docker run -d --name megabank-pg -p 5432:5432 \
  -e POSTGRES_DB=batchjobs -e POSTGRES_PASSWORD=megabank \
  postgres:16
```

### IDE (Optional)

IntelliJ IDEA or VS Code. Spring Batch's XML-free Java config works great in any editor.

### Quick Check

```bash
java -version && echo "---" && docker ps
```

If Java prints a version and you see the Postgres container, you're good.

## What Is Spring Batch?

Before we start building, a 60-second mental model.

Spring Batch is a framework for processing large volumes of data in jobs that run to completion (not continuously like a web server). Think: nightly reconciliation, monthly reports, data migrations, file imports.

The core abstraction:

```
Job
 └── Step 1
 │    └── Read → Process → Write (in chunks)
 └── Step 2
 │    └── Read → Process → Write (in chunks)
 └── Step 3
      └── Tasklet (single operation)
```

A **Job** is a batch process. It has one or more **Steps**. Each Step either processes data in **chunks** (read N items, process them, write them as a batch) or runs a single **Tasklet** (like "delete temp files" or "send a notification").

Spring Batch handles:
- **Restartability** — if a job fails at row 1.8M, restart from 1.8M, not from zero
- **Skip/Retry** — bad rows don't kill the whole job
- **Chunk transactions** — if writing 100 rows fails, only those 100 roll back
- **Job metadata** — who ran what, when, with what parameters, what was the result
- **Scaling** — partition work across threads or even machines

You don't need to understand all of this now. Each concept arrives when you need it.

Let's build the first job.

---

[Chapter 1: Your First Job →](chapter-01-first-job.md)
