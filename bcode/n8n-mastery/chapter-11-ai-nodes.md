# Chapter 11: AI Nodes — Adding Intelligence

[← Chapter 10: Sub-Workflows](chapter-10-sub-workflows.md) | [Chapter 12: File Processing →](chapter-12-files.md)

---

## The Problem

Aisha's support team gets 50-80 tickets per day through Intercom. Every morning, she spends 20 minutes reading each ticket and tagging it: `bug`, `feature-request`, or `question`. The tag determines which team handles it — bugs go to engineering, feature requests go to product, questions go to docs.

Aisha: "I can tell within 5 seconds of reading a ticket what category it is. It's not hard — it's just tedious. Can the automation do this?"

This isn't a problem you can solve with IF nodes or string matching. "My app crashes when I click export" is a bug. "It would be great if the export had PDF support" is a feature request. "How do I export to CSV?" is a question. The difference is semantic, not structural.

You need an LLM.

## OpenAI Node: Basic Setup

### Credentials

1. Go to Credentials → Add Credential → OpenAI
2. Enter your API key from [platform.openai.com](https://platform.openai.com)
3. Test → Save

### Simple Classification

Add an OpenAI node (or "AI Agent" node in newer n8n versions):

```json
{
  "parameters": {
    "model": "gpt-4o-mini",
    "messages": {
      "values": [
        {
          "role": "system",
          "content": "You are a support ticket classifier. Classify the ticket into exactly one category: bug, feature-request, or question. Respond with ONLY the category name, nothing else."
        },
        {
          "role": "user",
          "content": "={{ $json.ticket_body }}"
        }
      ]
    },
    "options": { "temperature": 0 }
  },
  "name": "Classify Ticket",
  "type": "n8n-nodes-base.openAi",
  "position": [450, 300]
}
```

**Temperature 0** = deterministic output. The same input always produces the same classification. Critical for automation — you don't want randomness in routing decisions.

## Structured Output: Beyond Free Text

The basic approach returns free text. Sometimes the LLM responds "Bug" instead of "bug", or "This is a feature request" instead of "feature-request". Parsing free text is fragile.

### JSON Mode

Force the LLM to return valid JSON:

```json
{
  "parameters": {
    "model": "gpt-4o-mini",
    "messages": {
      "values": [
        {
          "role": "system",
          "content": "Classify the support ticket. Return JSON with this exact schema:\n{\"category\": \"bug|feature-request|question\", \"confidence\": 0.0-1.0, \"summary\": \"one sentence summary\"}"
        },
        {
          "role": "user",
          "content": "={{ $json.ticket_body }}"
        }
      ]
    },
    "options": {
      "temperature": 0,
      "responseFormat": "json_object"
    }
  },
  "name": "Classify Ticket (Structured)",
  "type": "n8n-nodes-base.openAi",
  "position": [450, 300]
}
```

Output:
```json
{
  "category": "bug",
  "confidence": 0.92,
  "summary": "App crashes on export button click"
}
```

Now you can route on `$json.category` with a Switch node — no string parsing needed.

### Parsing the Response

Add a Code node after the OpenAI node to extract the JSON:

```javascript
const response = $input.item.json.message.content;
const parsed = JSON.parse(response);

return {
  json: {
    ...parsed,
    original_ticket: $('Webhook').item.json.ticket_body,
    ticket_id: $('Webhook').item.json.ticket_id
  }
};
```

## Prompt Engineering for Automation

LLM prompts in automation need to be more precise than conversational prompts. The LLM has no human to ask for clarification.

### Rules for Automation Prompts

1. **Be explicit about output format** — "Return ONLY the category name" or "Return valid JSON"
2. **Enumerate all valid values** — "bug, feature-request, or question" (not "classify it")
3. **Provide examples** — few-shot prompting improves accuracy dramatically
4. **Handle edge cases** — "If unclear, classify as question"
5. **Set temperature to 0** — deterministic output for consistent routing

### Few-Shot Prompt

```
You are a support ticket classifier for a SaaS product.

Classify each ticket into exactly one category. Return JSON: {"category": "...", "confidence": 0.0-1.0}

Valid categories:
- bug: Something is broken, crashing, or not working as expected
- feature-request: User wants new functionality or changes to existing behavior
- question: User needs help understanding how to use existing features

Examples:
Ticket: "The dashboard shows wrong numbers after the latest update"
→ {"category": "bug", "confidence": 0.95}

Ticket: "Can you add dark mode to the settings page?"
→ {"category": "feature-request", "confidence": 0.98}

Ticket: "How do I invite team members to my workspace?"
→ {"category": "question", "confidence": 0.97}

Ticket: "Export is slow and sometimes times out on large datasets"
→ {"category": "bug", "confidence": 0.85}

Now classify this ticket:
```

## The Complete Classification Workflow

```json
{
  "name": "Support Ticket Auto-Classification",
  "nodes": [
    {
      "parameters": { "httpMethod": "POST", "path": "support-ticket" },
      "name": "New Ticket Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "model": "gpt-4o-mini",
        "messages": { "values": [
          { "role": "system", "content": "Classify the support ticket. Return JSON: {\"category\": \"bug|feature-request|question\", \"confidence\": 0.0-1.0, \"summary\": \"one line\"}. If confidence < 0.7, set category to \"needs-review\"." },
          { "role": "user", "content": "={{ $json.body.ticket_body }}" }
        ]},
        "options": { "temperature": 0, "responseFormat": "json_object" }
      },
      "name": "Classify",
      "type": "n8n-nodes-base.openAi",
      "position": [450, 300]
    },
    {
      "parameters": {
        "mode": "runOnceForEachItem",
        "jsCode": "const classification = JSON.parse($input.item.json.message.content);\nreturn { json: { ...classification, ticket_id: $('New Ticket Webhook').item.json.body.ticket_id, ticket_body: $('New Ticket Webhook').item.json.body.ticket_body } };"
      },
      "name": "Parse Response",
      "type": "n8n-nodes-base.code",
      "position": [650, 300]
    },
    {
      "parameters": {
        "rules": { "rules": [
          { "conditions": { "conditions": [{ "leftValue": "={{ $json.category }}", "rightValue": "bug" }] }, "output": 0 },
          { "conditions": { "conditions": [{ "leftValue": "={{ $json.category }}", "rightValue": "feature-request" }] }, "output": 1 },
          { "conditions": { "conditions": [{ "leftValue": "={{ $json.category }}", "rightValue": "question" }] }, "output": 2 }
        ], "fallbackOutput": 3 }
      },
      "name": "Route by Category",
      "type": "n8n-nodes-base.switch",
      "position": [850, 300]
    }
  ],
  "connections": {
    "New Ticket Webhook": { "main": [[{ "node": "Classify", "type": "main", "index": 0 }]] },
    "Classify": { "main": [[{ "node": "Parse Response", "type": "main", "index": 0 }]] },
    "Parse Response": { "main": [[{ "node": "Route by Category", "type": "main", "index": 0 }]] }
  }
}
```

## Confidence Thresholds

Don't blindly trust the LLM. Use the confidence score:

```
[Route by Category]
    ├── bug (confidence >= 0.8)      → Auto-assign to engineering
    ├── feature-request (>= 0.8)     → Auto-assign to product
    ├── question (>= 0.8)            → Auto-reply with docs link
    └── fallback (low confidence)    → Send to Aisha for manual review
```

This keeps humans in the loop for ambiguous cases while automating the obvious ones.

## Cost Control

GPT-4o-mini is cheap (~$0.15 per million input tokens), but 80 tickets/day × 30 days = 2,400 calls/month. Monitor costs:

```javascript
// Code node — track token usage
const usage = $input.item.json.usage;

return {
  json: {
    ...$input.item.json,
    tokens_used: usage.total_tokens,
    estimated_cost: (usage.total_tokens / 1000000) * 0.15
  }
};
```

### Tips for Reducing Costs

- Use `gpt-4o-mini` for classification (cheaper, fast enough)
- Keep prompts concise — fewer input tokens = lower cost
- Cache results for identical tickets (rare but possible with automated retries)
- Truncate very long tickets to first 500 words — usually enough for classification

## Chains: Multi-Step AI Processing

For complex tasks, chain multiple LLM calls:

```
[Classify] → [IF: is bug?] → [Extract Steps to Reproduce] → [Create Linear Ticket with Details]
```

The second LLM call extracts structured data from the bug report:

```
Extract the following from this bug report. Return JSON:
{"steps_to_reproduce": ["step1", "step2"], "expected_behavior": "...", "actual_behavior": "...", "severity": "critical|high|medium|low"}
```

Now the Linear ticket is pre-filled with structured information — not just the raw ticket text.

## What You Learned

- **OpenAI node** sends prompts and receives completions
- **Temperature 0** for deterministic, consistent automation output
- **JSON mode** forces structured responses — no free-text parsing
- **Few-shot prompting** improves classification accuracy significantly
- **Confidence thresholds** keep humans in the loop for ambiguous cases
- **Cost control** — use mini models, truncate inputs, monitor token usage
- **Chains** — multiple LLM calls for complex extraction and classification

Aisha's 20-minute morning ritual is now automated. 85% of tickets are auto-classified with high confidence. The remaining 15% go to her for review — but that's 8 tickets instead of 60.

Next: invoices arrive as PDF email attachments. The finance team manually types the amounts into a spreadsheet. You need to process files.

---

[← Chapter 10: Sub-Workflows](chapter-10-sub-workflows.md) | [Chapter 12: File Processing →](chapter-12-files.md)
