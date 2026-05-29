# Scraper Mini-Project

This is a modular scraper for electoral rolls. It handles complex form submissions, session persistence, and authorization redirects.

## Features
- **Session Management:** Uses `requests.Session` to maintain cookies and CSRF tokens.
- **Auto-Authorization:** Automatically detects and submits inner authorization forms required by some government portals.
- **IP Redirect Handling:** Handles cases where PDF files are served from secondary IP addresses or different domains.
- **Configurable:** All URLs, output paths, and target IDs are stored in `config.json`.

## ECI Scraper (Playwright)
For the modern ECI Voters Service Portal (voters.eci.gov.in), use the Playwright-based scraper which handles dynamic content and allows for manual CAPTCHA solving.

### Setup
1. Install Playwright:
   ```bash
   pip install playwright
   playwright install chromium
   ```

### Usage
Run the ECI scraper:
```bash
python eci_scraper.py
```
- The script will automate selecting Maharashtra -> Yavatmal -> 78-Yavatmal.
- It will pause for you to solve the CAPTCHA in the browser.
- Once you click "Search", it will automatically download all PDF parts to `benchmarks/data/raw/eci_yavatmal_78/`.

## Features
- **Human-in-the-Loop:** Pauses for manual CAPTCHA solving.
- **Batch Download:** Iterates through all pages of the results table.
- **Auto-Organization:** Saves files with descriptive names (Part No + Filename).

## Configuration Schema (for main.py)
- `base_url`: The entry point for the voter list search.
- `output_dir`: Where to save the downloaded PDFs.
- `districts`: A map of District IDs to lists of Local Body Name IDs.

## Future Extensibility
To add a new state, create a new config file (e.g., `config_up.json`) and pass it to the `VoterScraper` constructor.
