# Google Maps List Builder — deploying as a web app

## Deploying as a Web App (Optional)

If you want a browser UI instead of (or in addition to) the CLI, add Express:

```bash
npm install express
npm install -D @types/express
```

Create `src/server.ts`:

```typescript
import express from 'express';
import { GoogleMapsClient } from './client.js';
import { exportCSV } from './csv.js';
import { tmpdir } from 'os';
import { join } from 'path';
import { readFile, unlink } from 'fs/promises';

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const client = new GoogleMapsClient({
  apiKey: process.env.RAPIDAPI_KEY!,
  requestsPerSecond: 2,
});

// Simple HTML form
app.get('/', (_req, res) => {
  res.send(`<!DOCTYPE html>
<html><head><title>Google Maps Scraper</title></head>
<body style="font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 20px">
  <h1>Google Maps Scraper</h1>
  <form method="POST" action="/scrape">
    <label>Search query:<br>
      <input name="query" placeholder="pizza restaurant" style="width:100%;padding:8px;margin:4px 0 12px" required>
    </label>
    <label>Locations (comma-separated zips or cities):<br>
      <input name="locations" placeholder="10014, 10013, 10012" style="width:100%;padding:8px;margin:4px 0 12px" required>
    </label>
    <button type="submit" style="padding:10px 24px;cursor:pointer">Scrape</button>
  </form>
</body></html>`);
});

app.post('/scrape', async (req, res) => {
  const { query, locations: locStr } = req.body;
  const locations = locStr.split(',').map((s: string) => s.trim()).filter(Boolean);

  const allPlaces: any[] = [];
  for (const loc of locations) {
    try {
      const results = await client.search({ query: `${query} in ${loc}`, limit: 20 });
      allPlaces.push(...results);
    } catch {}
  }

  // Dedup
  const seen = new Set<string>();
  const unique = allPlaces.filter(p => { if (seen.has(p.place_id)) return false; seen.add(p.place_id); return true; });

  // Export CSV and send as download
  const tmpPath = join(tmpdir(), `scrape-${Date.now()}.csv`);
  await exportCSV(unique, tmpPath);
  const csv = await readFile(tmpPath, 'utf-8');
  await unlink(tmpPath);

  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', `attachment; filename="maps-scrape-${Date.now()}.csv"`);
  res.send(csv);
});

const port = parseInt(process.env.PORT || '3000', 10);
app.listen(port, () => console.log(`Scraper running at http://localhost:${port}`));
```

Add a script to `package.json`:
```json
{
  "scripts": {
    "scrape": "tsx src/index.ts",
    "serve": "tsx src/server.ts"
  }
}
```

Run locally: `npm run serve` then open http://localhost:3000

### Deploying to Railway

1. Push your project to a GitHub repo
2. Go to https://railway.com, create a new project, connect the repo
3. Set the environment variable `RAPIDAPI_KEY` in Railway's dashboard
4. Set the start command to `npx tsx src/server.ts`
5. Railway auto-detects the port from `process.env.PORT` and gives you a public URL

You can add password protection by checking a `PASSWORD` env var in the POST handler, or use Railway's built-in auth features.

### Deploying to Other Platforms

This is a standard Node.js app. It runs anywhere:
- **Render**: Connect GitHub repo, set env vars, done
- **Fly.io**: `fly launch`, set secrets with `fly secrets set RAPIDAPI_KEY=xxx`
- **Vercel**: Deploy as a serverless function (modify server.ts to export handlers)
- **Docker**: `FROM node:20-slim` + `npm install` + `npx tsx src/server.ts`
