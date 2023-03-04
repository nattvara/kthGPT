from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from typing import List, Optional
from urllib.parse import urlparse
from config.logger import log
from datetime import datetime
from bs4 import BeautifulSoup
from urllib import request
import asyncio
import re


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


def scrape_title_from_page(url: str) -> str:
    html = request.urlopen(url).read().decode('utf8')
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('title')
    return title.string


def scrape_posted_date_from_kthplay(url: str) -> Optional[datetime]:
    html = request.urlopen(url).read().decode('utf8')
    soup = BeautifulSoup(html, 'html.parser')

    regex = re.compile(r'date:((\s|\d)*),')

    # Looking for a <script> tag containing a date on the form:
    #   date: 1613124505,
    matched_strings = soup.find_all(text=regex)
    if len(matched_strings) == 0:
        return None

    script_tag = matched_strings[0]
    ts = re.search(regex, script_tag).group(1).strip()

    if ts is not None:
        return datetime.fromtimestamp(int(ts))


def scrape_course_groups() -> List[str]:
    return asyncio.run(scrape_course_groups_async_wrapper())


async def scrape_course_groups_async_wrapper() -> str:
    url = 'https://www.kth.se/student/kurser/org'
    out = []

    async with async_playwright() as playwright:
        firefox = playwright.firefox
        browser = await firefox.launch()
        page = await browser.new_page()

        try:
            await page.goto(url, timeout=PAGE_LOAD_TIMEOUT)
            await asyncio.sleep(WAIT_TIME)
        except PlaywrightTimeoutError:
            # Sometime the browser waits for something unimportant
            log().warning('playwright reached a timeout')

        a_els = await page.query_selector_all('li > a')
        found = []
        for el in a_els:
            href = await el.get_attribute('href')
            if '/student/kurser' in href:
                found.append(f'https://kth.se{href}')

    for url in found:
        # Parse the url and make sure it's valid, also stripping
        # the query params, make sure to get the page in both
        # english and swedish
        parsed = urlparse(url)
        if parsed is not None:
            out.append(f'{parsed.scheme}://{parsed.netloc}{parsed.path}?l=sv')
            out.append(f'{parsed.scheme}://{parsed.netloc}{parsed.path}?l=en')

    return out


def scrape_courses_from_group(group_url: str) -> List[List[int]]:
    return asyncio.run(scrape_courses_from_group_async_wrapper(group_url))


async def scrape_courses_from_group_async_wrapper(group_url: str) -> List[List[int]]:
    out = []

    async with async_playwright() as playwright:
        firefox = playwright.firefox
        browser = await firefox.launch()
        page = await browser.new_page()

        try:
            await page.goto(group_url, timeout=PAGE_LOAD_TIMEOUT)
            await asyncio.sleep(WAIT_TIME)
        except PlaywrightTimeoutError:
            # Sometime the browser waits for something unimportant
            log().warning('playwright reached a timeout')
        except Exception:
            return []

        tr_els = await page.query_selector_all('tbody > tr')
        for tr in tr_els:
            data = []
            td_els = await tr.query_selector_all('td')
            for td in td_els:
                data.append(await td.text_content())

            out.append(data)

    return out
