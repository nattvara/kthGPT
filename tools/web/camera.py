from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright
import asyncio


def save_photo(url: str, filepath: str) -> str:
    return asyncio.run(save_photo_async_wrapper(url, filepath))


async def save_photo_async_wrapper(url: str, filepath: str) -> str:
    async with async_playwright() as playwright:
        firefox = playwright.firefox
        browser = await firefox.launch()
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=10000)
            await asyncio.sleep(2)
        except PlaywrightTimeoutError:
            # Sometime the browser waits for something unimportant
            pass
        await asyncio.sleep(1)
        await page.screenshot(path=filepath)
        await browser.close()
