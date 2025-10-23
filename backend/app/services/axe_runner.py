# axe_runner.py
import os
import json
from typing import Dict, Any
from playwright.async_api import Page

from .config import AXE_JS_PATH

# Load axe source into a string at module import
if not os.path.exists(AXE_JS_PATH):
    raise FileNotFoundError(f"axe.min.js not found at {AXE_JS_PATH}. Run `npm install axe-core` from backend root.")
with open(AXE_JS_PATH, "r", encoding="utf-8") as f:
    AXE_SCRIPT = f.read()


async def run_axe_on_page(page: Page, context: Dict = None) -> Dict[str, Any]:
    """
    Inject axe.min.js then run axe.run() in the page.
    Returns the axe results JSON (dict).
    """
    # Inject axe script
    await page.add_script_tag(content=AXE_SCRIPT)
    # Optionally pass a context or options to axe.run
    # Use evaluate to run axe.run in the page context and get JSON back
    options = {}  # can add rules or options
    context_arg = context or {}
    result = await page.evaluate(
        """async (options, context) => {
            try {
                const res = await window.axe.run(context, options);
                return res;
            } catch (err) {
                return { error: String(err) };
            }
        }""",
        {"options": options, "context": context_arg}
    )
    return result
