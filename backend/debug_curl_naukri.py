import asyncio
import os
from dotenv import load_dotenv
from scraper import scrape_with_curl_cffi
from tools import safe_tavily_search

# Load env variables
load_dotenv()

async def test_curl_naukri():

    test_url = "https://www.naukri.com/job-listings-client-technology-engineering-software-engineering-ernst-young-llp-bengaluru-10-to-15-years-261225914157"
    print(f"🎯 Testing Direct Job URL: {test_url}")

    try:
        from curl_cffi.requests import AsyncSession
        
        async with AsyncSession(impersonate="safari15_5") as s:
            print(f"🕵️‍♂️ Fetching {test_url}...")
            # Random delay
            import time
            import random
            time.sleep(random.uniform(1, 3))
            
            response = await s.get(test_url, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            with open("debug_curl.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("💾 Saved Job HTML to debug_curl.html")
            
            if "Access Denied" in response.text:
                print("⚠️ BLOCK DETECTED: 'Access Denied'")
            elif "Security Check" in response.text:
                 print("⚠️ BLOCK DETECTED: 'Security Check'")
            else:
                 print("✅ Content seems to have loaded (check file for details).")
                 
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_curl_naukri())
