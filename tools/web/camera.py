from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright
import asyncio

from db.models import Lecture


YOUTUBE_COOKIE_BTN_SELECTOR = '[aria-label="Accept the use of cookies and other data for the purposes described"]'


def save_photo(url: str, lecture: Lecture) -> str:
    return asyncio.run(save_photo_async_wrapper(url, lecture))


async def save_photo_async_wrapper(url: str, lecture: Lecture) -> str:
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

        if lecture.source == lecture.Source.YOUTUBE:
            element = await page.query_selector(YOUTUBE_COOKIE_BTN_SELECTOR)
            await element.click()
            await asyncio.sleep(2)

        await asyncio.sleep(1)
        await page.screenshot(path=lecture.preview_filename())
        await browser.close()
