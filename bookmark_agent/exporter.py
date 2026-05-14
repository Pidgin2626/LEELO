"""Scrape X (Twitter) bookmarks with Playwright.

You run this on your own machine. The browser opens, you log in once,
the session is saved to .auth/state.json, then it scrolls your
bookmarks page and dumps every tweet to data/bookmarks.json.

Re-runs reuse the saved session; delete .auth/state.json to log in fresh.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    TimeoutError as PWTimeout,
    async_playwright,
)

ROOT = Path(__file__).parent
AUTH_DIR = ROOT / ".auth"
AUTH_STATE = AUTH_DIR / "state.json"
DATA_DIR = ROOT / "data"
OUT_FILE = DATA_DIR / "bookmarks.json"

BOOKMARKS_URL = "https://x.com/i/bookmarks"
LOGIN_HINT_URL = "https://x.com/login"


async def ensure_logged_in(context: BrowserContext, page: Page) -> None:
    await page.goto(BOOKMARKS_URL, wait_until="domcontentloaded")
    await page.wait_for_timeout(2500)

    if "/login" in page.url or "/i/flow/login" in page.url:
        print("Not logged in. The browser is open — log in to X in the window.")
        print("After you reach your bookmarks page, come back and press Enter here.")
        input("Press Enter once you see your bookmarks loaded... ")
        await page.goto(BOOKMARKS_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)
        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        await context.storage_state(path=str(AUTH_STATE))
        print(f"Saved session to {AUTH_STATE}")


async def scrape_bookmarks(page: Page, max_scrolls: int = 400) -> list[dict]:
    seen_ids: set[str] = set()
    bookmarks: list[dict] = []
    stale_rounds = 0

    print("Scrolling bookmarks. This will take a while if you have a lot.")
    for i in range(max_scrolls):
        articles = await page.query_selector_all("article[data-testid='tweet']")
        new_this_round = 0

        for art in articles:
            data = await extract_tweet(art)
            if not data:
                continue
            if data["id"] in seen_ids:
                continue
            seen_ids.add(data["id"])
            bookmarks.append(data)
            new_this_round += 1

        if new_this_round == 0:
            stale_rounds += 1
        else:
            stale_rounds = 0

        if stale_rounds >= 5:
            print(f"No new bookmarks after {stale_rounds} scrolls. Assuming done.")
            break

        print(f"  scroll {i + 1}: total bookmarks captured = {len(bookmarks)}")

        await page.mouse.wheel(0, 4000)
        await page.wait_for_timeout(1200)

    return bookmarks


async def extract_tweet(article) -> dict | None:
    try:
        link_el = await article.query_selector("a[href*='/status/']")
        if not link_el:
            return None
        href = await link_el.get_attribute("href") or ""
        m = re.search(r"/([^/]+)/status/(\d+)", href)
        if not m:
            return None
        author, tweet_id = m.group(1), m.group(2)

        text_el = await article.query_selector("div[data-testid='tweetText']")
        text = (await text_el.inner_text()) if text_el else ""

        url_elements = await article.query_selector_all(
            "div[data-testid='tweetText'] a[href^='http'], "
            "div[data-testid='tweetText'] a[href*='t.co/']"
        )
        urls: list[str] = []
        for u in url_elements:
            href = await u.get_attribute("href")
            if href and href not in urls:
                urls.append(href)

        media_urls: list[str] = []
        for img in await article.query_selector_all("img[src*='twimg.com/media']"):
            src = await img.get_attribute("src")
            if src:
                media_urls.append(src)

        video_present = bool(await article.query_selector("video"))

        return {
            "id": tweet_id,
            "author": author,
            "url": f"https://x.com/{author}/status/{tweet_id}",
            "text": text,
            "linked_urls": urls,
            "media_urls": media_urls,
            "has_video": video_present,
        }
    except Exception as e:
        print(f"  warn: failed to extract a tweet: {e}", file=sys.stderr)
        return None


async def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    AUTH_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(headless=False)
        context_kwargs: dict = {
            "user_agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "viewport": {"width": 1400, "height": 900},
        }
        if AUTH_STATE.exists():
            context_kwargs["storage_state"] = str(AUTH_STATE)

        context = await browser.new_context(**context_kwargs)
        page = await context.new_page()

        await ensure_logged_in(context, page)

        bookmarks = await scrape_bookmarks(page)

        OUT_FILE.write_text(json.dumps(bookmarks, indent=2, ensure_ascii=False))
        print(f"\nWrote {len(bookmarks)} bookmarks to {OUT_FILE}")

        await context.storage_state(path=str(AUTH_STATE))
        await browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
