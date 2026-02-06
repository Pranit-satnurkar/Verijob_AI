from dotenv import load_dotenv
import os
load_dotenv()

from tools import search_company_health, search_reddit_sentiment

company = "Tata Consultancy Services"
role = "Data Analyst"

print(f"Testing filtered search for: {company} - {role}")

print("\n--- Health News ---")
health = search_company_health(company, role)
for link in health.get('links', []):
    print(f" [KEEP] {link['title']}")

print("\n--- Reddit ---")
reddit = search_reddit_sentiment(company, role)
for link in reddit.get('links', []):
    print(f" [KEEP] {link['title']}")
