import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any
import asyncio
from tools import extract_metadata_from_text, safe_tavily_search

# Try imports for Playwright
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

def scrape_naukri_specific(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extracts data specifically from Naukri's DOM structure.
    Enhanced with JSON-LD and meta tag extraction.
    """
    try:
        # 1. Job Description
        description = ""
        desc_element = soup.find("div", {"class": "styles_job-desc-container__txpYf"}) or soup.find("section", {"class": "job-desc"})
        if desc_element:
            description = desc_element.get_text(separator="\n", strip=True)
            
        # 2. Title and Company - Try multiple methods
        title = ""
        company = ""
        
        # Method 1: JSON-LD Schema (most reliable)
        json_ld = soup.find("script", {"type": "application/ld+json"})
        if json_ld:
            try:
                import json
                data = json.loads(json_ld.string)
                if isinstance(data, dict):
                    title = data.get("title", "") or data.get("name", "")
                    if "hiringOrganization" in data:
                        company = data["hiringOrganization"].get("name", "")
            except:
                pass
        
        # Method 2: Meta tags
        if not title:
            title_meta = soup.find("meta", {"property": "og:title"}) or soup.find("meta", {"name": "title"})
            if title_meta:
                title = title_meta.get("content", "")
        
        # Method 3: DOM selectors (new Naukri layout)
        if not title or not company:
            header = soup.find("header", {"class": "styles_jd-header__kv1aP"})
            if header:
                if not title:
                    title_elem = header.find("h1")
                    if title_elem: title = title_elem.get_text(strip=True)
                
                if not company:
                    comp_elem = header.find("div", {"class": "styles_jd-header-comp-name__MvqAI"})
                    if comp_elem: company = comp_elem.get_text(strip=True)
            
        # Method 4: Older layouts
        if not title:
            title_elem = soup.find("h1", {"class": "jd-header-title"})
            if title_elem: title = title_elem.get_text(strip=True)
            
        if not company:
            comp_elem = soup.find("a", {"class": "jd-header-comp-name"})
            if comp_elem: company = comp_elem.get_text(strip=True)
        
        # Fallback: Extract from page title
        if not title and soup.title:
            page_title = soup.title.string or ""
            # Naukri format: "Job Title - Company Name | Naukri.com"
            if " - " in page_title:
                parts = page_title.split(" - ")
                title = parts[0].strip()
                if " | " in parts[1]:
                    company = parts[1].split(" | ")[0].strip()

        if description:
            return {
                "scraped_text": description[:15000],
                "title": title or "UNKNOWN_ROLE",
                "company": company or "UNKNOWN_ENTITY"
            }
    except Exception as e:
        print(f"⚠️ Naukri Specific Parse Failed: {e}")
        
    return {}

async def scrape_with_tavily(url: str) -> Dict[str, Any]:
    """
    Option 3: Use Search Snippets/API to get content (Lightweight & Reliable).
    """
    print(f"🔍 Scraping via Tavily Search API: {url}...")
    try:
        # Use Tavily's search to find the URL content
        # We search specifically for the URL or "job description {url}"
        response = safe_tavily_search(
            query=url, 
            search_depth="advanced", 
            include_raw_content=True,
            max_results=1
        )
        
        results = response.get('results', [])
        if not results:
            print("⚠️ Tavily found no results for this URL.")
            return {}
            
        best_result = results[0]
        content = best_result.get('raw_content') or best_result.get('content')
        
        if content and len(content) > 300:
            print(f"✅ Tavily Extracted {len(content)} chars.")
            extraction_result = extract_metadata_from_text(content, url)
            return {
                "scraped_text": content[:15000],
                **extraction_result
            }
    except Exception as e:
        print(f"❌ Tavily Scrape Failed: {e}")
        
    return {}

async def scrape_with_curl_cffi(url: str) -> Dict[str, Any]:
    """
    Advanced scraper using curl_cffi to mimic real Chrome TLS fingerprint.
    Best for Naukri to avoid 'Access Denied'.
    """
    try:
        from curl_cffi.requests import AsyncSession
    except ImportError:
        print("⚠️ curl_cffi not installed. skipping advanced scrape.")
        return {}

    print(f"🕵️‍♂️ Scraping with curl_cffi (Chrome Masquerade): {url}...")
    try:
        # Impersonate Chrome 120
        async with AsyncSession(impersonate="chrome120") as s:
            response = await s.get(url, timeout=30)
            
        if response.status_code == 200:
            # Check for block
            if "Access Denied" in response.text or "Security Check" in response.text:
                 print("⚠️ curl_cffi got blocked (Access Denied).")
                 return {} # Fallback

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Naukri specific parsing
            if "naukri.com" in url:
                naukri_data = scrape_naukri_specific(soup)
                if naukri_data:
                    print("✅ curl_cffi Successfully Scraped Naukri!")
                    return naukri_data
            
            # General fallback
            text = soup.get_text(separator=' ', strip=True)
            if len(text) > 500:
                 print(f"✅ curl_cffi Extracted {len(text)} chars.")
                 extraction_result = extract_metadata_from_text(text, url)
                 return {"scraped_text": text[:15000], **extraction_result}
                 
    except Exception as e:
        print(f"❌ curl_cffi Scrape Failed: {e}")
        
    return {}

async def scrape_with_httpx(url: str) -> Dict[str, Any]:
    """
    Primary scraper using HTTPX (No browser required).
    """
    print(f"🚀 Scraping with HTTPX: {url}...")
    if "naukri.com" in url:
        print("🎯 Detected Naukri URL, preparing specific headers...")
    
    # Specific headers for Naukri to prevent blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for Naukri specific content first
            if "naukri.com" in url:
                # print(f"🕵️‍♂️ Naukri Raw HTML Preview: {response.text[:500]}")
                # with open("debug_naukri.html", "w", encoding="utf-8") as f:
                #     f.write(response.text)
                
                naukri_data = scrape_naukri_specific(soup)
                if naukri_data:
                    print("✅ Successfully used Naukri-specific parser.")
                    return naukri_data
                else:
                    print("⚠️ Naukri parser matched nothing.")

            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            text = soup.get_text(separator=' ', strip=True)
            
            if len(text) > 500:
                print(f"✅ HTTPX Extracted {len(text)} chars.")
                extraction_result = extract_metadata_from_text(text, url)
                return {
                    "scraped_text": text[:15000], 
                    **extraction_result
                }
            else:
                print(f"⚠️ HTTPX content too short ({len(text)} chars).")
    except Exception as e:
        print(f"❌ HTTPX Failed: {e}")
        
    return {}

async def scrape_with_playwright(url: str) -> Dict[str, Any]:
    """
    Secondary scraper using Playwright (Only if installed & HTTPX fails).
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {}

    print(f"🕸️ Attempting Playwright for: {url}...")
    browser = None
    try:
        async with async_playwright() as p:
            # Try to verify if browser exists BEFORE launching to avoid crash
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
                )
            except Exception as launch_err:
                print(f"⛔ Playwright binary missing or launch failed: {launch_err}")
                return {} 

            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(5000) # Wait for hydration
                page_content = await page.evaluate("document.body.innerText")
                
                if len(page_content) > 500:
                   extraction_result = extract_metadata_from_text(page_content, url)
                   return {"scraped_text": page_content[:15000], **extraction_result}
            finally:
                await browser.close()
                
    except Exception as e:
        print(f"❌ Playwright execution error: {e}")
    
    return {}

async def scrape_job_details(url: str) -> Dict[str, Any]:
    """
    Main scraping entry point.
    Strategy: 
    1. Naukri -> Tavily (Option 3 - API based)
    2. Others -> HTTPX -> Playwright
    """
    print(f"🕸️ Scraping URL: {url}...")

    # SPECIAL HANDLING FOR NAUKRI
    if "naukri.com" in url:
        print("⚡ Naukri URL detected: Using Advanced TLS Fingerprinting (curl_cffi)...")
        # 1. Try curl_cffi (Best for evasion)
        result = await scrape_with_curl_cffi(url)
        if result:
            return result
        
        # 2. Try Search Snippets (Tavily - Option 3)
        print("⚠️ curl_cffi failed. Trying Search Snippets (Option 3)...")
        result = await scrape_with_tavily(url)
        if result:
            return result
        
        # 3. Fallback to Playwright
        if PLAYWRIGHT_AVAILABLE:
             print("⚠️ Tavily failed. Trying Playwright fallback...")
             result = await scrape_with_playwright(url)
             if result: return result

    # 1. Try HTTPX first (Standard Strategy for non-Naukri)
    result = await scrape_with_httpx(url)
    if result:
        return result
        
    # 2. Try Playwright only if HTTPX failed
    try:
        if PLAYWRIGHT_AVAILABLE:
            result = await scrape_with_playwright(url)
            if result:
                return result
    except Exception:
        pass
        
    # 3. Last Resort: Tavily (if everything else failed)
    print("⚠️ Standard methods failed. Trying Tavily as last resort...")
    result = await scrape_with_tavily(url)
    if result: return result

    print("❌ All scraping methods failed.")
    return {
        "error": "Could not extract content. Please paste Job Description manually."
    }
