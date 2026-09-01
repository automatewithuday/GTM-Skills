---
name: google-maps-list-builder
description: "Use when targeting local SMBs (restaurants, clinics, gyms, salons, contractors) by category and location and the list should come from Google Maps as a CSV ready for enrichment. Also use when a US-wide category search needs zip-code or city splitting."
license: MIT
metadata:
  source: growthenginenowoslawski/coldoutboundskills
  source-license: MIT
  curator: automatewithuday
  version: "1.0"
  category: list-building
---

# Google Maps List Builder

A self-contained tool for scraping business listings from Google Maps. Give it a search query (e.g., "pizza restaurant") and a location (zip code, city, or coordinates), and it returns structured data for every matching business — written to CSV.

## How this fits in the cold email flow

Google Maps gives you COMPANIES (name, domain, phone, address, ratings). It does NOT give you PEOPLE. To run cold email:

1. Run this skill → CSV of businesses with `company_domain`
2. **Run [`/icp-prompt-builder`](../icp-prompt-builder/SKILL.md) on a sample of 50** — tune a qualification prompt to filter out bad fits before paying for downstream enrichment
3. Run [`/blitz-list-builder`](../blitz-list-builder/SKILL.md) with the filtered CSV → adds owners/managers to each business
4. Run `/email-waterfall` → fills in missing emails
5. Run [`/cold-email-starter-kit`](../cold-email-starter-kit/SKILL.md)'s `smartlead-add-leads.ts` → upload to Smartlead

This skill is only the first step.

## Required step: Qualify with /icp-prompt-builder

**This is a required step. Do not skip it.**

Google Maps will happily return 10,000 "pizza restaurants in Illinois," but most of those won't match your actual ICP (maybe you only want 50-200 seat operators, or only ones without online ordering). Before spending on enrichment, sample ~50 results and run [`/icp-prompt-builder`](../icp-prompt-builder/SKILL.md):

1. Evaluate 10 results with an AI qualification prompt
2. You flag "this one should be NO, they're a chain franchise"
3. Refine, run next 10
4. Stop when 2 rounds show no corrections
5. Apply tuned prompt to filter the rest of the scrape

**Why required:** downstream owner-finding (via [`/blitz-list-builder`](../blitz-list-builder/SKILL.md)) and email waterfall cost $0.10-$0.30 per contact. On a 10,000-business scrape, that's $1K-$3K. Qualifying upfront saves 50-80% of that spend on average.

## What You Need Before Starting

1. **Node.js 18+** and **npm** installed
2. **A RapidAPI account** (free tier available) with a subscription to the **Maps Data API**:
   - Sign up at https://rapidapi.com
   - Subscribe to the API: https://rapidapi.com/alexanderxbx/api/maps-data
   - Copy your RapidAPI key from the dashboard (it's in the `X-RapidAPI-Key` header on any endpoint page)

That's it. No Google Cloud account, no OAuth, no billing setup beyond RapidAPI.

## Project Setup

Create a new project directory and initialize it:

```bash
mkdir google-maps-scraper && cd google-maps-scraper
npm init -y
npm install typescript bottleneck
npm install -D @types/node tsx
```

Add to `package.json` scripts:
```json
{
  "scripts": {
    "scrape": "tsx src/index.ts"
  }
}
```

Create `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "esModuleInterop": true,
    "strict": true,
    "outDir": "dist",
    "rootDir": "src",
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

Set your API key as an environment variable:
```bash
export RAPIDAPI_KEY=your_key_here
```

Or create a `.env` file (add `.env` to `.gitignore`):
```
RAPIDAPI_KEY=your_key_here
```

## File Structure

```
google-maps-scraper/
  data/
    us-zip-codes.csv   # 42,734 US zip codes with city, state, lat/lng, population
  src/
    index.ts           # CLI entry point
    client.ts          # RapidAPI Maps Data client with rate limiting
    types.ts           # TypeScript interfaces
    csv.ts             # CSV export
    zips.ts            # Zip code loader (filter by state, city, population)
```

## Bundled Zip Code Database

The repo includes `data/us-zip-codes.csv` — a complete US zip code reference with 42,734 entries. Columns:

```
zip,primary_city,state,timezone,area_codes,world_region,country,latitude,longitude,irs_estimated_population
```

This lets you scrape an entire state or metro area without manually listing zip codes. The `src/zips.ts` loader provides filtering by state, city, and minimum population.

## Core Files

Moved to [references/core-files.md](references/core-files.md) — the full source of every file in the project (copy them in when setting up).

## Running It

### Local CLI

```bash
# Search pizza places in 3 NYC zip codes
npm run scrape -- --query="pizza restaurant" --zips=10014,10013,10012

# Search ALL dentists in Texas (zips with population >= 5000)
npm run scrape -- --query="dentist" --state=TX --min-pop=5000

# Every gym in California (all 2,657 zip codes — takes a while)
npm run scrape -- --query="gym" --state=CA

# Search dentists across specific cities
npm run scrape -- --query="dentist" --cities="Austin TX,Dallas TX,San Antonio TX"

# Custom output file
npm run scrape -- --query="gym" --zips=90210 --output=./data/gyms.csv
```

### Programmatic Usage

```typescript
import { GoogleMapsClient } from './client.js';

const client = new GoogleMapsClient({
  apiKey: process.env.RAPIDAPI_KEY!,
  requestsPerSecond: 2,
});

// Simple search
const places = await client.search({
  query: 'coffee shop in 94105',
  limit: 20,
});

// Search with coordinates
const { lat, lng } = await client.geocode('94105');
const nearby = await client.search({
  query: 'coffee shop',
  lat,
  lng,
  zoom: 14,
  limit: 20,
});
```

## Deploying as a Web App (Optional)

Moved to [references/web-app.md](references/web-app.md) — optional web UI deployment.

## API Reference

The underlying API is the **Maps Data API** on RapidAPI:
https://rapidapi.com/alexanderxbx/api/maps-data

### Key Endpoints Used

| Endpoint | Purpose | Example |
|---|---|---|
| `searchmaps.php` | Search businesses by query + location | `?query=pizza+in+10014&limit=20` |
| `geocoding.php` | Convert address/zip to lat/lng | `?query=10014,+US` |
| `nearby.php` | Search near a lat/lng point | `?query=pizza&lat=40.73&lng=-74.00` |
| `place.php` | Get full details for one business | `?place_id=ChIJ...` |

### Rate Limits

The free tier on RapidAPI has request limits (check your plan). The client is hard-coded to 2 requests/second with automatic retries on 429s. Adjust `requestsPerSecond` if your plan allows more.

### Response Fields

Each result includes:
- `place_id` — unique Google Maps identifier
- `name` — business name
- `address` — full street address
- `phone` — phone number (if listed)
- `website` — website URL (if listed)
- `rating` — star rating (1-5)
- `reviews_count` — number of Google reviews
- `lat` / `lng` — coordinates
- `types` / `category` — business categories (e.g., "pizza_restaurant")

## Tips

- **"query in zipcode"** format works best for US searches. No coordinates needed.
- **20 results per search** is the max. To get more coverage, search multiple overlapping zip codes.
- **Dedup by `place_id`** — the same business often shows up in adjacent zip code searches.
- **Cuisine/category filtering**: The `types` field tells you what kind of business it is. Use it to filter out irrelevant results (e.g., filter out "bar" when searching for "restaurant").
- **Cost**: Check your RapidAPI plan. The free tier usually gives you enough for testing. Paid plans are cheap for bulk scraping.

---

## What to do next

**Run [`/icp-prompt-builder`](../icp-prompt-builder/SKILL.md)** on a 50-business sample (required step above). Then [`/blitz-list-builder`](../blitz-list-builder/SKILL.md) with the filtered domains to find owner contacts — Google Maps returns businesses, not people.

After owner discovery: `/email-waterfall` to fill missing emails, then [`/list-quality-scorecard`](../list-quality-scorecard/SKILL.md) to grade.

**Or wait:** if your scrape returned <200 businesses, your query + location is too narrow. Widen before proceeding.

## Related skills

- [`/icp-prompt-builder`](../icp-prompt-builder/SKILL.md) — required qualification pass
- [`/blitz-list-builder`](../blitz-list-builder/SKILL.md) — find owner contacts at each business
- `/email-waterfall` — fill missing emails
- [`/list-quality-scorecard`](../list-quality-scorecard/SKILL.md) — grade the final list
