# Scraper Mini-Project

This is a modular scraper for electoral rolls. It handles complex form submissions, session persistence, and authorization redirects.

## Features
- **Session Management:** Uses `requests.Session` to maintain cookies and CSRF tokens.
- **Auto-Authorization:** Automatically detects and submits inner authorization forms required by some government portals.
- **IP Redirect Handling:** Handles cases where PDF files are served from secondary IP addresses or different domains.
- **Configurable:** All URLs, output paths, and target IDs are stored in `config.json`.

## Usage
1. Update `config.json` with the target state's URL and District/Local Body IDs.
2. Run the scraper:
   ```bash
   python main.py
   ```

## Configuration Schema
- `base_url`: The entry point for the voter list search.
- `output_dir`: Where to save the downloaded PDFs.
- `districts`: A map of District IDs to lists of Local Body Name IDs.

## Future Extensibility
To add a new state, create a new config file (e.g., `config_up.json`) and pass it to the `VoterScraper` constructor.
