import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient
from typing import Dict, Any, List

# Initialize Clients
tavily_api_key = os.getenv("TAVILY_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

print(f"DEBUG: Tools initialized. Tavily Key Present: {bool(tavily_api_key)}")

tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None
llm = ChatGroq(
    groq_api_key=groq_api_key, 
    model_name="llama-3.3-70b-versatile"
) if groq_api_key else None


import time
import random

def safe_tavily_search(query: str, **kwargs) -> Dict[str, Any]:
    """
    Wraps Tavily search with retry logic to handle connection resets.
    """
    if not tavily_client:
        return {}
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return tavily_client.search(query, **kwargs)
        except Exception as e:
            print(f"⚠️ Tavily search failed (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt + random.random()) # Exponential backoff
            else:
                print("❌ Max retries reached for Tavily search.")
                return {} # Return empty on final failure
    return {}


def analyze_jd_quality(jd_text: str) -> Dict[str, Any]:
    """
    Analyzes job description quality to detect AI-generated or generic postings.
    Returns a score (0-100) and list of red flags.
    """
    if not jd_text or len(jd_text) < 100:
        return {"quality_score": 0, "red_flags": ["Insufficient content"], "is_suspicious": True}
    
    red_flags = []
    score = 100
    
    # Generic buzzwords that indicate AI-generated or template content
    generic_phrases = [
        "rockstar", "ninja", "guru", "wizard", "unicorn",
        "wear many hats", "fast-paced environment", "work hard play hard",
        "competitive salary", "exciting opportunity", "dynamic team",
        "self-starter", "go-getter", "think outside the box"
    ]
    
    # AI-generation indicators
    ai_indicators = [
        "as a [role], you will", "the ideal candidate will",
        "we are looking for a highly motivated", "join our growing team",
        "this is an exciting opportunity to", "you will be responsible for"
    ]
    
    # Vague requirements (lack of specifics)
    vague_indicators = [
        "various tasks", "other duties as assigned", "and more",
        "etc.", "among other things", "as needed"
    ]
    
    jd_lower = jd_text.lower()
    
    # Check for generic buzzwords
    buzzword_count = sum(1 for phrase in generic_phrases if phrase in jd_lower)
    if buzzword_count >= 3:
        red_flags.append(f"Contains {buzzword_count} generic buzzwords")
        score -= 15
    
    # Check for AI-generation patterns
    ai_pattern_count = sum(1 for phrase in ai_indicators if phrase in jd_lower)
    if ai_pattern_count >= 3:
        red_flags.append("Shows AI-generated content patterns")
        score -= 20
    
    # Check for vague language
    vague_count = sum(1 for phrase in vague_indicators if phrase in jd_lower)
    if vague_count >= 2:
        red_flags.append("Contains vague/non-specific requirements")
        score -= 15
    
    # Check for specificity (good signs)
    specific_indicators = [
        "salary", "₹", "$", "compensation", "benefits",
        "team size", "reporting to", "tech stack", "tools:",
        "years of experience", "degree in", "certification"
    ]
    specificity_count = sum(1 for phrase in specific_indicators if phrase in jd_lower)
    
    if specificity_count < 2:
        red_flags.append("Lacks specific details (salary, team, tech stack)")
        score -= 20
    
    # Check for excessive length (AI tends to be verbose)
    if len(jd_text) > 5000:
        red_flags.append("Unusually long description (possible AI padding)")
        score -= 10
    
    # Check for repetitive structure
    sentences = jd_text.split('.')
    if len(sentences) > 10:
        # Simple repetition check
        unique_starts = len(set(s.strip()[:20] for s in sentences if len(s.strip()) > 20))
        if unique_starts < len(sentences) * 0.7:
            red_flags.append("Repetitive sentence structure")
            score -= 15
    
    score = max(0, score)
    is_suspicious = score < 60 or len(red_flags) >= 3
    
    return {
        "quality_score": score,
        "red_flags": red_flags,
        "is_suspicious": is_suspicious,
        "specificity_count": specificity_count
    }



def filter_irrelevant_sources(results: List[Dict], company_name: str, job_title: str) -> List[Dict]:
    """
    Uses LLM to filter out search results that are not relevant to the specific company/role.
    """
    if not results or not llm:
        return results

    # Create a summarized list for the LLM to evaluate
    sources_text = "\n".join([f"ID {i}: Title: {r['title']}, Content: {r['content'][:150]}..." for i, r in enumerate(results)])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strict relevance filter. Return ONLY the IDs of relevant sources."),
        ("human", f"""
        We are verifying a job listing for '{company_name}' - '{job_title}'.
        
        Evaluate these search results. mark as RELEVANT only if they strictly discuss:
        1. '{company_name}' specifically (not just a list of all companies).
        2. Bad interview experiences, scams, or layoffs related to this company.
        
        If a result is a generic "Top 10 jobs" or "List of layoffs" without specific details on {company_name}, it is IRRELEVANT.
        
        Sources:
        {sources_text}
        
        Return a JSON list of relevant IDs, e.g., [0, 2]. If none are relevant, return [].
        """)
    ])
    
    chain = prompt | llm
    try:
        import json, re
        response = chain.invoke({})
        content = response.content
        
        # Parse IDs
        relevant_ids = []
        match = re.search(r"\[.*?\]", content, re.DOTALL)
        if match:
             relevant_ids = json.loads(match.group(0))
        
        filtered_results = [results[i] for i in relevant_ids if i < len(results)]
        return filtered_results
    except Exception as e:
        print(f"Filtering error: {e}")
        return results # Fallback to original list

def search_company_health(company_name: str, job_title: str = "") -> Dict[str, Any]:
    """
    Searches for recent news about company layoffs, hiring freezes, or funding.
    """
    if not tavily_client:
        return {"summary": "Error: TAVILY_API_KEY not found.", "links": []}
        
    # Construct more specific query
    query = f"{company_name} layoffs hiring freeze funding news 2024 2025"
    if job_title and job_title.lower() != "unknown":
         query = f"{company_name} {job_title} layoffs hiring freeze 2024 2025"

    try:
        response = safe_tavily_search(query, search_depth="advanced", max_results=5) # Fetch more, then filter
        results = response.get('results', [])
        
        # Filter with LLM
        filtered_results = filter_irrelevant_sources(results, company_name, job_title)
        
        # Summarize results into a string
        results_text = "\n".join([f"- {result['title']}: {result['content']}" for result in filtered_results])
        links = [{"title": r['title'], "url": r['url']} for r in filtered_results]
        return {
            "summary": results_text if results_text else "No specific news found after filtering.",
            "links": links
        }
    except Exception as e:
        return {"summary": f"Error performing search: {str(e)}", "links": []}

def search_reddit_sentiment(company_name: str, job_title: str = "") -> Dict[str, Any]:
    """
    Searches Reddit for negative sentiment/scam reports about the company.
    """
    if not tavily_client:
        return {"summary": "Error: TAVILY_API_KEY not found.", "links": []}
    
    # Targeting reddit.com with specific negative keywords
    query = f"site:reddit.com {company_name} (scam OR ghosting OR fake job OR interview experience)"
    if job_title and job_title.lower() != "unknown":
         query = f"site:reddit.com {company_name} {job_title} (scam OR ghosting OR fake job OR interview experience)"

    try:
        response = safe_tavily_search(query, search_depth="advanced", max_results=5) # Fetch more
        results = response.get('results', [])
        
        # Filter
        filtered_results = filter_irrelevant_sources(results, company_name, job_title)
        
        if not filtered_results:
            return {"summary": "No specific negative discussions found on Reddit.", "links": []}
            
        summary = "\n".join([f"- {r['title']}: {r['content'][:200]}..." for r in filtered_results])
        links = [{"title": r['title'], "url": r['url']} for r in filtered_results]
        return {"summary": summary, "links": links}
    except Exception as e:
        return {"summary": f"Error searching Reddit: {str(e)}", "links": []}

def analyze_job_description(jd_text: str) -> Dict[str, Any]:
    """
    Uses Groq (Llama 3) to analyze if a JD looks like a 'Ghost Job' template.
    """
    if not llm:
        return {"ghost_probability": 0, "analysis": "Error: GROQ_API_KEY not found."}

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert HR recruiter and scam detector. Analyze the following Job Description (JD)."),
        ("human", """
        Analyze this JD text for 'Ghost Job' signals. 
        Signals:
        1. Vague responsibilities vs Generic requirements.
        2. 'Evergreen' language (e.g. 'We are always hiring for...').
        3. Lack of specific team details.
        4. Overly broad salary ranges or mismatched requirements.
        
        Job Description Text:
        {jd_text}
        
        Return a JSON response with:
        - ghost_probability (integer 0-100)
        - main_concerns (summarized text)
        - is_template (boolean)
        """)
    ])
    
    chain = prompt | llm
    try:
        # Truncate text to avoid token limits if necessary, Llama 3 70b has good context though
        safe_text = jd_text[:8000] 
        response = chain.invoke({"jd_text": safe_text})
        content = response.content
        return {"raw_analysis": content}
    except Exception as e:
        return {"error": str(e)}


def extract_metadata_from_text(raw_text: str, url: str) -> Dict[str, Any]:
    """
    Uses LLM to extract structured metadata (Title, Company, Date) from raw page text.
    """
    if not llm:
        return {}

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a data extraction assistant. Extract job details from the provided raw text."),
        ("human", """
        Extract the following fields from the text below.
        
        URL: {url}
        Text: {text}
        
        Return JSON with:
        - title (string)
        - company (string)
        - location (string)
        - posted_date (string YYYY-MM-DD, try to infer relative dates like '2 days ago' based on today's date)
        - source (e.g. LinkedIn, Indeed, Company Site)
        """)
    ])
    
    chain = prompt | llm
    try:
        import re
        import json
        
        safe_text = raw_text[:5000]
        response = chain.invoke({"url": url, "text": safe_text})
        content = response.content
        
        # Parse JSON
        extracted_data = {}
        match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
        if match:
             json_str = match.group(1)
        else:
             start = content.find("{")
             end = content.rfind("}")
             if start != -1 and end != -1:
                 json_str = content[start:end+1]
             else:
                 json_str = ""

        if json_str:
            try:
                extracted_data = json.loads(json_str)
            except:
                pass
                
        # Return merged result
        return {
            "llm_extracted": content, # Keep raw for debugging
            **extracted_data # Merge parsed fields (company, title, etc)
        }
    except Exception as e:
        print(f"Extraction error: {e}")
        return {}


def search_hiring_signals() -> List[Dict[str, Any]]:
    """
    Searches for 'Green Flags' - signs of active hiring, funding, or expansion.
    """
    if not tavily_client:
        return []

    signals = []
    
    # 3 Distinct queries to get diverse signals
    queries = [
        {"q": "companies raising series A B funding 2024 2025 news", "type": "FUNDING"},
        {"q": "companies mass hiring engineering india 2024 2025", "type": "HIRING SURGE"},
        {"q": "site:reddit.com received interview offer software engineer india 2025", "type": "INTERVIEWS"}
    ]

    try:
        for q_obj in queries:
            response = safe_tavily_search(q_obj["q"], search_depth="advanced", max_results=3)
            results = response.get('results', [])
            
            for r in results:
                title = r['title']
                # Simple cleaning
                company = "Unknown"
                if " - " in title:
                    company = title.split(" - ")[0]
                elif "|" in title:
                    company = title.split("|")[0]
                else:
                    # Fallback: Try to find a capitalized word in the title
                    words = title.split()
                    for w in words:
                        if w[0].isupper() and len(w) > 3 and w.lower() not in ["layoffs", "hiring", "news", "report", "funding"]:
                            company = w
                            break
                
                signals.append({
                    "company": company[:30],
                    "title": title[:80], # Headline
                    "url": r['url'],
                    "type": q_obj["type"],
                    "score": "SIGNAL" # Marker for UI
                })
        
        # Shuffle slightly to mix types (optional, but good for feed)
        import random
        random.shuffle(signals)
        return signals[:9] # Return top 9 mixed signals

    except Exception as e:
        print(f"Signal search error: {e}")
        return []

