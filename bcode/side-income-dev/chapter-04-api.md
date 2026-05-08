# Chapter 4: API as a Product

[← Templates & Digital Products](./chapter-03-templates.md) | [Next: Technical Content →](./chapter-05-content.md)

---

## The Strategy

APIs are the ultimate "build once, earn forever" product for developers. You build a service, document it, and charge per request or per month. No UI to maintain, no design skills needed, no customer-facing frontend. Just clean endpoints that solve a problem.

**Why APIs are perfect for time-constrained devs:**
- No frontend to build or maintain
- Usage-based pricing means revenue scales without your time
- Technical moat — non-developers can't easily replicate
- Low support burden (good docs + status page = happy customers)
- Can run on serverless (pay only when used, scale automatically)

**API product categories that work:**
- **Data enrichment:** Company info lookup, email validation, IP geolocation
- **Media processing:** Image resize/optimize, PDF generation, screenshot capture
- **AI wrappers:** Summarization, classification, extraction (add domain-specific value on top of LLMs)
- **Developer utilities:** Webhook testing, cron monitoring, log parsing
- **Niche data:** Real estate data, job listings, product prices

## The Math

**Usage-based pricing models:**

| Tier | Requests/Month | Price | Target Customer |
|------|---------------|-------|-----------------|
| Free | 100 | $0 | Hobbyists, evaluation |
| Starter | 5,000 | $19/mo | Small projects |
| Pro | 50,000 | $49/mo | Growing apps |
| Business | 500,000 | $199/mo | Established companies |

**Revenue scenario:**
- 20 free users (funnel)
- 30 Starter users × $19 = $570
- 10 Pro users × $49 = $490
- 2 Business users × $199 = $398
- **Total: $1,458/mo** from ~62 paying customers

**Cost to run:** $20-50/mo on serverless (Vercel/AWS Lambda + managed DB)

## The Strategy: Building & Distributing

**Tech stack for API products:**
- **Runtime:** Node.js (Hono/Express) or Python (FastAPI)
- **Hosting:** Vercel Edge Functions, AWS Lambda, or Railway
- **Database:** Supabase or PlanetScale (if needed)
- **Auth:** API keys (simple) or OAuth (if integrating with other services)
- **Rate limiting:** Upstash Redis
- **Docs:** Mintlify, ReadMe, or simple Markdown
- **Billing:** Stripe Metered Billing or manual tier-based

**Distribution channels:**
- **RapidAPI Marketplace:** Built-in audience of developers searching for APIs
- **Your own docs site:** Better margins, full control
- **API directories:** ProgrammableWeb, API List, Public APIs
- **Content marketing:** "How to [solve problem] with [your API]" tutorials

## Action Items

- [ ] Identify one data transformation or processing task you do regularly
- [ ] Build a single endpoint that does it (1-2 hours)
- [ ] Add API key authentication and basic rate limiting
- [ ] Write clear documentation with curl examples
- [ ] List on RapidAPI (free, instant distribution)
- [ ] Create a simple pricing page with 3 tiers

## Time Required

**Building the API:** 10-15 hours (over 2 weekends)
**Documentation:** 3-4 hours
**Setting up billing:** 2-3 hours
**Ongoing maintenance:** 30-60 min/week (monitoring, occasional bug fixes)
**Adding features:** 2-3 hours/month based on customer requests

## Real Examples

- **Abstract API:** Suite of simple APIs (email validation, IP geolocation, VAT). Started as a side project, grew to significant revenue.
- **ScreenshotOne:** Takes screenshots of websites via API. Solo developer, usage-based pricing. Minimal maintenance.
- **Remove.bg:** Background removal API. Started simple, now processes millions of images. (Grew beyond side project, but started as one.)
- **Hunter.io:** Email finder API. Started as a solo project, bootstrapped to $3M+ ARR before raising money.
- **RapidAPI sellers:** Many solo devs earn $500-3000/mo from niche APIs on the marketplace with zero marketing effort.

## Pitfalls

- **Pitfall #1: Building without rate limiting.** One abusive user can bankrupt your serverless bill. Always rate limit.
- **Pitfall #2: No free tier.** Developers want to test before committing. 100 free requests/month costs you nothing and builds your funnel.
- **Pitfall #3: Poor documentation.** If a developer can't figure out your API in 5 minutes, they'll leave. Invest in docs.
- **Pitfall #4: Ignoring uptime.** APIs need to be reliable. Set up monitoring (UptimeRobot, free tier) and a status page.
- **Pitfall #5: Building something easily replicated.** "Random number API" isn't a business. Add value through data, speed, or domain expertise.

---

[← Templates & Digital Products](./chapter-03-templates.md) | [Next: Technical Content →](./chapter-05-content.md)
