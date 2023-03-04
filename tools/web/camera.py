from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from PIL import Image
import asyncio

from db.models import Lecture


# The two different buttons that has been seen
YOUTUBE_COOKIE_BTN_SELECTOR_1 = '[aria-label="Accept the use of cookies and other data for the purposes described"]'
YOUTUBE_COOKIE_BTN_SELECTOR_2 = '[aria-label="Accept all"]'


def save_photo(url: str, lecture: Lecture, small: bool = False) -> str:
    return asyncio.run(save_photo_async_wrapper(url, lecture, small))


async def save_photo_async_wrapper(url: str, lecture: Lecture, small: bool = False) -> str:
    async with async_playwright() as playwright:
        firefox = playwright.firefox
        browser = await firefox.launch()
        page = await browser.new_page(user_agent='kthgpt')

        try:
            await page.goto(url, timeout=10000)
            await asyncio.sleep(2)
        except PlaywrightTimeoutError:
            # Sometime the browser waits for something unimportant
            pass

        if lecture.source == lecture.Source.YOUTUBE:
            await asyncio.sleep(10)
            for btn in [YOUTUBE_COOKIE_BTN_SELECTOR_1, YOUTUBE_COOKIE_BTN_SELECTOR_2]:
                element = await page.query_selector(btn)
                if element is not None:
                    await element.click()
                    await asyncio.sleep(10)

        if small:
            path = lecture.preview_small_filename()
        else:
            path = lecture.preview_filename()

        await asyncio.sleep(1)
        await page.screenshot(path=path)
        await browser.close()

        if small:
            image = Image.open(path)
            width, height = image.size
            new_width = int(width / 4)
            new_height = int(height / 4)

            resized = image.resize((new_width, new_height))
            resized.save(path)
