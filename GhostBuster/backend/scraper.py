from playwright.async_api import async_playwright
from typing import Dict, Any
import asyncio
from tools import extract_metadata_from_text

async def scrape_job_details(url: str) -> Dict[str, Any]:
    """
    Extracts metadata from a job URL using Playwright (Real Browser) + LLM Extraction.
    """
    print(f"🕸️ Scraping URL: {url}...")
    
    async with async_playwright() as p:
        # Launch headless browser
        browser = await p.chromium.launch(headless=True)
        # Random user agent to avoid immediate blocking
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # Go to URL with timeout
            # Go to URL with relaxed wait condition
            await page.goto(url, wait_until="commit", timeout=30000)
            
            # Wait a bit for dynamic content (LinkedIn/Indeed SPAs)
            await page.wait_for_timeout(3000) 
            
            # Extract raw text
            page_content = await page.evaluate("document.body.innerText")
            
            # Cleanup
            await browser.close()
            
            if not page_content or len(page_content) < 100:
                print("⚠️ Warning: Scraped content is too short.")
                return {}

            print(f"✅ Extracted {len(page_content)} characters. Sending to LLM...")
            
            # Use LLM to structure this mess
            llm_result = extract_metadata_from_text(page_content, url)
            
            # Parse the LLM's JSON-like string (it returns "extraction_raw")
            # In a production app, we'd use JsonOutputParser. 
            # For now, we trust the chain generally returns valid structure or text we can return.
            # We return it as 'raw' and let the verification agent refine it.
            
            return {
                "scraped_text": page_content[:10000],  # Pass text to analysis node
                "llm_extracted": llm_result.get("extraction_raw", "")
            }

        except Exception as e:
            print(f"❌ Scraping Failed: {e}")
            await browser.close()
            return {}
