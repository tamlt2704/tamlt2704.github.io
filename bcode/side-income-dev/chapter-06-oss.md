# Chapter 6: Getting Paid for Open Source

[← Technical Content](./chapter-05-content.md) | [Next: High-Value Freelancing →](./chapter-07-freelance.md)

---

## The Strategy

Open source doesn't have to mean "free labor." Developers are earning $3K-20K/month from OSS through sponsorships, dual licensing, premium features, and support tiers. The key: build something useful, build an audience around it, then offer paid value on top.

**Monetization models for OSS:**

1. **GitHub Sponsors / Open Collective:** Direct donations from users and companies who depend on your work
2. **Dual licensing:** MIT for individuals, paid license for commercial use
3. **Open core:** Core is free, premium features/plugins are paid
4. **Sponsorware:** New features are sponsor-only for 2-4 weeks, then go public
5. **Support tiers:** Free community support, paid priority support ($200-500/mo per company)
6. **Hosted version:** Self-host is free, managed hosting is paid

**Why this works:**
- Companies have budgets for tools they depend on
- Your OSS project is your marketing (people discover you through it)
- Trust is pre-built (they've already used your code)
- Switching costs are high (once integrated, they'll pay to keep it working)

## The Math

**GitHub Sponsors tiers:**

| Tier | Price | What They Get | Target |
|------|-------|---------------|--------|
| Supporter | $5/mo | Name in README, warm feeling | Individual devs |
| Backer | $25/mo | Priority issues, early access | Power users |
| Bronze | $100/mo | Logo in README, priority support | Small companies |
| Silver | $500/mo | Direct access, feature requests | Mid-size companies |
| Gold | $2000/mo | Dedicated support, custom features | Enterprise |

**Realistic scenario (established project with 1K+ stars):**
- 20 × $5 = $100
- 10 × $25 = $250
- 5 × $100 = $500
- 2 × $500 = $1,000
- **Total: $1,850/mo**

**Dual licensing scenario:**
- MIT for personal/OSS use (free)
- Commercial license: $99/year per company
- 30 companies × $99/year = $2,970/year ($247/mo)
- Scale: 100 companies = $9,900/year

## The Strategy: Building a Sponsorable Project

**Step 1: Build something genuinely useful** (not a toy project)
- Solve a real problem that companies face
- Focus on developer tools, libraries, or infrastructure
- Quality documentation is non-negotiable

**Step 2: Build an audience around it**
- Tweet about development progress
- Write blog posts about the "why" behind design decisions
- Engage with issues and PRs (community = value)

**Step 3: Make sponsoring easy**
- Set up GitHub Sponsors with clear tiers
- Add a "Sponsors" section to your README
- Mention sponsorship in your docs ("This project is maintained by...")
- Send a personal email to companies using your project

**Step 4: Add paid value**
- Premium plugins or integrations
- Priority support channel (Discord or email)
- Commercial license for companies that need it

## Action Items

- [ ] Identify a tool/library you've built that others might use
- [ ] Clean it up: good README, docs, examples, and a LICENSE file
- [ ] Publish it on GitHub with a clear "Contributing" guide
- [ ] Set up GitHub Sponsors with 3-5 tiers
- [ ] Add a FUNDING.yml to your repo
- [ ] Write a blog post introducing the project and why you built it
- [ ] If you have an existing popular project, email 5 companies using it about sponsorship

## Time Required

**Initial project setup:** 10-20 hours (if starting from scratch)
**Ongoing maintenance:** 2-4 hours/week (issues, PRs, releases)
**Sponsorship outreach:** 1-2 hours/month
**Content about the project:** 1-2 hours/week

## Real Examples

- **Calcom (Cal.com):** Open-source scheduling. Dual license model. Started as a side project, now a company — but the model works at any scale.
- **Sindre Sorhus:** Maintains 1000+ npm packages. Earns $10K+/mo from GitHub Sponsors alone.
- **Evan You (Vue.js):** Started as a side project. Patreon/sponsors funded full-time work before any company was involved.
- **Anthony Fu:** OSS contributor earning $5K+/mo through GitHub Sponsors by maintaining popular developer tools.
- **Sponsorware examples:** Several devs release features to sponsors first, then open-source after 30 days. Creates urgency to sponsor.

## Pitfalls

- **Pitfall #1: Expecting sponsorship from a 50-star repo.** You need real users (ideally companies) before sponsorship works.
- **Pitfall #2: Feeling guilty about charging.** Companies save thousands using your free work. Charging $100/mo is a bargain for them.
- **Pitfall #3: Burning out on free support.** Set boundaries. Free tier = community support (GitHub issues). Paid tier = direct response.
- **Pitfall #4: Choosing a saturated space.** Don't build "yet another state management library." Find underserved niches.
- **Pitfall #5: No license clarity.** If companies can't figure out if they can use your code commercially, they won't — and they won't sponsor either. Be explicit.

---

[← Technical Content](./chapter-05-content.md) | [Next: High-Value Freelancing →](./chapter-07-freelance.md)
