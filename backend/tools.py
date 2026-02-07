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
        response = tavily_client.search(query, search_depth="advanced", max_results=5) # Fetch more, then filter
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
        response = tavily_client.search(query, search_depth="advanced", max_results=5) # Fetch more
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

def search_jobs(query: str = "Data Analyst jobs") -> List[Dict[str, Any]]:
    """
    Searches for recent job listings using Tavily.
    """
    if not tavily_client:
        return []

    try:
        # Search specifically for job listings across major platforms
        search_query = f"{query} hiring now in India site:linkedin.com/jobs OR site:naukri.com OR site:indeed.com"
        # Using a broader search query to get more results
        response = tavily_client.search(search_query, search_depth="advanced", max_results=6)
        results = response.get('results', [])
        
        jobs = []
        for r in results:
            title = r['title']
            company = "Unknown Company"
            
            # Simple heuristic to split Title - Company
            if " - " in title:
                parts = title.split(" - ")
                if len(parts) >= 2:
                    title = parts[0]
                    company = parts[1]
            elif "|" in title:
                parts = title.split("|")
                if len(parts) >= 2:
                    title = parts[0]
                    company = parts[1]

            jobs.append({
                "title": title[:50], # Truncate for UI
                "company": company[:30],
                "url": r['url'],
                "score": "NEW" 
            })
        return jobs
    except Exception as e:
        print(f"Job search error: {e}")
        return []
