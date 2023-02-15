from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from config.logger import log
import asyncio


PLAY_BTN_CLASS = '.largePlayBtn'

PAGE_LOAD_TIMEOUT = 40000
WAIT_TIME = 4


def get_m3u8(url: str) -> str:
    return asyncio.run(get_m3u8_async_wrapper(url))


async def get_m3u8_async_wrapper(url: str) -> str:
    m3u8 = None
    requests = []

    async with async_playwright() as playwright:
        firefox = playwright.firefox
        browser = await firefox.launch()
        page = await browser.new_page()
        page.on('request', lambda request: requests.append(request.url))

        try:
            await page.goto(url, timeout=PAGE_LOAD_TIMEOUT)
            await asyncio.sleep(WAIT_TIME)
        except PlaywrightTimeoutError:
            # Sometime the browser waits for something unimportant
            log().warning('playwright reached a timeout')

        iframe = await page.query_selector('iframe')
        content = await iframe.content_frame()
        element = await content.query_selector(PLAY_BTN_CLASS)

        await element.click()
        await asyncio.sleep(WAIT_TIME)

        for url in requests:
            if 'index.m3u8' in url and m3u8 is None:
                m3u8 = url
        await browser.close()

    return m3u8
