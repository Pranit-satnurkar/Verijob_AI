from dotenv import load_dotenv
import os
load_dotenv()

from tools import extract_metadata_from_text

print(f"Groq API Key present: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")

sample_text = """
We are looking for a Senior Software Engineer at Google.
Location: Mountain View, CA.
Posted 2 days ago.
"""
print(f"Testing extraction...")

result = extract_metadata_from_text(sample_text, "http://example.com")
print(f"\nExtraction Result: {result}")
