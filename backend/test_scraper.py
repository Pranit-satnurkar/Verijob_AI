import asyncio
from scraper import scrape_job_details

# Test URL (using a generic one, but user can replace)
# Using a LinkedIn or Naukri URL would be ideal, but for now we test the function call.
TEST_URL = "https://www.google.com/about/careers/applications/jobs/results/" 

async def main():
    print(f"Testing scraper with URL: {TEST_URL}")
    result = await scrape_job_details(TEST_URL)
    print("Scraping Result Keys:", result.keys())
    if "scraped_text" in result:
        print(f"Scraped Text Length: {len(result['scraped_text'])}")
    else:
        print("Failed to scrape text.")

if __name__ == "__main__":
    asyncio.run(main())
