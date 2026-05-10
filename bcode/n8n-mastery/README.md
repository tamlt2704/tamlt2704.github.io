# n8n Mastery — Automation That Actually Works

A narrative-driven course on workflow automation with n8n. You're an ops engineer at a growing startup where everyone is drowning in manual processes. Over 15 chapters, you'll automate everything — one broken workflow at a time.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, workflow thinking, the cast |
| 01 | [Your First Workflow](chapter-01-first-workflow.md) | Slack alerts are manual | Triggers, HTTP nodes, basic flow |
| 02 | [Transforming Data](chapter-02-data-transform.md) | API responses are messy | Expressions, Code node, JSON manipulation |
| 03 | [Branching Logic](chapter-03-branching.md) | Not all alerts need the same response | IF node, Switch, routing |
| 04 | [Loops and Batches](chapter-04-loops.md) | 500 records need processing | SplitInBatches, loop patterns, rate limiting |
| 05 | [Error Handling](chapter-05-errors.md) | Workflow fails silently at 3 AM | Error triggers, retries, dead letter queues |
| 06 | [Webhooks](chapter-06-webhooks.md) | External services need to trigger workflows | Webhook node, authentication, response |
| 07 | [Database Operations](chapter-07-databases.md) | Spreadsheets aren't scaling | Postgres node, queries, upserts |
| 08 | [API Integrations](chapter-08-apis.md) | Manual data sync between tools | HTTP Request, OAuth2, pagination |
| 09 | [Scheduling](chapter-09-scheduling.md) | Reports need to run daily | Cron triggers, time zones, idempotency |
| 10 | [Sub-Workflows](chapter-10-sub-workflows.md) | Workflows are getting huge | Execute Workflow node, modularity, reuse |
| 11 | [AI Nodes](chapter-11-ai-nodes.md) | Classification needs intelligence | LLM nodes, chains, structured output |
| 12 | [File Processing](chapter-12-files.md) | PDFs and CSVs arrive by email | Read/write files, parsing, S3 storage |
| 13 | [Multi-Step Approvals](chapter-13-approvals.md) | Some actions need human sign-off | Wait node, forms, approval flows |
| 14 | [Monitoring & Observability](chapter-14-monitoring.md) | "Is the automation still working?" | Execution logs, health checks, alerting |
| 15 | [Production Deployment](chapter-15-production.md) | Local n8n isn't reliable enough | Docker, queue mode, scaling, backups |

## Prerequisites

- Docker (for running n8n locally)
- Basic understanding of APIs and JSON

## Philosophy

Every workflow is introduced because someone is doing something manually that's eating their week. No automation without a human pain point first. The manual process comes first. The automated version follows.
