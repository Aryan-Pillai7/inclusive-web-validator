import sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import asyncio 
from app.services.report_service import run_full_scan 

async def main(): 
    res = await run_full_scan("https://leetcode.com", max_pages=3, max_depth=1)
    print("Report path: ", res["report_path"])
    print("Summary: ", res["report"]["summary"])
    
asyncio.run(main())