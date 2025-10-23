import asyncio 
import os 
import time 
from urllib.parse import urlparse, urljoin 
from pathlib import Path 
from typing import List, Dict, Any, Set 

from playwright.async_api import async_playwright, TimeoutError as PWTtimeoutError

from .config import MAX_PAGES, MAX_DEPTH, PAGE_TIMEOUT, SCREENSHOT, REPORTS_DIR, SAME_ORIGIN_ONLY   

Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True) 

async def fetch_page_snapshot(page, target_url: str, out_dir: str) -> Dict[str, Any]: 
    """Assumes page is already navigated to the target_url"""
    title = await page.title() 
    html = await page.content()
    screenshot_path = None 
    if SCREENSHOT: 
        screenshot_path = os.path.join(out_dir, f"screenshot_{int(time.time()*1000)}.png")
        await page.screenshot(path=screenshot_path, full_page=True) 
    return {
        "url" : target_url, 
        "title" : title, 
        "html" : html, 
        "screenshot" : screenshot_path 
    }
    
def same_origin(base: str, other: str) -> bool: 
    a = urlparse(base) 
    b = urlparse(other) 
    return (a.scheme, a.hostname, a.port) == (b.scheme, b.hostname, b.port)

async def extract_links(page) -> Set[str]: 
    """Returns hrefs found on page (absolute)"""
    anchors = await page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
    return set([a for a in anchors if a])

async def crawl(url: str, max_pages: int = MAX_PAGES, max_depth: int = MAX_DEPTH) -> List[Dict]: 
    """Crawling starts at url, returns snapshots list"""
    snapshots = [] 
    visited = set() 
    queue = [(url, 0)]
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    semaphore = asyncio.Semaphore(3)
    
    async def worker(target_url: str, depth: int): 
        async with semaphore: 
            if len(snapshots) >= max_pages: 
                return 
            if target_url in visited: 
                return 
            
            visited.add(target_url) 
            page = await context.new_page() 
            
            try: 
                await page.goto(target_url, timeout = PAGE_TIMEOUT)
            except PWTtimeoutError: 
                await page.close() 
                return 
            except Exception: 
                await page.close()
                return 
            
            out_dir = os.path.join(REPORTS_DIR, f"scan{int(time.time())}")
            os.makedirs(out_dir, exist_ok=True) 
            snap = await fetch_page_snapshot(page, target_url, out_dir)
            snapshots.append(snap)
            
            if depth<max_depth and len(snapshots) < max_pages: 
                links = await extract_links(page) 
                for link in links:
                    if not links: 
                        continue
                    if SAME_ORIGIN_ONLY and not same_origin(url, link): 
                        continue
                    if link not in visited: 
                        queue.append((link, depth+1))
                        
            await page.close() 
            
    while queue and len(snapshots) < max_pages:
        tasks = [] 
        while queue and len(tasks) < 3 and len(snapshots) + len(tasks) < max_pages: 
            u, d = queue.pop(0) 
            tasks.append(asyncio.create_task(worker(u,d)))
        if not tasks: 
            break 
        await asyncio.gather(*tasks) 
        
    await context.close() 
    await browser.close() 
    await playwright.stop() 
    return snapshots 

