# config.py
MAX_PAGES = 20             # max pages to crawl per scan
MAX_DEPTH = 2              # how deep (links) to follow
CONCURRENCY = 3            # parallel pages visited at once
PAGE_TIMEOUT = 30_000      # ms
SCREENSHOT = True
SAME_ORIGIN_ONLY = True
REPORTS_DIR = "reports_output"
AXE_JS_PATH = "node_modules/axe-core/axe.min.js"
