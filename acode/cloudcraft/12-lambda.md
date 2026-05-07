# Chapter 12: "Run Code Without a Server"

[← DynamoDB](11-dynamodb.md) | [Next: Expose It as an API →](13-api-gateway.md)

---

Nora draws on a napkin:

> "When a user uploads a profile picture, resize it to 3 sizes. I don't want a server running 24/7 waiting for uploads that happen twice a day."

Tomás nods:

> "Lambda. You write a function. AWS runs it when something happens. You pay per invocation. No server to manage."

---

## What Is Lambda?

> "Imagine a **vending machine**. It doesn't have a chef inside cooking 24/7. You press a button, the machine wakes up, makes your drink, and goes back to sleep. You only pay for the drink."

```
Traditional server:                Lambda:

┌──────────────┐                  (nothing running)
│  Server 24/7 │                         │
│  Waiting...  │                   Event happens
│  Waiting...  │                         │
│  Waiting...  │                         ▼
│  Oh! Request!│                  ┌──────────────┐
│  Process it  │                  │ Function runs│
│  Waiting...  │                  │ Process it   │
└──────────────┘                  └──────────────┘
                                         │
  Paying: always                  (nothing running)
                                  Paying: only when it ran
```

| Concept | What It Is |
|---|---|
| **Function** | Your code — a single handler method |
| **Trigger** | What invokes it (API call, S3 upload, SQS message, schedule) |
| **Cold start** | First invocation is slower (Lambda spins up the runtime) |
| **Execution role** | Permissions the function has (what AWS services it can touch) |

---

## Your First Lambda (Locally)

Create a simple function. A Python file (Lambda supports Java too, but Python is faster to demo):

```python
# handler.py
def resize(event, context):
    filename = event.get("filename", "unknown")
    return {
        "statusCode": 200,
        "body": f"Resized: {filename}"
    }
```

Two arguments. Every Lambda gets them:
- `event` — the input data (what triggered it)
- `context` — metadata (timeout, memory, request ID)

---

## Deploy to LocalStack

Zip it:

```bash
zip function.zip handler.py
```

Create the function:

```bash
awslocal lambda create-function \
  --function-name image-resizer \
  --runtime python3.11 \
  --handler handler.resize \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::000000000000:role/lambda-role
```

| Flag | What It Means |
|---|---|
| `--function-name` | Name of your Lambda |
| `--runtime` | Language + version |
| `--handler` | `file.function` — which function to call |
| `--zip-file` | Your code, zipped |
| `--role` | IAM role (LocalStack doesn't enforce it, but the flag is required) |

---

## Invoke It

```bash
awslocal lambda invoke \
  --function-name image-resizer \
  --payload '{"filename": "photo.jpg"}' \
  output.json

cat output.json
```

```json
{"statusCode": 200, "body": "Resized: photo.jpg"}
```

Your function ran. No server. No container you manage. Just code → result.

---

## Cold Starts

Invoke it again. Notice it's faster the second time?

First invocation: Lambda creates a container, loads your code, runs it. **Cold start**.

Second invocation (within minutes): Reuses the warm container. **Warm start**.

```
1st call:  Container created → Code loaded → Function runs  (slow)
2nd call:  Container reused  → Function runs                (fast)
...
15 min idle: Container destroyed
Next call: Cold start again
```

This matters in production. For LocalStack practice, it's just good to know.

---

## Lambda with Java

For your Spring Boot world, a Java Lambda looks like:

```java
public class ResizeHandler
    implements RequestHandler<Map<String, String>, String> {

    @Override
    public String handleRequest(Map<String, String> event, Context context) {
        String filename = event.getOrDefault("filename", "unknown");
        return "Resized: " + filename;
    }
}
```

Package as a JAR, deploy the same way. Java cold starts are slower (~3-5s vs ~200ms for Python), which is why many teams use Python/Node for Lambda and Java for long-running services.

---

## What You Learned

```
────────────────────┬──────────────────────────────────────
Concept             │ One-liner
────────────────────┼──────────────────────────────────────
Lambda              │ Run code on demand, no server to manage
Handler             │ The function that gets called
Event               │ The input data
Cold start          │ First invocation is slower
Warm start          │ Reused container, faster
Trigger             │ What causes the function to run
────────────────────┴──────────────────────────────────────
```

---

## The Foreshadow

Your Lambda works when you invoke it manually. But Nora doesn't want to invoke it manually.

> "When someone hits `POST /resize`, the Lambda should run. I need an API in front of it."

That's **API Gateway**.

---

[← DynamoDB](11-dynamodb.md) | [Next: Expose It as an API →](13-api-gateway.md)
