# ocr-v2 Architecture

## Overview
The `ocr-v2` project is a globally distributed, high-performance API designed to provide instant voter data search capabilities for mobile applications.

## Technical Stack
- **API Runtime:** Cloudflare Workers (V8 Isolate-based serverless).
- **Web Framework:** Hono (Lightweight, Cloudflare-optimized).
- **Database:** Cloudflare D1 (Serverless SQL based on SQLite).
- **Protocol:** RESTful JSON API.

## Data Flow
1. **Extraction (Local):** The `ocr` Data Factory processes PDFs and outputs a structured SQLite file.
2. **Handoff:** The SQLite schema and data are uploaded to Cloudflare D1 via the `wrangler d1 execute` command.
3. **Consumption:** Mobile apps hit the Cloudflare Worker endpoint.
4. **Execution:** The Worker queries D1 and returns JSON to the mobile client.

## Performance Targets
- **TTFB (Time to First Byte):** < 30ms (Edge execution).
- **Query Time:** < 50ms for indexed searches.
- **Concurrent Users:** Scalable to 100k+ daily users on the Cloudflare Free Tier.
