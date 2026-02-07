import asyncio
import os
from dotenv import load_dotenv

# Load env variables BEFORE importing tools
load_dotenv()

from tools import safe_tavily_search

async def test_tavily_naukri():
    # 1. Search for a Naukri job URL first (since I don't have one handy)
    print("🔍 Searching for a recent Naukri job...")
    search_response = safe_tavily_search(
        "site:naukri.com software engineer bangalore", 
        search_depth="basic", 
        max_results=1
    )
    
    if not search_response.get('results'):
        print("❌ Could not find a Naukri URL to test.")
        return

    test_url = search_response['results'][0]['url']
    print(f"🎯 Testing URL: {test_url}")

    # 2. Simulate scrape_with_tavily logic
    print("--------------------------------------------------")
    print("🚀 Simulating scrape_with_tavily...")
    
    try:
        response = safe_tavily_search(
            query=test_url, 
            search_depth="advanced", 
            include_raw_content=True,
            max_results=1
        )
        
        results = response.get('results', [])
        if not results:
            print("⚠️ Tavily found no results for this URL.")
            return
            
        best_result = results[0]
        raw_content = best_result.get('raw_content')
        if raw_content:
            print("✅ Got RAW CONTENT (Full Page Text)")
            content = raw_content
        else:
            print("⚠️ Only got SNIPPET (Search Result Summary)")
            content = best_result.get('content')
        
        print(f"📦 Content Length: {len(content) if content else 0}")
        if content:
            print(f"📄 Raw Content Preview (first 500 chars):\n{content[:500]}")
            
            # Check if it looks like a captcha or block
            lower_content = content.lower()
            if "access denied" in lower_content or "security check" in lower_content:
                print("⚠️ DETECTED BLOCKING/CAPTCHA TEXT!")
            else:
                print("✅ Content looks potentially valid.")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_tavily_naukri())
