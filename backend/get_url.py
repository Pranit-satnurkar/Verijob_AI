from dotenv import load_dotenv
load_dotenv()
import os
from tools import safe_tavily_search
import json

def get_url():
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        print("❌ NO API KEY FOUND")
        return

    print(f"🔑 Key Length: {len(key)}")
    print("🔍 Searching for Naukri URL...")
    
    # Try a very specific query likely to return a job listing
    res = safe_tavily_search(
        'site:naukri.com inurl:job-listings "software engineer" bangalore', 
        max_results=3
    )
    
    if res and res.get('results'):
        print("✅ Found Results:")
        for r in res['results']:
            print(f"URL: {r['url']}")
            # Accept any Naukri URL that looks like a job or listing
            if "naukri.com" in r['url']:
                print(f"🎯 FOUND URL: {r['url']}")
                with open("found_url.txt", "w") as f:
                    f.write(r['url'])
                return # Stop after first valid one
    else:
        print("❌ No results found from Tavily.")
        # Try fallback query
        res = safe_tavily_search('naukri job bangalore python', max_results=3)
        if res and res.get('results'):
             print("✅ Found Results (Fallback):")
             for r in res['results']:
                 print(f"URL: {r['url']}")

if __name__ == "__main__":
    get_url()
