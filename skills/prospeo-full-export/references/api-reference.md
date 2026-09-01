# Prospeo Full Export — filter and API reference

## Filter Reference

These are the exact filter names the Prospeo API accepts. When you describe your search, Claude maps your description to these:

| UI Filter | API Filter Key | Format |
|-----------|---------------|--------|
| Job Title | `person_job_title` | `{ include: ["CEO", "CTO"], exclude: ["Intern"] }` |
| Location | `person_location_search` | `{ include: ["California, United States #US"] }` |
| Industry | `company_industry` | `{ include: ["Information Technology"] }` |
| Headcount | `company_headcount_custom` | `{ min: 11, max: 500 }` |
| Technology | `company_technology` | `{ include: ["Salesforce", "HubSpot"] }` |
| Revenue | `company_revenue_custom` | `{ min: 1000000, max: 50000000 }` |
| Founded Year | `company_founding_year` | `{ min: 2010, max: 2025 }` |
| Company Name | `company_name` | `{ include: ["Acme"], exclude: ["Test"] }` |
| Company Domain | `company_domain` | `{ include: ["acme.com"] }` |
| Has Email | `person_contact_details` | `{ email: ["VERIFIED"] }` |
| Has Phone | `person_contact_details` | `{ mobile: ["TRUE"] }` |
| Exact Title Match | `person_job_title` | `{ include: [...], match_only_exact_job_titles: true }` |

### Location Format

Locations must follow this exact format:
- Country: `"United States #US"`, `"United Kingdom #GB"`, `"Canada #CA"`
- State: `"California, United States #US"`, `"Texas, United States #US"`
- City: `"San Francisco, California, United States #US"`

### Headcount Ranges (Common Presets)

| Label | min | max |
|-------|-----|-----|
| 1-10 | 1 | 10 |
| 11-50 | 11 | 50 |
| 51-200 | 51 | 200 |
| 201-500 | 201 | 500 |
| 501-1000 | 501 | 1000 |
| 1001-5000 | 1001 | 5000 |
| 5001-10000 | 5001 | 10000 |
| 10001+ | 10001 | (omit max) |

---

## API Details

**Endpoint:** `POST https://api.prospeo.io/search-person`

**Auth:** `X-KEY` header with your API key

**Rate Limit:** 2 requests per second (the script handles this automatically)

**Pagination:** 25 results per page, max 1000 pages = **25,000 results per search**

**Credits:** 1 credit per request that returns at least 1 result. A 25,000-result search costs ~1,000 credits.

### Request Format

```typescript
const response = await fetch('https://api.prospeo.io/search-person', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-KEY': process.env.PROSPEO_API_KEY!,
  },
  body: JSON.stringify({
    page: 1,  // 1-1000
    filters: {
      person_job_title: { include: ['CEO', 'CTO'] },
      person_location_search: { include: ['United States #US'] },
      company_headcount_custom: { min: 11, max: 500 },
      company_industry: { include: ['Information Technology'] },
      person_contact_details: { email: ['VERIFIED'] },
    },
  }),
});
```

### Response Format

```typescript
{
  error: false,
  results: [
    {
      person: {
        person_id: "abc123",
        first_name: "Jane",
        last_name: "Smith",
        full_name: "Jane Smith",
        current_job_title: "CEO",
        linkedin_url: "https://linkedin.com/in/janesmith",
        email: "jane@acme.com",
        email_status: "VERIFIED",
        phone: "+14155551234",
        location: { city: "San Francisco", state: "California", country: "United States" }
      },
      company: {
        name: "Acme Corp",
        domain: "acme.com",
        linkedin_url: "https://linkedin.com/company/acme",
        industry: "Information Technology",
        headcount: 150,
        headcount_range: "51-200",
        technologies: ["Salesforce", "HubSpot"],
        location: { city: "San Francisco", state: "California", country: "United States" }
      }
    }
  ],
  pagination: {
    current_page: 1,
    total_page: 400,
    total_count: 10000,
    per_page: 25
  }
}
```

---
