---
name: prospeo-full-export
description: "Use when exporting an entire Prospeo people search to CSV, including searches over the 25K result limit that need state-by-state splitting. Also use when someone built filters in Prospeo's UI and wants every matching contact out via the API."
license: MIT
metadata:
  author: automatewithuday
  source: martechs.io
  version: "1.0"
  category: list-building
---

# Prospeo Full Search Export

Extract your entire Prospeo people search to a CSV file. Build your search in Prospeo's UI, then let Claude pull every single result via the API — even if the search has more than 25,000 results.

## Required step: Qualify with /icp-prompt-builder (do not skip)

Before exporting more than 500 contacts, run Prospeo on a 50-contact sample, then invoke [`/icp-prompt-builder`](../icp-prompt-builder/SKILL.md) to tune a qualification prompt in 3-5 rounds of 10 (with your approval each round). Apply the tuned prompt to the full export to filter out bad fits.

**Why required:** email enrichment downstream costs $0.05-$0.15 per person. A 25K export that's 40% wrong-fit wastes $500-$1,500 on email-finding that goes nowhere. The ICP prompt builder takes 10-15 min and saves that cost 40-70% of the time.

**Safe skip:** only if your Prospeo filter is already extremely tight (e.g., 5 exact titles + 1 industry + narrow headcount) AND you've run the same filter successfully before. Even then, run [`/icp-prompt-builder`](../icp-prompt-builder/SKILL.md) on 10 samples as a sanity check — it's nearly free to confirm.

## What This Does

1. You build a search in Prospeo's web UI (filters for title, location, industry, company size, etc.)
2. You tell Claude what filters you used
3. Claude translates those filters into Prospeo API calls
4. Claude paginates through every page of results and exports to CSV
5. For large US searches (25K+), Claude automatically splits by state to get everything

## Setup (First Time Only)

### Step 1: Create a Prospeo Account

1. Go to [prospeo.io](https://prospeo.io) and sign up
2. Choose a plan that includes the **Search Person API** (most paid plans do)
3. Each API request that returns results costs **1 credit** and returns 25 contacts

### Step 2: Get Your API Key

1. Log into Prospeo
2. Go to **Settings > API** (or visit [prospeo.io/app/settings/api](https://prospeo.io/app/settings/api))
3. Copy your API key

### Step 3: Set Your API Key

Set it as an environment variable so Claude can use it:

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
export PROSPEO_API_KEY="your_api_key_here"
```

Then restart your terminal or run `source ~/.zshrc`.

**Security note:** Never paste your API key directly into a script file. Always use environment variables.

---

## How to Use

### Step 1: Build Your Search in Prospeo's UI

Go to [prospeo.io/app/search](https://prospeo.io/app/search) and use the filters to build your search. The UI lets you filter by:

- **Job title** (e.g., "CEO", "VP Sales", "Head of Marketing")
- **Location** (e.g., "United States", "California", "New York")
- **Company industry** (e.g., "Information Technology", "Healthcare")
- **Company headcount** (e.g., 11-500 employees)
- **Company technology** (e.g., "Salesforce", "HubSpot")
- **Revenue range**
- **Contact details** (has verified email, has phone number)

Note the total result count shown in the UI — you'll need this to estimate credits.

### Step 2: Tell Claude Your Filters

Just describe what you filtered for. Examples:

> "I searched for CEOs and CTOs at companies with 11-500 employees in the US, in the Information Technology industry, with verified emails."

> "I'm looking for VP of Sales and Head of Sales at SaaS companies in California with 50-200 employees."

> "I need all Marketing Directors in the US at companies using HubSpot, 20-1000 headcount."

### Step 3: Claude Runs the Export

Claude will:
1. Confirm the filters and estimated credit cost
2. Create a TypeScript script
3. Run it to paginate through all results
4. Export everything to a CSV file in your current directory

---

## Filter Reference

Moved to [references/api-reference.md](references/api-reference.md) — filter values and request/response details.

## API Details

Moved to [references/api-reference.md](references/api-reference.md) — filter values and request/response details.

## The 25K Limit: State-by-State Splitting

Prospeo caps any single search at 25,000 results (1,000 pages x 25 per page). If your US-wide search has more than 25K results, the script automatically splits it into 50 separate state-level searches.

**How it works:**
1. Run the search once to check `total_count`
2. If > 20,000, switch to state-by-state mode
3. Replace `"United States #US"` with each state (e.g., `"California, United States #US"`)
4. Paginate through each state's results
5. Deduplicate across states (by LinkedIn URL)

This means you can extract **hundreds of thousands** of results from a single search definition.

### US States (ordered by population for efficiency)

```
California, Texas, Florida, New York, Illinois, Pennsylvania,
Ohio, Georgia, North Carolina, Michigan, New Jersey, Virginia,
Washington, Arizona, Massachusetts, Tennessee, Indiana, Missouri,
Maryland, Wisconsin, Colorado, Minnesota, South Carolina, Alabama,
Louisiana, Kentucky, Oregon, Oklahoma, Connecticut, Utah, Iowa,
Nevada, Arkansas, Mississippi, Kansas, New Mexico, Nebraska,
Idaho, West Virginia, Hawaii, New Hampshire, Maine, Montana,
Rhode Island, Delaware, South Dakota, North Dakota, Alaska,
Vermont, Wyoming
```

---

## Script Template

Moved to [references/script-template.md](references/script-template.md) — the complete export script to copy into your project.

## Credit Cost Estimation

Before running, Claude will estimate the credit cost:

| Total Results | Pages | Credits | Approximate Cost (varies by plan) |
|--------------|-------|---------|-----------------------------------|
| 1,000 | 40 | 40 | ~$2 |
| 5,000 | 200 | 200 | ~$10 |
| 25,000 | 1,000 | 1,000 | ~$50 |
| 100,000 (state split) | ~4,000 | ~4,000 | ~$200 |

Claude will always tell you the estimated cost and ask for confirmation before running the full export.

---

## Example Conversations

**Simple search:**
> "Export all CEOs at 11-50 person companies in California in the SaaS industry with verified emails."

**Large US-wide search:**
> "I need every VP of Sales and Head of Sales in the US at companies with 50-500 employees. The Prospeo UI shows 87,000 results."

**With exclusions:**
> "Marketing Directors in the US, exclude staffing and recruiting industries, 20-200 headcount, must have verified email."

**With technology filter:**
> "CTOs at companies using Shopify in the US, any company size."

---

## Troubleshooting

### "Set PROSPEO_API_KEY environment variable first"
Your API key isn't set. Run: `export PROSPEO_API_KEY="your_key"` in your terminal.

### "API error: 401"
Your API key is invalid. Check it at [prospeo.io/app/settings/api](https://prospeo.io/app/settings/api).

### "API error: 402"
You're out of credits. Top up your Prospeo account.

### "API error: 429"
Rate limited. The script handles this automatically with exponential backoff. If it persists, you're making too many concurrent requests — only run one export at a time.

### Results seem low
- Check that your location format is correct (must include `#US`, `#GB`, etc.)
- Broaden your title filters — Prospeo does fuzzy matching by default
- Remove the `person_contact_details` filter to see all results (not just those with verified emails)

### Duplicates across states
The script deduplicates by LinkedIn URL automatically. Some contacts may appear in multiple state searches if they've relocated — the dedup handles this.

---

## Requirements

- **Node.js 18+** (for native `fetch` support)
- **TypeScript** (`npm install -g tsx` to run .ts files directly)
- A Prospeo account with API credits

No other dependencies needed — the script uses only built-in Node.js modules.

---

## What to do next

**Run [`/icp-prompt-builder`](../icp-prompt-builder/SKILL.md)** on a 50-contact sample (required step above). Apply the tuned prompt to your full export, then [`/list-quality-scorecard`](../list-quality-scorecard/SKILL.md) to grade.

Next: [`/campaign-copywriting`](../campaign-copywriting/SKILL.md) → [`/smartlead-campaign-upload-public`](../smartlead-campaign-upload-public/SKILL.md).

**Or wait:** if Prospeo returned <500 contacts for your filter, your ICP may be too narrow. Broaden titles (add synonyms) or industries before scaling.

## Related skills

- [`/icp-prompt-builder`](../icp-prompt-builder/SKILL.md) — required qualification pass before scaling
- [`/list-quality-scorecard`](../list-quality-scorecard/SKILL.md) — grade the filtered list
- [`/campaign-copywriting`](../campaign-copywriting/SKILL.md) — write the emails
- [`/smartlead-campaign-upload-public`](../smartlead-campaign-upload-public/SKILL.md) — launch in DRAFT
