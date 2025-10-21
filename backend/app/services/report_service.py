# report_service.py
import os
import json
import time
from typing import Dict, Any, List
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError

from .config import REPORTS_DIR, PAGE_TIMEOUT, SCREENSHOT
from .playwright_crawler import crawl
from .axe_runner import run_axe_on_page

Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)


async def audit_single_page(browser, url: str, out_dir: str) -> Dict[str, Any]:
    page = await browser.new_page()
    try:
        await page.goto(url, timeout=PAGE_TIMEOUT)
    except Exception as e:
        await page.close()
        return {"url": url, "error": str(e)}

    # run axe
    res = await run_axe_on_page(page)
    # optionally capture fresh screenshot (if wanted per-axe run)
    screenshot = None
    if SCREENSHOT:
        screenshot = os.path.join(out_dir, f"screenshot_{int(time.time()*1000)}.png")
        try:
            await page.screenshot(path=screenshot, full_page=True)
        except Exception:
            screenshot = None
    await page.close()
    return {"url": url, "axe": res, "screenshot": screenshot}


async def run_full_scan(start_url: str, max_pages: int = 10, max_depth: int = 1) -> Dict[str, Any]:
    """High-level entrypoint: crawl -> run axe on discovered pages -> save report JSON"""
    ts = int(time.time())
    scan_dir = os.path.join(REPORTS_DIR, f"scan_{ts}")
    os.makedirs(scan_dir, exist_ok=True)
    report = {
        "start_url": start_url,
        "scanned_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pages": []
    }

    # First: get a list of page URLs via the crawler snapshots (uses Playwright itself)
    snapshots = await crawl(start_url, max_pages=max_pages, max_depth=max_depth)
    page_urls = [snap["url"] for snap in snapshots]

    # Now run axe on each page (spawn a new browser context)
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    results = []
    for u in page_urls:
        r = await audit_single_page(browser, u, scan_dir)
        results.append(r)

    await browser.close()
    await playwright.stop()

    report["pages"] = results

    # Compute simple summary
    total_violations = 0
    sev_count = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
    for p in results:
        axe = p.get("axe")
        if not axe or "violations" not in axe:
            continue
        for v in axe["violations"]:
            impact = v.get("impact") or "moderate"
            if impact in sev_count:
                sev_count[impact] += 1
            else:
                sev_count[impact] = sev_count.get(impact, 0) + 1
            total_violations += 1

    report["summary"] = {
        "total_violations": total_violations,
        "by_impact": sev_count,
        "pages_scanned": len(results)
    }

    # Write report JSON
    report_path = os.path.join(scan_dir, "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return {"report_path": report_path, "report": report}
