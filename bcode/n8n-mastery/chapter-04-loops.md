# Chapter 4: Loops and Batches — Processing at Scale

[← Chapter 3: Branching Logic](chapter-03-branching.md) | [Chapter 5: Error Handling →](chapter-05-errors.md)

---

## The Problem

Jake wants all HubSpot contacts synced to Notion. "We have about 500 contacts. Just pull them all and create Notion pages."

Your first attempt: HTTP Request to HubSpot → loop through results → create Notion page for each.

It works for the first 40 contacts. Then HubSpot returns:

```json
{ "status": "error", "message": "Rate limit exceeded. Max 100 requests per 10 seconds." }
```

The workflow crashes. 40 contacts made it to Notion. 460 didn't. And you have no idea which 40 succeeded because n8n processed them all as one batch that failed partway through.

Jake: "So now I have duplicates in Notion AND missing contacts? This is worse than doing it manually."

He's right. Bulk operations need batching, rate limiting, and the ability to resume after failure.

## SplitInBatches: The Core Pattern

The **SplitInBatches** node takes an array of items and processes them in groups. Instead of sending 500 requests at once, you send 10 at a time with a pause between each batch.

### Basic Structure

```
[Get All Contacts] → [SplitInBatches] → [Process One Batch] → [Wait] → (loop back)
                                                                              ↓
                                                                        [Done - all batches processed]
```

The SplitInBatches node has two outputs:
- **Loop** (top) → items in the current batch, loops back after processing
- **Done** (bottom) → fires once when all batches are complete

### Configuration

1. Add SplitInBatches after your data source
2. Set **Batch Size**: `10` (process 10 items per loop)
3. Connect the Loop output to your processing nodes
4. Connect the last processing node back to SplitInBatches
5. Connect the Done output to your completion logic

## The HubSpot → Notion Sync

```json
{
  "name": "HubSpot to Notion Sync",
  "nodes": [
    {
      "parameters": { "resource": "contact", "returnAll": true },
      "name": "Get HubSpot Contacts",
      "type": "n8n-nodes-base.hubspot",
      "position": [250, 300]
    },
    {
      "parameters": { "batchSize": 10, "options": {} },
      "name": "SplitInBatches",
      "type": "n8n-nodes-base.splitInBatches",
      "position": [450, 300]
    },
    {
      "parameters": {
        "resource": "databasePage",
        "databaseId": "your-notion-db-id",
        "properties": {
          "Name": "={{ $json.firstname }} {{ $json.lastname }}",
          "Email": "={{ $json.email }}",
          "Company": "={{ $json.company }}"
        }
      },
      "name": "Create Notion Page",
      "type": "n8n-nodes-base.notion",
      "position": [650, 200]
    },
    {
      "parameters": { "amount": 1, "unit": "seconds" },
      "name": "Wait 1s",
      "type": "n8n-nodes-base.wait",
      "position": [850, 200]
    },
    {
      "parameters": { "channel": "#ops", "text": "✅ HubSpot → Notion sync complete. {{ $('Get HubSpot Contacts').all().length }} contacts synced." },
      "name": "Notify Complete",
      "type": "n8n-nodes-base.slack",
      "position": [650, 450]
    }
  ],
  "connections": {
    "Get HubSpot Contacts": { "main": [[{ "node": "SplitInBatches", "type": "main", "index": 0 }]] },
    "SplitInBatches": {
      "main": [
        [{ "node": "Create Notion Page", "type": "main", "index": 0 }],
        [{ "node": "Notify Complete", "type": "main", "index": 0 }]
      ]
    },
    "Create Notion Page": { "main": [[{ "node": "Wait 1s", "type": "main", "index": 0 }]] },
    "Wait 1s": { "main": [[{ "node": "SplitInBatches", "type": "main", "index": 0 }]] }
  }
}
```

## The Wait Node: Respecting Rate Limits

The Wait node pauses execution between batches. Without it, n8n fires batches as fast as possible — which defeats the purpose.

### Calculating Wait Time

HubSpot allows 100 requests per 10 seconds. With a batch size of 10:
- Each batch = 10 API calls
- 100 calls / 10 items per batch = 10 batches per 10 seconds
- Wait 1 second between batches = safe margin

```
Batch size: 10
Wait between batches: 1 second
Total time for 500 contacts: ~50 seconds
```

### Wait Node Configuration

- **Resume**: After time interval
- **Amount**: `1`
- **Unit**: Seconds

For stricter APIs (e.g., 10 requests per minute), increase the wait:

```
Batch size: 5
Wait: 30 seconds
Total time for 500 contacts: ~50 minutes
```

Slow but reliable beats fast and broken.

## Handling Pagination

Most APIs don't return all records at once. HubSpot returns 100 contacts per page with a cursor for the next page. You need to paginate before batching.

### Pattern: Loop Until No More Pages

```javascript
// Code node — pagination loop
let allContacts = [];
let hasMore = true;
let after = undefined;

// Note: In practice, use the HTTP Request node's built-in pagination
// This shows the concept
while (hasMore) {
  const response = await this.helpers.httpRequest({
    method: 'GET',
    url: 'https://api.hubapi.com/crm/v3/objects/contacts',
    qs: { limit: 100, after },
    headers: { Authorization: `Bearer ${$credentials.hubspotApi.accessToken}` }
  });
  
  allContacts.push(...response.results);
  after = response.paging?.next?.after;
  hasMore = !!after;
}

return allContacts.map(contact => ({ json: contact }));
```

Or use the HTTP Request node's built-in pagination (simpler):

1. Enable **Pagination**
2. Set **Pagination Type**: "Response Contains Next URL"
3. Set **Next URL**: `{{ $response.body.paging.next.link }}`
4. Set **Max Pages**: `10` (safety limit)

## Advanced Pattern: Tracking Progress

For long-running syncs, track what's been processed so you can resume after failures:

```javascript
// Code node — before processing each batch
const item = $input.item.json;
const batchIndex = $('SplitInBatches').context.currentRunIndex;
const totalBatches = Math.ceil($('Get HubSpot Contacts').all().length / 10);

return {
  json: {
    ...item,
    _batchIndex: batchIndex,
    _totalBatches: totalBatches,
    _progress: `${batchIndex + 1}/${totalBatches}`
  }
};
```

## Common Mistakes

### Forgetting to Loop Back

If you don't connect the last node in your batch processing back to SplitInBatches, only the first batch runs. The workflow completes after processing 10 items and ignores the other 490.

### Batch Size Too Large

Setting batch size to 100 when the API allows 100 requests per 10 seconds means your entire batch fires simultaneously and gets rate-limited. Use smaller batches with waits.

### Not Handling Partial Failures

If item 7 in a batch of 10 fails, the entire batch fails by default. Use the **Continue On Fail** setting on the processing node to skip failures and handle them separately:

1. Click the processing node → Settings
2. Enable "Continue On Fail"
3. Failed items get an `error` field you can filter on later

### Memory with Large Datasets

Loading 50,000 items into memory before batching can crash n8n. For very large datasets, paginate at the source and process page-by-page rather than loading everything first.

## Pattern: Deduplication Before Sync

Before creating Notion pages, check if the contact already exists:

```
[Get HubSpot Contacts] → [Get Existing Notion Pages] → [Code: Find New Only] → [SplitInBatches] → ...
```

```javascript
// Code node — filter to new contacts only
const hubspotContacts = $('Get HubSpot Contacts').all();
const notionPages = $('Get Existing Notion Pages').all();

const existingEmails = new Set(
  notionPages.map(p => p.json.properties.Email?.email)
);

const newContacts = hubspotContacts.filter(
  c => !existingEmails.has(c.json.email)
);

return newContacts;
```

## What You Learned

- **SplitInBatches** processes items in groups with a loop-back pattern
- **Two outputs**: Loop (current batch) and Done (all complete)
- **Wait node** adds delays between batches to respect rate limits
- **Calculate batch timing** from API rate limits: requests ÷ batch size = batches per window
- **Pagination** fetches all records before batching (or page-by-page for large sets)
- **Continue On Fail** prevents one bad item from killing the entire batch
- **Deduplication** before sync prevents duplicates on re-runs

The HubSpot sync now processes 500 contacts in 50 seconds without hitting rate limits. Jake has his Notion database. Diana is impressed.

Then Thursday at 3 AM, the sync runs (you scheduled it — Chapter 9 spoiler) and Notion's API is down. The workflow fails silently. Nobody knows until Jake checks Notion on Monday and finds three days of missing contacts.

You need error handling.

---

[← Chapter 3: Branching Logic](chapter-03-branching.md) | [Chapter 5: Error Handling →](chapter-05-errors.md)
