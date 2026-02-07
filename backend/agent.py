from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
from tools import search_company_health, analyze_job_description, search_reddit_sentiment
import datetime
import json

class AgentState(TypedDict):
    url: str
    metadata: Dict
    health_data: str
    health_links: List[Dict] # New
    reddit_data: str 
    reddit_links: List[Dict] # New
    analysis: Dict 
    temporal_analysis: str
    final_score: int
    final_reasoning: str

# --- Nodes ---

def search_node(state: AgentState):
    """
    Search for Company Health (Layoffs) AND Reddit Sentiment.
    """
    # 1. Try to find Company Name from metadata (LLM extraction might be a string, so we need safe parsing)
    # Ideally, scraper returns a dict. If it returned raw LLM string, we might need to parse it here.
    # For now, assume metadata has a 'company' key OR we try to fetch it.
    
    # 1. Try to find Company Name from metadata
    company_name = state.get("metadata", {}).get("company", "Unknown Company")
    
    # Fallback: if 'company' key is missing but 'llm_extracted' exists (e.g. parsing failed in tools)
    if company_name == "Unknown Company" and "llm_extracted" in state.get("metadata", {}):
        extracted_data = state["metadata"]["llm_extracted"]
        try:
             import json, re
             match = re.search(r"```json\s*(.*?)\s*```", extracted_data, re.DOTALL)
             if match:
                data = json.loads(match.group(1))
                company_name = data.get("company", "Unknown Company")
        except:
             pass

    # Extract Job Title if available
    job_title = state.get("metadata", {}).get("title", "")

    print(f"🔎 Searching intelligence for: {company_name} - {job_title}")
    
    # Parallelize these in production
    news_result = search_company_health(company_name, job_title)
    reddit_result = search_reddit_sentiment(company_name, job_title)
    
    return {
        "health_data": news_result.get("summary", ""), 
        "health_links": news_result.get("links", []),
        "reddit_data": reddit_result.get("summary", ""),
        "reddit_links": reddit_result.get("links", [])
    }

def analyze_node(state: AgentState):
    """
    Analyze JD Text for Ghost Job patterns.
    """
    # Prefer scraped text if available, else standard metadata
    jd_text = state["metadata"].get("scraped_text") or str(state["metadata"])
    
    analysis_result = analyze_job_description(jd_text)
    return {"analysis": analysis_result}

def temporal_audit_node(state: AgentState):
    """
    Check if the job is stale.
    """
    current_year = datetime.datetime.now().year
    # Try to find date in metadata
    text_corpus = str(state["metadata"]) + str(state.get("metadata", {}).get("llm_extracted", ""))
    
    audit_result = "Temporal Status: Unknown"
    
    if "2023" in text_corpus:
         audit_result = f"WARNING: Job appears to be from 2023. Current year is {current_year}."
    elif str(current_year) in text_corpus:
         audit_result = "Temporal Status: Current Year (Fresh)."
    
    return {"temporal_analysis": audit_result}

def score_node(state: AgentState):
    """
    Compute final Ghost Score based on all signals.
    """
    score = 100 # Start perfect
    reasons = []

    # 0. Sanity Check: Is there enough data?
    scraped_text = state["metadata"].get("scraped_text", "")
    if not scraped_text or len(scraped_text) < 200:
        return {
            "final_score": 0,
            "final_reasoning": "ERROR: Insufficient job data extracted. Verification incomplete."
        }
    
    # 1. JD Quality Check (AI-generated / Generic content)
    from tools import analyze_jd_quality
    jd_analysis = analyze_jd_quality(scraped_text)
    if jd_analysis["is_suspicious"]:
        penalty = 100 - jd_analysis["quality_score"]
        score -= penalty
        red_flag_summary = ", ".join(jd_analysis["red_flags"][:2])  # Show top 2
        reasons.append(f"JD Quality Issues: {red_flag_summary}")
    
    # 2. Health Check
    if "layoff" in state["health_data"].lower():
        score -= 30
        reasons.append("Company has recent layoff news.")
        
    # 3. Reddit Check
    if "scam" in state["reddit_data"].lower() or "ghosting" in state["reddit_data"].lower():
        score -= 25
        reasons.append("Negative sentiment/scam reports found on Reddit.")

    # 4. JD Analysis
    # Parse the LLM output (it might be a raw string)
    analysis_raw = state["analysis"].get("raw_analysis", "").lower()
    if "high probability" in analysis_raw or '"ghost_probability": 8' in analysis_raw or '"ghost_probability": 9' in analysis_raw:
        score -= 40
        reasons.append("Job Description matches 'Ghost Job' template patterns.")

    # 5. Temporal
    if "WARNING" in state["temporal_analysis"]:
        score -= 50
        reasons.append("Job listing is stale (detected previous year dates).")
    
    # Cap score
    score = max(0, score)
    
    # Psychological Rule: Never show 100% (User Trust Issue)
    if score > 95:
        score = 95
        
    return {
        "final_score": score,
        "final_reasoning": "; ".join(reasons) if reasons else "Job appears legitimate based on available signals."
    }

# --- Graph ---
workflow = StateGraph(AgentState)

workflow.add_node("search", search_node)
workflow.add_node("analyze", analyze_node)
workflow.add_node("temporal", temporal_audit_node)
workflow.add_node("score", score_node)

workflow.set_entry_point("search")
workflow.add_edge("search", "analyze")
workflow.add_edge("analyze", "temporal")
workflow.add_edge("temporal", "score")
workflow.add_edge("score", END)

agent_graph = workflow.compile()
