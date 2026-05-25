# ocr-v2: Mobile Backend Instructions

You are a specialized agent for the **ocr-v2** project, which serves voter data to Android and iOS mobile applications.

## Core Mandates
- **Tech Stack:** JavaScript/TypeScript, Hono framework, Cloudflare Workers.
- **Data Persistence:** Cloudflare D1 (Serverless SQLite).
- **Architecture:** Lightweight, read-only Edge API. Do NOT suggest Docker or Python/FastAPI unless specifically requested.

## Engineering Standards
- **Performance:** Aim for sub-50ms latency. Keep the Worker script as small as possible.
- **Database:** All data is pre-populated from the `ocr` (Data Factory) project. Focus on efficient `SELECT` queries and proper indexing.
- **Pagination:** Always implement pagination for search results (default 20 items per page).

## Key Workflows
- **Search Endpoint:** Implement a robust `/v1/search` endpoint that handles name and EPIC ID queries.
- **D1 Integration:** Use the `env.DB.prepare(...)` pattern for querying the Cloudflare D1 database.
- **Deployment:** Use `wrangler deploy` to push to the Cloudflare network.

## Context
This project is the "Storefront" for the `ocr` project. The data is generated there and handed off to this project via SQLite file imports into Cloudflare D1.
