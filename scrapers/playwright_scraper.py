"""Optional Playwright scraper for websites without RSS.

Run:
    python -m playwright install chromium
    python scrapers/playwright_scraper.py https://example.com/jobs
"""

import asyncio
import sys

from playwright.async_api import async_playwright


async def scrape_titles(url: str) -> list[str]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='domcontentloaded')
        titles = await page.locator('h1, h2, h3, a').all_inner_texts()
        await browser.close()
    return [t.strip() for t in titles if t.strip()][:50]


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python scrapers/playwright_scraper.py <url>')

    scraped = asyncio.run(scrape_titles(sys.argv[1]))
    print(f'Scraped {len(scraped)} text entries')
    for row in scraped[:20]:
        print('-', row)
