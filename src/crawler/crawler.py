from playwright.async_api import async_playwright
import beeprint
import asyncio
import time


PLAY_BTN_CLASS = '.largePlayBtn'



def get_m3u8(url: str) -> str:
    return asyncio.run(get_m3u8_async_wrapper(url))

async def get_m3u8_async_wrapper(url: str) -> str:
    m3u8 = None
    requests = []

    async with async_playwright() as playwright:
        firefox = playwright.firefox
        browser = await firefox.launch()
        page = await browser.new_page()
        page.on("request", lambda request: requests.append(request.url))

        await page.goto(url)
        await asyncio.sleep(1)

        iframe = await page.query_selector('iframe')
        content = await iframe.content_frame()
        element = await content.query_selector(PLAY_BTN_CLASS)

        await element.click()
        await asyncio.sleep(1)

        for url in requests:
            if 'index.m3u8' in url and m3u8 is None:
                m3u8 = url
        await browser.close()

    return m3u8
