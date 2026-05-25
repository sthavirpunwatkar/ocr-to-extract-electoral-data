# Data Handoff Workflow

This document explains how to move data from the **Data Factory** (OCR Project) to the **Storefront** (OCR-v2 Mobile Backend).

## 1. Local Export (Data Factory)
In the main `ocr` project, run the export script (to be implemented) to generate a SQLite file:
```bash
# Example command
python scripts/export_to_sqlite.py --region maharashtra
```
This will create `maharashtra.sqlite`.

## 2. Prepare Cloudflare D1 (OCR-v2)
Navigate to your `ocr-v2` directory.
If you haven't created the database yet:
```bash
npx wrangler d1 create voter-db
```

## 3. Upload Data
To push your local data into the cloud:
```bash
# Upload schema first
npx wrangler d1 execute voter-db --file=./schema.sql

# Import data
npx wrangler d1 execute voter-db --command=".import maharashtra.sqlite voters"
```
*Note: Depending on the size, you may need to use a CSV export/import or multiple `execute` commands for bulk inserts.*

## 4. Verify
Test the deployment with a query:
```bash
npx wrangler d1 execute voter-db --command="SELECT COUNT(*) FROM voters"
```
