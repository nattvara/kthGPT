from playwright.async_api import async_playwright
import asyncio


def save_photo(url: str, filepath: str) -> str:
    return asyncio.run(save_photo_async_wrapper(url, filepath))


async def save_photo_async_wrapper(url: str, filepath: str) -> str:
    async with async_playwright() as playwright:
        firefox = playwright.firefox
        browser = await firefox.launch()
        page = await browser.new_page()
        await page.goto(url)
        await asyncio.sleep(1)
        await page.screenshot(path=filepath)
        await browser.close()
