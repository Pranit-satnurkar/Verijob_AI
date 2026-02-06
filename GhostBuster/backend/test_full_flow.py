import asyncio
from dotenv import load_dotenv
import os
import sys

# Force UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from tools import extract_metadata_from_text, search_company_health, search_reddit_sentiment
from verifier import verify_job_listing

# Mock TCS Job Description
tcs_jd = """
Tata Consultancy Services (TCS) is hiring a Data Analyst.
Location: Mumbai, India.
Responsibilities:
- Analyze large datasets.
- SQL and Python required.
- Create dashboards in Tableau.
experience: 3-5 years.
"""

async def test_flow():
    print("Starting Full Flow Test...")
    
    # 1. Test Metadata Extraction
    print("\n1. Testing Metadata Extraction...")
    metadata = extract_metadata_from_text(tcs_jd, "http://tcs.com/job")
    print(f"Extraction Result: {metadata}")
    
    # 2. Test Verification Logic (Agent)
    print("\n2. Testing Verification Agent...")
    result = await verify_job_listing("http://tcs.com/job", content=tcs_jd)
    
    print("\n--- FINAL RESULT ---")
    print(f"Company Detected: {result.get('metadata', {}).get('company', 'Unknown')}")
    print(f"Score: {result.get('score')}")
    print(f"Sources Count: {len(result.get('references', []))}")
    for ref in result.get('references', []):
        print(f" - {ref['title']} ({ref['url']})")

if __name__ == "__main__":
    asyncio.run(test_flow())
