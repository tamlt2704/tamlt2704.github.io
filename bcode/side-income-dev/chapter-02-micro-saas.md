# Chapter 2: Micro-SaaS — Tiny Tools, Real Revenue

[← MVP in One Hour](./chapter-01-mvp.md) | [Next: Templates & Digital Products →](./chapter-03-templates.md)

---

## The Strategy

Micro-SaaS is the sweet spot for developer-parents. Small, focused tools that solve one problem well, charge $10-50/month, and require minimal maintenance once built. You're not building the next Slack — you're building the tool that saves someone 2 hours per week.

**What makes a good micro-SaaS:**
- Solves one specific problem (not a platform)
- Can be built in 2-4 weekends
- Charges monthly (recurring revenue = predictable income)
- Requires < 2 hours/week maintenance once stable
- Has a clear, findable audience

**Where to find problems:**
- Reddit: r/webdev, r/SaaS, r/smallbusiness — look for "Is there a tool that..."
- Twitter: search "[tool] alternative" or "I wish [tool] could..."
- Your own frustrations at work
- Support forums of existing tools (what are people complaining about?)

## The Math

**The $1,000/month formula:**
- 50 customers × $20/mo = $1,000/mo
- 100 customers × $10/mo = $1,000/mo
- 25 customers × $40/mo = $1,000/mo

**Realistic timeline:**
- Weeks 1-4: Build MVP (20-30 hours total)
- Weeks 5-8: Launch, get first 5 paying customers
- Months 3-6: Grow to 20-50 customers through content + SEO
- Month 6+: Maintenance mode (2 hrs/week)

**Churn reality:** Expect 5-8% monthly churn. You need to add 3-5 new customers/month just to stay flat. This is why multiple products help.

## The Strategy: Tech Stack for Solo Devs

**Recommended stack (fast to build, cheap to run):**
- **Frontend:** Next.js (or Remix)
- **Backend/DB:** Supabase (Postgres + auth + realtime)
- **Payments:** Stripe (subscriptions + billing portal)
- **Hosting:** Vercel (generous free tier)
- **Email:** Resend or Postmark
- **Monitoring:** Sentry free tier

**Total cost until you have paying customers:** $0-20/month

**Micro-SaaS ideas that work:**
| Tool | Target Audience | Price Point |
|------|----------------|-------------|
| Screenshot API | Developers, marketers | $19-49/mo |
| PDF invoice generator | Freelancers | $9-29/mo |
| Webhook tester/debugger | Developers | $15-39/mo |
| Status page (simple) | Small SaaS teams | $10-29/mo |
| Cron job monitor | DevOps, solo devs | $9-19/mo |
| Link shortener with analytics | Marketers | $12-29/mo |

## Action Items

- [ ] Spend 30 minutes browsing Reddit/Twitter for pain points in your niche
- [ ] Pick ONE idea that you could build in under 30 hours
- [ ] Validate it (Chapter 1 method: landing page + price)
- [ ] If validated, build the MVP in 2-4 weekends
- [ ] Launch on Product Hunt, Hacker News, and relevant subreddits
- [ ] Set up Stripe billing with a free trial (7 or 14 days)

## Time Required

**Building:** 20-30 hours (spread over 3-4 weeks)
**Launching:** 3-5 hours
**Ongoing maintenance:** 1-2 hours/week
**Customer support:** 30 min/week (if you write good docs)

## Real Examples

- **Simple Analytics:** Privacy-focused website analytics. Solo founder, started as a side project. Now does $30K+/mo. Started with one feature: page views without cookies.
- **Plausible:** Similar story — two founders, started small, grew to $1M+ ARR by being the "simple alternative" to Google Analytics.
- **ScreenshotOne:** API for taking website screenshots. Solo dev, charges per screenshot. Low maintenance, usage-based revenue.
- **Cron job monitoring tools:** Multiple solo devs run these at $1-5K/mo. Dead simple product, high reliability expectations.

## Pitfalls

- **Pitfall #1: Building a "platform."** You don't have time for a platform. Build a tool.
- **Pitfall #2: Competing on features with funded startups.** Compete on simplicity, price, or niche focus instead.
- **Pitfall #3: Underpricing.** $5/mo attracts the worst customers (most support, most churn). Start at $15+ minimum.
- **Pitfall #4: No free trial, no demo.** People need to try before they buy. 7-day trial, no credit card required.
- **Pitfall #5: Ignoring SEO.** Your best long-term acquisition channel is "best [tool] for [use case]" Google searches. Write comparison pages early.

---

[← MVP in One Hour](./chapter-01-mvp.md) | [Next: Templates & Digital Products →](./chapter-03-templates.md)
