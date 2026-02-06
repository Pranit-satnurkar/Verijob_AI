from dotenv import load_dotenv
import os
load_dotenv()

from tools import search_company_health, search_reddit_sentiment

print(f"API Key present: {'Yes' if os.getenv('TAVILY_API_KEY') else 'No'}")

company = "Google" # Known entity
print(f"Testing search for: {company}")

health = search_company_health(company)
print(f"\nHealth Results: {health}")

reddit = search_reddit_sentiment(company)
print(f"\nReddit Results: {reddit}")
