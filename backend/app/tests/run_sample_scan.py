import asyncio 
from services.report_service import run_full_scan 

async def main(): 
    res = await run_full_scan("https.//example.com", max_pages=3, max_depth=1)
    print("Report path: ", res["report_path"])
    print("Summary: ", res["report"]["summary"])
    
asyncio.run(main())