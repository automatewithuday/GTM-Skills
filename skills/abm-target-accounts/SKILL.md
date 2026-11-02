---
name: abm-target-accounts
description: "Use when building, sizing, scoring, tiering, or managing a target account list for ABM — working out how many accounts a revenue target needs, sizing TAM from closed-won lookalike filters, scoring fit and timing separately, setting A/B/C/D tiers with a budget split, building the buying committee, pushing company and contact audiences to LinkedIn, Meta, or Google, or keeping ABM stage state in a database (Supabase, Postgres, any SQL) with an optional CRM write-back. Also use when a team is starting ABM from leads instead of accounts, blends fit and timing into one score, or relies on platform lookalike audiences or website de-anonymization."
license: MIT
metadata:
  author: automatewithuday
  source: martechs.io
  version: "1.1"
---

# ABM target account lists

How to build, score, tier, and manage target account lists for ABM campaigns.

ABM starts with accounts, not leads. You're choosing who to pursue before anything else. Every dollar of ad spend and every BDR hour gets concentrated on accounts that actually fit your ICP.

**Stack this skill assumes:** an agent (Claude Code) reads the skill, a tool layer (Deepline) runs the data providers, and a database holds the state. Provider names below are the ones we run; any equivalent provider reachable through Deepline does the same job. A CRM (HubSpot or any other) is a sync target for the sales team, not the system of record.

Related: `abm-retargeting` (reading engagement back and acting on it) and `abm-measurement` (program metrics and ROI). All three skills read and write the same `abm_accounts` table and use the same stage thresholds: 50 impressions, 5 clicks or 10 engagements.

## How to apply this skill

When asked to build or fix a target account list:

1. Gather inputs (ask for what's missing):
   - Revenue target, ACV, close rate, qualification rate — if the user has no stage rates, use the benchmark rates in the sizing example
   - Closed-won list from the CRM (for lookalike filters) and any win-loss analysis
   - Providers available through the tool layer: company search and enrichment (Crustdata), technographics (BuiltWith), hiring signals (PredictLeads), job changes (Deepline job change check), LinkedIn post engagement (HarvestAPI), email finding (Prospeo), email validation (LeadMagic), audience push (LinkedIn, Meta, Google)
   - Which database holds state (Supabase, Postgres, anything with SQL) and whether a CRM write-back is wanted
   - Whether the list is for 1:1, 1:few, or 1:many plays (decides which tiers are in scope)
2. Work in this order: size the list → size the market and build the list → score fit and timing separately → tier and write the budget split → build the buying committee → push audiences → write state → schedule the weekly rebuild.
3. Report: required account count with the math shown, the lookalike filters and the TAM count they return, tier cut-offs and the spend share per tier, the table the state lives in, the five stage definitions with their thresholds, and the weekly job. Say what the program should look like at 90 days and at maturity using the illustrative figures.

Do not score from website visits or de-anonymized traffic, and do not blend fit and timing into one number.

## How many accounts you need

The math matters: to close $1M in ARR from ABM with a $50K ACV, 25% close rate, and 75% qualification rate, you need ~3,250 target accounts in your campaigns (working backwards through stage conversion benchmarks).

```
Revenue Target ÷ ACV = Deals Needed
Deals ÷ Close Rate ÷ Qualification Rate ÷ Considering Rate ÷ Interested Rate ÷ Aware Rate
= Total Target Accounts
```

Example:

```
$1,000,000 ÷ $50,000 = 20 deals
20 ÷ 0.25 ÷ 0.75 ÷ 0.20 ÷ 0.30 ÷ 0.55 = ~3,250 accounts
```

The headline number: across these stages, roughly 2.5% of targeted accounts convert to pipeline (an open, qualified opportunity) and about 0.6% close. So a ~3,250-account program produces ~80 opportunities and ~20 deals at a $50K deal size.

## 1. Size the market before you buy anything

Job: know the total count of accounts that fit.

```
1. Pull closed-won accounts from the CRM (or the customer table)
2. Enrich each one through the company enrichment provider (Crustdata)
3. Keep the values most winners share: industry, headcount band, region, the tools they run
   → those shared values are the lookalike filters
4. Run a company search with the filters and limit = 1
   → the response carries total_count: that is the TAM, before you spend a credit on rows
5. Add the technographic cut from BuiltWith lists
6. Export rows only once the count is in range for the sizing math above
```

Why: a lookalike is a filter set you can read and argue with. A platform lookalike audience is a model you cannot audit, and it stays inside the ad platform where your database never sees it.

## 2. Score fit and timing separately

Job: one static fit score, one decaying timing score, never blended.

**Fit** is 0 to 100 from the closed-won filters. Set it once a quarter. It decides the tier.

**Timing** is a stack of dated signals. It decides who gets worked this week inside the tier.

| Signal | Source via the tool layer |
|---|---|
| Open roles on the team you sell to | PredictLeads job postings |
| A past champion who moved in the last 14 to 45 days | Deepline job change check |
| People at the account engaging with your LinkedIn posts | HarvestAPI post reactions and comments |
| Closed-lost accounts that went quiet | CRM closed-lost export |

Decay rule:

```
signal age 0–30 days   → full points
signal age 31–60 days  → half points
signal age 61+ days    → 0
No single signal is worth more than half the timing max.
```

Why: blend them into one number and a perfect-fit account with nothing happening ranks next to a poor-fit account with a job post. One trigger is public and everyone sees it the same day. A stack on one account describes a problem you can offer to fix.

## 3. Tier the list and write the budget split down

Job: A/B/C/D tiers with a spend share each.

```
A-tier (80–100): worked by hand, ads by company name
B-tier (60–79):  ads per segment
C-tier (40–59):  one message per segment, 1:many only
D-tier (<40):    out
```

- Set the A cut-off where the team can work every A account by hand.
- Decide the spend share per tier before launch and treat it as a starting point.
- Write the tier and both scores to the account row every week (and to the CRM company record if sales reads the CRM).

Why: the split is the ABM budget. Everything else is execution.

## 4. Build the buying committee, then the audiences

Job: the people at each account, then the ad lists.

```
1. Person search by the titles that buy (Crustdata person search, filtered to the account list)
2. Email finding (Prospeo)
3. Email validation (LeadMagic) is the gate → only valid goes forward
4. Write contacts to the contacts table (and to the CRM if wanted)
5. Push audiences through the tool layer:
   → LinkedIn: company lists per tier (audience_kind companies)
   → Meta and Google: hashed contact lists
```

Platform rules that decide whether the audience serves:

| Platform | Rule |
|---|---|
| LinkedIn company lists | Match best past 1,000 companies; serve past 300 matched members; ~48h to be ready |
| LinkedIn contact lists | Want 10,000+ rows |
| LinkedIn sync | Every sync replaces the list, so the weekly push is a refresh, not an append |
| Meta | A delivery status of 411 means the list matched poorly |

Why: A gets ads by company name, B gets ads per segment, C gets one message per segment. The depth follows the tier because the tier already encodes the fit.

## Where the state lives

One table, one row per account per campaign. Supabase, Postgres, SQLite, anything with SQL. The retargeting and measurement skills read the same rows.

```sql
create table abm_accounts (
  domain            text not null,
  campaign          text not null,
  fit_score         int,            -- 0–100, set quarterly
  timing_score      int,            -- recomputed weekly from abm_signals
  tier              char(1),        -- A/B/C/D
  stage             text,           -- identified | aware | interested | considering | selecting
  impressions_30d   int default 0,
  clicks_30d        int default 0,
  engagements_30d   int default 0,
  engaged_people_7d int default 0,
  stage_changed_at  timestamptz,
  owner             text,
  primary key (domain, campaign)
);

create table abm_signals (          -- one row per dated timing signal
  domain text, campaign text, signal text, source text, observed_at date, points int
);
```

Stage definitions (the same five everywhere):

| Stage | Rule |
|---|---|
| Identified | fit_score ≥ 40 (tier C or above), in the campaign |
| Aware | impressions_30d ≥ 50 |
| Interested | clicks_30d ≥ 5 OR engagements_30d ≥ 10 |
| Considering | demo booked OR trial signup |
| Selecting | deal stage = open in the CRM |

If sales works out of the CRM, write `stage`, `tier`, `fit_score`, and `timing_score` to the company record on the same weekly run and build the CRM's active lists on those properties. The database stays the source of truth.

## Stage progression: the weekly job

One scheduled play, read then write:

```
1. Recompute timing_score from abm_signals with the decay rule
2. Read impressions and clicks per account from the Campaign Manager company engagement report
   (see abm-retargeting for the post-engagement scrape that fills engagements_30d)
3. Apply the stage rules in order; never move an account backwards here
   IF impressions_30d ≥ 50 AND stage = identified → stage = aware
   IF (clicks_30d ≥ 5 OR engagements_30d ≥ 10) AND stage = aware → stage = interested
     → hand the account to the outbound lanes in abm-retargeting
4. Rebuild the tier lists and push them to the ad platforms (LinkedIn replaces on sync)
5. Write stage, tier, both scores to the CRM if it is in use
```

No connector product is needed for company-level engagement: the Campaign Manager report is read in weekly and the numbers land in the table.

## What a well-run program looks like

The figures below are illustrative of a well-run program. They show the shape of ABM economics over time rather than a guaranteed result.

### First campaign (roughly 90 days)

| Metric | Illustrative result |
|---|---|
| Accounts touched | ~1,400 |
| Total cost | ~$52K (ads + tools) |
| Pipeline generated | ~$655K |
| Pipeline per $ spent | ~$12 |
| Team | ~4.5 FTE |

### Mature program (cumulative, 12–18 months)

| Metric | Illustrative result |
|---|---|
| Accounts touched | ~26,000 |
| Total LinkedIn ad spend | ~$490K |
| Pipeline generated | ~$5.3M |
| Pipeline per $ spent | ~$11 |
| ROAS (closed won) | ~2x |
| Team | ~4.5 FTE |

Versus cold outbound: a mature ABM program typically reaches the same pipeline faster and at a lower cost than cold outbound alone.

## Quick reference

| Item | Rule / number |
|---|---|
| List size | Deals ÷ close ÷ qualification ÷ considering ÷ interested ÷ aware |
| Benchmark stage rates | Aware 55% · Interested 30% · Considering 20% · Qualified 75% · Close 25% |
| Headline conversion | ~2.5% of targeted accounts → pipeline · ~0.6% close |
| Worked example | $1M ARR at $50K ACV → 20 deals → ~3,250 accounts → ~80 opps |
| TAM count | Company search with the lookalike filters and limit 1 → total_count, no row credits spent |
| Fit score | 0–100 from closed-won filters · set quarterly · decides the tier |
| Timing score | Dated signals · full points 30 days, half to 60, then 0 · no signal > half the max · decides who is worked this week |
| Tiers | A 80–100 (by hand, ads by company name) · B 60–79 (ads per segment) · C 40–59 (one message per segment, 1:many only) · D <40 out |
| Budget | Spend share per tier decided before launch |
| Contacts | Title search → email find → validation gate → only valid goes forward |
| LinkedIn audiences | 1,000+ companies to match well · 300 matched members to serve · 10,000+ rows for contact lists · ~48h · sync replaces |
| Meta | Delivery status 411 = poor match |
| Stage thresholds | Aware ≥50 impressions · Interested ≥5 clicks or ≥10 engagements · Considering demo/trial · Selecting open deal |
| State | `abm_accounts` table in any SQL database · CRM is a weekly write-back |
| 90-day shape | ~1,400 accounts · ~$52K · ~$655K pipeline · ~$12 per $1 |
| Mature shape | ~26,000 accounts · ~$490K ads · ~$5.3M pipeline · ~$11 per $1 · ~2x ROAS |

## Common mistakes

- Starting from leads — pick the accounts first; every dollar and BDR hour concentrates on them.
- Guessing list size — work backwards from the revenue target through the stage rates.
- Paying for rows before knowing the count — a limit-1 search returns the TAM for free.
- Using a platform lookalike audience — it is a model you cannot audit and the database never sees it. Lookalikes are filter sets.
- Blending fit and timing — a perfect-fit account with nothing happening ends up next to a poor-fit account with one job post.
- Letting one timing signal dominate — cap every signal at half the max; a single public trigger is not a reason.
- Scoring from website visits or de-anonymized traffic — one test identified 1 company out of 300 visitors, itself.
- Putting C-tier accounts into 1:1 plays — C-tier is 1:many only; D-tier is excluded.
- Appending to a LinkedIn list — every sync replaces it; push the full list every week.
- Launching under 300 matched LinkedIn members, or before the ~48h audience sync completes.
- Making the CRM the source of truth — stage lives in the table; the CRM gets a weekly write-back.
