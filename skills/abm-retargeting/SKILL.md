---
name: abm-retargeting
description: "Use when planning, building, or troubleshooting retargeting and engagement follow-up for ABM target accounts — reading ad engagement back from LinkedIn at account and contact level, moving accounts to Aware or Interested, routing interested accounts to email and LinkedIn outreach lanes, alerting account owners, segmenting audiences by engagement level or page visited, setting ad frequency caps and creative rotation, sequencing a multi-channel play after a trigger, setting up website or matched audiences in LinkedIn, Meta, or Google, syncing a database of accounts to ad audiences, or weighting multi-touch attribution for retargeting. Also use when someone treats ABM retargeting like generic display retargeting, mentions the ad or the visit in the first email, or is seeing ad fatigue on target accounts."
license: MIT
metadata:
  author: automatewithuday
  source: martechs.io
  version: "1.1"
---

# ABM retargeting

Reading engagement back, acting in lanes, audience segmentation, frequency management, and multi-channel orchestration for Account-Based Marketing retargeting.

ABM retargeting is not the same as generic display retargeting. ABM retargeting:

1. **Targets known accounts** — people at specific companies already in your ICP
2. **Respects the buying committee** — different messages for different roles
3. **Coordinates across channels** — ads + email + BDR outreach + direct mail in sync
4. **Accelerates pipeline** — re-engages warm accounts that stalled
5. **Wins back lost deals** — systematically reactivates churned or lost opportunities

**Stack this skill assumes:** an agent reads the skill, a tool layer (Deepline) runs the providers, and the `abm_accounts` table from `abm-target-accounts` holds the state in any SQL database. Provider names below are the ones we run; swap in any equivalent reachable through the tool layer. The CRM gets a write-back; it is not where the logic runs.

Related: `abm-measurement` for program-level metrics, ROI, and reporting. The attribution weights in this skill are for optimizing retargeting touches, not for reporting program ROI.

## How to apply this skill

When asked to plan, build, or fix ABM retargeting:

1. Gather inputs (ask for what's missing):
   - The `abm_accounts` rows for the campaign (stage, tier, 30-day counts) and the contacts table
   - The company's domain (to list its live ads) and the Campaign Manager company engagement report
   - Which site pages are tagged (LinkedIn Insight Tag, Meta Pixel, Google Tag) and which pages matter (pricing, demo, case studies, blog)
   - Channels available: LinkedIn, Meta, Google, email (Smartlead or equivalent), LinkedIn outreach (HeyReach or equivalent), BDR, direct mail, Slack
   - Current frequency and number of active creatives
   - Which accounts are high-value and which contacts are executives
2. Build in this order: engagement read-back → stage moves → lanes and alerts → segment tiers → frequency and rotation plan → day-by-day play → platform audience setup → database-to-platform sync loop.
3. Report: how engagement lands in the table and at what cadence, which accounts moved stage this week, who went to which lane with the problem each email leads with, the tier each account falls into and the content it should get, the frequency cap and rotation cadence per segment, and the exact setup steps for each platform in use.

Do not run one ad on repeat, lean on platform lookalike audiences, prospect on Meta, or mention the ad or the visit in outreach. Every audience is known accounts, never anonymous traffic.

## Read engagement back

Job: the table knows who warmed up, at company and contact level, from the same rows.

```
1. List every live ad for your domain with the post link behind it
   → Adyntel through the tool layer (or the Apify LinkedIn Ads scraper)
2. Scrape the reactions and comments on each post
   → HarvestAPI post engagement
3. Match each engaging person to an account (domain, then LinkedIn company)
   → write one row per person per post to abm_engagements
4. Roll engagements up to the company → engagements_30d, engaged_people_7d on abm_accounts
5. Impressions and clicks per account still come from the Campaign Manager
   company engagement report, read in weekly → impressions_30d, clicks_30d
```

```sql
create table abm_engagements (
  person_linkedin text, domain text, campaign text,
  post_url text, kind text,        -- reaction | comment
  observed_at date
);
```

Why: the contact view and the company view come from the same rows, so the number sales sees on the account is the sum of people they can name.

## Act in lanes

Stage moves (from `abm-target-accounts`): 50 impressions moves an account to Aware; 5 clicks or 10 engagements moves it to Interested.

| Condition | Lane |
|---|---|
| Interested AND a known person engaged | Email sequence (Smartlead) and LinkedIn sequence (HeyReach), pushed through the tool layer, from the name whose ads they saw |
| 3 or more engaged people at one account in a week | Slack alert to the account owner the same day |
| Interested, no response by day 21 | Drop to Warm, reduce frequency, change the angle |
| Executive at a high-value account | Direct mail and InMail on top of the lanes |

The email talks about the problem the signals add up to. It never mentions the ad, the post, or the visit.

Why: outbound after the ads means the first email comes from a name they have seen in their feed. ~4 impressions per person per week with 3 or 4 creatives live keeps that recall from turning into fatigue.

## Audience segmentation

### Engagement-based tiers

Score accounts by cumulative engagement:

```
1-2 touchpoints  → Light engagement    → Awareness content
3-5 touchpoints  → Moderate engagement → Solution content
6-10 touchpoints → Heavy engagement    → Conversion content
10+ touchpoints  → Hot account         → BDR outreach + direct offers
```

### Website retargeting setup

```
1. Install LinkedIn Insight Tag on all pages
2. Create URL-based audiences for key pages:
   - /pricing → "Pricing Page Visitors"
   - /demo → "Demo Page Visitors"
   - /case-studies/* → "Case Study Readers"
   - /blog/* → "Blog Readers"
3. Set lookback windows (7, 30, 90, 180 days)
4. Exclude converted leads to avoid waste
```

## Frequency management

- **Too low:** account never remembers you, no brand recall, wasted impressions.
- **Too high:** ad fatigue, negative brand perception, wasted budget, annoying buyers.

**Target: about 4 impressions per person per week.** Bottom-of-funnel accounts can run higher — up to roughly 15 per 30 days — because they are close to a decision and the reinforcement is intentional.

Creative rotation is what makes this work. Run several distinct ads, not one ad on repeat. At about 4 per week with 3–4 active creatives, each person sees variety, so the frequency stays productive rather than fatiguing.

### Rotation schedule by audience temperature

```
HOT audiences (0-14 days):
  → Rotate creative every 2 weeks
  → 3-4 active variants minimum
  → Test different CTAs aggressively

WARM audiences (15-45 days):
  → Rotate creative every 3-4 weeks
  → 2-3 active variants
  → Test different angles/proof points

COOL audiences (46-90 days):
  → Rotate creative monthly
  → 2 active variants sufficient
  → Focus on reactivation messaging
```

## Multi-channel orchestration: trigger play

The trigger is a stage move to Interested, a pricing-page visit by a known account, or a job-change signal. The play is the same.

```
Day 0:  Trigger lands in the table
        → Add to "Hot" retargeting segment

Day 1:  LinkedIn ad (case study)
        Email 1: leads with the problem the signals add up to (never the ad or the visit)

Day 3:  Meta retargeting ad (social proof)

Day 5:  LinkedIn ad (product demo)
        LinkedIn connection request from the same sender

Day 7:  Email 2: value proposition reminder
        LinkedIn ad (comparison content)

Day 10: BDR outreach email
        Meta ad (urgency/offer)

Day 14: Direct mail (if high-value account)
        LinkedIn InMail (if executive)

Day 21: If no response → move to "Warm" segment
        Reduce frequency, change messaging angle
```

## Attribution for retargeting

```
Multi-Touch Attribution for ABM:

First Touch (20%):    What channel introduced the account?
Last Touch (20%):     What channel got the meeting/conversion?
Linear (60%):         Distributed across all touchpoints

Weight adjustments:
  - BDR meeting booked: 2x weight
  - Content download: 1.5x weight
  - Ad click: 1x weight
  - Ad impression: 0.5x weight
  - Email open: 0.25x weight
```

## Platform setup

### LinkedIn Campaign Manager

```
1. Push the tier company list through the tool layer (audience_kind companies)
   → every sync replaces the list; push the full list weekly
2. Audience > Create Audience > Website; select pages (OR logic for multiple URLs)
3. Set lookback window (7/30/90/180 days)
4. Combine: Website visitors AND Company list
   → This retargets only known accounts who visited
5. Serves past 300 matched members; matches best past 1,000 companies; ~48h
```

### Meta Business Manager

```
1. Install Meta Pixel on ABM landing pages
2. Push hashed contact lists through the tool layer (mode replace for full snapshots)
3. Create Custom Audience from website traffic
4. Delivery status 411 = the list matched poorly; fix the contact list, not the creative
5. Use Lookalike audiences sparingly (dilutes ABM precision)
6. Focus on retargeting, not prospecting on Meta
```

### Google Ads

```
1. Push hashed contact lists as Customer Match through the tool layer
2. Create remarketing lists from Google Tag; target specific pages (pricing, demo request)
3. Use RLSA for search intent + retargeting combo
4. Combine with IP-to-company targeting where available
5. Note: Match rates are low for B2B - use as supplement only
```

## Database → ad platform → database loop

```
abm_accounts (tier, stage per campaign)
  ↓ weekly play through the tool layer
LinkedIn company audiences per tier (replace) · Meta + Google hashed contact lists
  ↓ ~48 hour sync
Campaign Manager targets the audience
  ↓
Engagement comes back two ways:
  · Campaign Manager company engagement report → impressions_30d, clicks_30d
  · Live ads (Adyntel/Apify) → post links → HarvestAPI reactions and comments → abm_engagements → engagements_30d
  ↓
Stage rules run → stage changes in the table → lanes fire
  ↓
CRM gets stage, tier, scores written back (optional)
  ↓
Next weekly push rebuilds every platform list from the table
```

## Quick reference

| Decision | Rule |
|---|---|
| Engagement sources | Impressions/clicks: Campaign Manager company report weekly · Engagements: live ads → post links → reactions and comments, matched to accounts |
| Stage moves | ≥50 impressions → Aware · ≥5 clicks or ≥10 engagements → Interested |
| Outreach lane | Interested + known person engaged → email and LinkedIn sequences through the tool layer; email leads with the problem, never the ad |
| Alert | 3+ engaged people at one account in a week → Slack to the owner same day |
| Content by engagement | 1–2 touches: awareness · 3–5: solution · 6–10: conversion · 10+: BDR outreach + direct offers |
| Frequency cap | ~4 impressions / person / week; bottom-of-funnel up to ~15 per 30 days |
| Creatives active | HOT 3–4 · WARM 2–3 · COOL 2 |
| Rotation cadence | HOT every 2 weeks · WARM every 3–4 weeks · COOL monthly |
| Audience temperature | HOT 0–14 days · WARM 15–45 · COOL 46–90 |
| Lookback windows | 7 / 30 / 90 / 180 days |
| Play exit | Day 21 with no response → move to Warm, reduce frequency, change angle |
| Attribution split | First 20% · Last 20% · Linear 60%; BDR meeting 2x, download 1.5x, click 1x, impression 0.5x, email open 0.25x |
| LinkedIn audience logic | Website visitors AND company list · sync replaces · 300 members to serve · ~48h |
| Meta | Replace mode for snapshots · status 411 = poor match |

## Common mistakes

- Mentioning the ad, the post, or the visit in the first email — lead with the problem the signals add up to.
- Reading engagement at company level only — scrape the post engagers so the company number is the sum of named people.
- Waiting on a connector product for company-level engagement — the Campaign Manager report read weekly is enough.
- Running one ad on repeat — frequency without rotation is fatigue. Keep 3–4 variants live for hot audiences.
- Retargeting anonymous traffic — always intersect website visitors with the company list so only known accounts see ads.
- Appending to a LinkedIn audience — every sync replaces it; rebuild the full list from the table each week.
- Blaming the creative for a Meta 411 — it is the contact list that matched poorly.
- Using lookalike audiences — they dilute ABM precision. Use sparingly or not at all.
- Prospecting on Meta — Meta is for retargeting in ABM, not net-new.
- Leaning on Google remarketing — B2B match rates are low; use it as a supplement to LinkedIn, not the core.
- Not excluding converted leads — wasted spend and an annoyed customer.
- Leaving accounts in the Hot segment forever — no response by Day 21 means move to Warm and change the angle.
