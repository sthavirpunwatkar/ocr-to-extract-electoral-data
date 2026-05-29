import os
import asyncio
import time
from playwright.async_api import async_playwright

async def run_scraper():
    """
    ECI Voters Service Portal Scraper
    
    This script automates the selection of State, District, and AC on the ECI portal,
    pauses for manual CAPTCHA solving, and then batch downloads all electoral roll parts.
    """
    
    # Configuration
    STATE = "Maharashtra"
    DISTRICT = "Yavatmal"
    AC = "78 - Yavatmal"
    OUTPUT_DIR = "benchmarks/data/raw/eci_yavatmal_78"
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with async_playwright() as p:
        print("Launching browser...")
        # Headless=False is REQUIRED for the user to solve the CAPTCHA
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("Navigating to ECI Voters Service Portal...")
        try:
            await page.goto("https://voters.eci.gov.in/download-electoral-roll", timeout=60000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            await browser.close()
            return

        print("\n" + "!"*50)
        print("MANDATORY ACTION REQUIRED:")
        print("The ECI portal now requires LOGIN to download files.")
        print("1. If you see a Login page, please LOG IN or SIGN UP now.")
        print("2. Once logged in, navigate back to 'Download Electoral Roll' if needed.")
        print("3. Note: The download page might open in a NEW TAB after login.")
        print("The script will automatically find the correct tab and detect when you are ready.")
        print("!"*50 + "\n")

        # Function to find the correct page across all tabs
        async def find_download_page():
            for _ in range(300): # 5 minute wait
                for p in context.pages:
                    try:
                        # Look for a unique element on the download page
                        if await p.locator("select[name='state']").count() > 0:
                            return p
                    except:
                        continue
                await asyncio.sleep(1)
            return None

        # Switch to the active download page
        page = await find_download_page()
        if not page:
            print("Timed out waiting for the Download page. Please ensure you are logged in and on the correct page.")
            await browser.close()
            return
        
        await page.bring_to_front()

        # 1. Select State
        print(f"Selecting State: {STATE}...")
        try:
            await page.select_option("select[name='state']", label=STATE)
        except Exception:
            await page.get_by_label("Select State").select_option(label=STATE)

        # 2. Select District
        print(f"Selecting District: {DISTRICT}...")
        await asyncio.sleep(1) # Wait for dropdown to populate
        try:
            await page.wait_for_selector("select[name='district']", timeout=10000)
            await page.select_option("select[name='district']", label=DISTRICT)
        except Exception:
            await page.get_by_label("Select District").select_option(label=DISTRICT)

        # 3. Select Assembly Constituency
        print(f"Selecting Assembly Constituency: {AC}...")
        await asyncio.sleep(1) # Wait for dropdown to populate
        try:
            await page.wait_for_selector("select[name='ac']", timeout=10000)
            await page.select_option("select[name='ac']", label=AC)
        except Exception:
            await page.get_by_label("Select Assembly Constituency").select_option(label=AC)

        # 4. Select Language
        print("Selecting Language...")
        await asyncio.sleep(1)
        try:
            # Try to select the first available language option
            await page.locator("select[name='lang']").select_option(index=1)
        except Exception:
            print("Language selection skipped or already set.")

        print("\n" + "="*50)
        print("ACTION REQUIRED:")
        print("1. In the browser window, solve the CAPTCHA.")
        print("2. Click the 'Search' button.")
        print("3. Wait for the list of parts to appear.")
        print("The script will automatically detect the results and start downloading.")
        print("="*50 + "\n")

        # Wait for the results table to appear
        # The table usually has class 'table' or we look for the download icon
        print("Waiting for results table...")
        try:
            # Wait for any table row to appear in the results area
            await page.wait_for_selector("table tbody tr", timeout=600000) # 10 minute timeout for user
        except Exception:
            print("Timed out waiting for search results. Did you click 'Search'?")
            await browser.close()
            return

        print("Results detected. Starting batch download...")

        page_num = 1
        total_downloaded = 0

        while True:
            print(f"Scanning page {page_num}...")
            
            # Find all download links. They typically contain a download icon.
            # We use a locator that finds the <a> tag that contains the icon.
            download_locators = page.locator("a:has(i.fa-download), a:has(i.bi-download)")
            count = await download_locators.count()
            
            if count == 0:
                print("No download links found on this page.")
                break

            print(f"Found {count} parts on this page.")

            for i in range(count):
                link = download_locators.nth(i)
                
                # Get some info about the row if possible (e.g. Part Number)
                # Usually part number is in the first or second column
                try:
                    row = page.locator("table tbody tr").nth(i)
                    part_info = await row.locator("td").first.inner_text()
                    part_info = part_info.strip().replace("/", "_")
                except:
                    part_info = f"part_{total_downloaded + 1}"

                print(f"  [{i+1}/{count}] Downloading {part_info}...")
                
                try:
                    async with page.expect_download(timeout=60000) as download_info:
                        await link.click()
                    
                    download = await download_info.value
                    suggested_name = download.suggested_filename
                    
                    # Prefix with part info if not already there
                    filename = f"{part_info}_{suggested_name}" if part_info not in suggested_name else suggested_name
                    
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    await download.save_as(filepath)
                    total_downloaded += 1
                    print(f"    Saved to {filepath}")
                    
                    # Small delay to be polite
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"    Failed to download {part_info}: {e}")

            # Check for "Next" button in pagination
            next_button = page.locator("li.page-item.next:not(.disabled) a, a.next-page")
            if await next_button.count() > 0 and await next_button.is_visible():
                print("Navigating to next page...")
                await next_button.click()
                await asyncio.sleep(2) # Wait for table refresh
                page_num += 1
            else:
                print("No more pages.")
                break

        print(f"\nSuccessfully downloaded {total_downloaded} files to {OUTPUT_DIR}")
        print("Closing browser...")
        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(run_scraper())
    except KeyboardInterrupt:
        print("\nScraper stopped by user.")
