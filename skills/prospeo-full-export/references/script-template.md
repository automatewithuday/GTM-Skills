# Prospeo Full Export — script template

## Script Template

When Claude generates the export script, it follows this pattern:

```typescript
import { writeFileSync } from 'fs';

// --- Config ---
const API_KEY = process.env.PROSPEO_API_KEY;
if (!API_KEY) {
  console.error('Set PROSPEO_API_KEY environment variable first.');
  process.exit(1);
}

const RATE_LIMIT_MS = 500; // 2 requests/sec
const MAX_RETRIES = 5;

// --- Types ---
interface ProspeoFilters {
  person_job_title?: { include?: string[]; exclude?: string[]; match_only_exact_job_titles?: boolean };
  person_location_search?: { include?: string[]; exclude?: string[] };
  company_headcount_custom?: { min?: number; max?: number };
  company_industry?: { include?: string[]; exclude?: string[] };
  company_technology?: { include?: string[]; exclude?: string[] };
  company_revenue_custom?: { min?: number; max?: number };
  company_founding_year?: { min?: number; max?: number };
  company_name?: { include?: string[]; exclude?: string[] };
  company_domain?: { include?: string[]; exclude?: string[] };
  person_contact_details?: { email?: string[]; mobile?: string[]; operator?: string };
}

// --- Rate-limited fetch ---
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));

async function searchPage(filters: ProspeoFilters, page: number, retries = 0): Promise<any> {
  await sleep(RATE_LIMIT_MS);

  const res = await fetch('https://api.prospeo.io/search-person', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-KEY': API_KEY! },
    body: JSON.stringify({ page, filters }),
  });

  if (res.status === 429 && retries < MAX_RETRIES) {
    const backoff = Math.min(2000 * Math.pow(2, retries), 60000);
    console.log(`  Rate limited, waiting ${backoff / 1000}s...`);
    await sleep(backoff);
    return searchPage(filters, page, retries + 1);
  }

  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

// --- Deduplication ---
const seenLinkedIn = new Set<string>();
const seenEmail = new Set<string>();

function isDuplicate(person: any): boolean {
  const li = person.linkedin_url;
  const em = person.email;
  if (li && seenLinkedIn.has(li)) return true;
  if (em && seenEmail.has(em)) return true;
  if (li) seenLinkedIn.add(li);
  if (em) seenEmail.add(em);
  return false;
}

// --- CSV helpers ---
function escapeCSV(val: any): string {
  if (val == null) return '';
  const s = String(val);
  return s.includes(',') || s.includes('"') || s.includes('\n')
    ? `"${s.replace(/"/g, '""')}"` : s;
}

function resultToRow(r: any): string[] {
  const p = r.person || {};
  const c = r.company || {};
  return [
    p.first_name, p.last_name, p.full_name, p.current_job_title,
    p.email, p.email_status, p.phone, p.linkedin_url,
    p.location?.city, p.location?.state, p.location?.country,
    c.name, c.domain, c.linkedin_url, c.industry,
    c.headcount, c.headcount_range,
    (c.technologies || []).join('; '),
    c.location?.city, c.location?.state, c.location?.country,
  ];
}

const CSV_HEADERS = [
  'first_name', 'last_name', 'full_name', 'job_title',
  'email', 'email_status', 'phone', 'linkedin_url',
  'person_city', 'person_state', 'person_country',
  'company_name', 'company_domain', 'company_linkedin', 'company_industry',
  'company_headcount', 'company_headcount_range',
  'company_technologies',
  'company_city', 'company_state', 'company_country',
];

// --- Main export ---
async function exportSearch(filters: ProspeoFilters, outputFile: string, maxResults?: number) {
  console.log('Running initial search to check result count...');
  const first = await searchPage(filters, 1);

  if (first.error) {
    console.error('API error:', first.message);
    process.exit(1);
  }

  const totalCount = first.pagination?.total_count || 0;
  const totalPages = first.pagination?.total_page || 0;
  console.log(`Found ${totalCount.toLocaleString()} total results (${totalPages} pages)`);

  // Check if we need state-by-state splitting
  const needsSplit = totalCount > 20000
    && filters.person_location_search?.include?.some(l => l === 'United States #US');

  if (needsSplit) {
    console.log('Search exceeds 20K — switching to state-by-state mode...');
    await exportByState(filters, outputFile, maxResults);
    return;
  }

  // Simple pagination
  const rows: string[][] = [];
  const pagesToFetch = maxResults ? Math.min(Math.ceil(maxResults / 25), totalPages) : totalPages;
  const creditsEstimate = pagesToFetch;
  console.log(`Will fetch ${pagesToFetch} pages (~${creditsEstimate} credits)`);

  // Process page 1 results we already have
  for (const r of first.results || []) {
    if (!isDuplicate(r.person)) rows.push(resultToRow(r));
  }
  console.log(`  Page 1/${pagesToFetch} — ${rows.length} contacts`);

  for (let page = 2; page <= pagesToFetch; page++) {
    if (maxResults && rows.length >= maxResults) break;
    const data = await searchPage(filters, page);
    for (const r of data.results || []) {
      if (!isDuplicate(r.person)) rows.push(resultToRow(r));
    }
    if (page % 50 === 0 || page === pagesToFetch) {
      console.log(`  Page ${page}/${pagesToFetch} — ${rows.length} contacts so far`);
    }
  }

  writeCSV(outputFile, rows);
}

// --- State-by-state export ---
const US_STATES = [
  'California', 'Texas', 'Florida', 'New York', 'Illinois', 'Pennsylvania',
  'Ohio', 'Georgia', 'North Carolina', 'Michigan', 'New Jersey', 'Virginia',
  'Washington', 'Arizona', 'Massachusetts', 'Tennessee', 'Indiana', 'Missouri',
  'Maryland', 'Wisconsin', 'Colorado', 'Minnesota', 'South Carolina', 'Alabama',
  'Louisiana', 'Kentucky', 'Oregon', 'Oklahoma', 'Connecticut', 'Utah', 'Iowa',
  'Nevada', 'Arkansas', 'Mississippi', 'Kansas', 'New Mexico', 'Nebraska',
  'Idaho', 'West Virginia', 'Hawaii', 'New Hampshire', 'Maine', 'Montana',
  'Rhode Island', 'Delaware', 'South Dakota', 'North Dakota', 'Alaska',
  'Vermont', 'Wyoming',
];

async function exportByState(filters: ProspeoFilters, outputFile: string, maxResults?: number) {
  const rows: string[][] = [];

  for (let i = 0; i < US_STATES.length; i++) {
    if (maxResults && rows.length >= maxResults) break;

    const state = US_STATES[i];
    const stateFilters = JSON.parse(JSON.stringify(filters));
    stateFilters.person_location_search.include =
      stateFilters.person_location_search.include.map((loc: string) =>
        loc === 'United States #US' ? `${state}, United States #US` : loc
      );

    const first = await searchPage(stateFilters, 1);
    const stateTotal = first.pagination?.total_count || 0;
    const statePages = first.pagination?.total_page || 0;

    if (stateTotal === 0) {
      console.log(`  [${i + 1}/50] ${state}: 0 results, skipping`);
      continue;
    }

    // Process page 1
    for (const r of first.results || []) {
      if (!isDuplicate(r.person)) rows.push(resultToRow(r));
    }

    // Paginate remaining
    for (let page = 2; page <= statePages; page++) {
      if (maxResults && rows.length >= maxResults) break;
      const data = await searchPage(stateFilters, page);
      for (const r of data.results || []) {
        if (!isDuplicate(r.person)) rows.push(resultToRow(r));
      }
    }

    console.log(`  [${i + 1}/50] ${state}: ${stateTotal.toLocaleString()} results — ${rows.length.toLocaleString()} total contacts`);
  }

  writeCSV(outputFile, rows);
}

// --- Write CSV ---
function writeCSV(outputFile: string, rows: string[][]) {
  const lines = [CSV_HEADERS.join(',')];
  for (const row of rows) {
    lines.push(row.map(escapeCSV).join(','));
  }
  writeFileSync(outputFile, lines.join('\n'), 'utf-8');
  console.log(`\nExport complete!`);
  console.log(`  File: ${outputFile}`);
  console.log(`  Contacts: ${rows.length.toLocaleString()}`);
  console.log(`  Credits used: ~${seenLinkedIn.size + seenEmail.size > 0 ? 'see above' : rows.length / 25}`);
}

// --- Entry point ---
// Claude will fill in the filters based on your search description
const filters: ProspeoFilters = {
  // FILTERS_GO_HERE
};

const outputFile = 'prospeo-export.csv';
exportSearch(filters, outputFile);
```

---
