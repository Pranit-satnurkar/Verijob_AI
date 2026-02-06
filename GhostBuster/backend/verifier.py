from scraper import scrape_job_details
from agent import agent_graph

from typing import Optional
from tools import extract_metadata_from_text

async def verify_job_listing(url: str, content: Optional[str] = None):
    """
    Orchestrates the verification process using LangGraph Agent.
    """
    # 1. Extract Metadata
    if content:
        print(f"📥 Received content from extension for {url} ({len(content)} chars)")
        # Use simple structure if content is provided
        extraction = extract_metadata_from_text(content, url)
        # Use simple structure if content is provided
        extraction = extract_metadata_from_text(content, url)
        metadata = {
            "scraped_text": content[:10000],
            **extraction
        }
    else:
        metadata = await scrape_job_details(url)
    
    if not metadata:
        return {
            "status": "Error",
            "score": 0,
            "details": "Could not extract job details."
        }

    # 2. Run Agent Workflow
    initial_state = {
        "url": url,
        "metadata": metadata,
        "health_data": "",
        "analysis": {},
        "final_score": 0,
        "final_reasoning": ""
    }
    
    try:
        # Run the graph
        result_state = await agent_graph.ainvoke(initial_state)
        
        print(f"DEBUG: Agent Result Keys: {result_state.keys()}")
        print(f"DEBUG: Health Links: {result_state.get('health_links')}")
        print(f"DEBUG: Reddit Links: {result_state.get('reddit_links')}")
        
        return {
            "metadata": result_state['metadata'],
            "status": "Verified" if result_state['final_score'] > 70 else "Unverified",
            "score": result_state['final_score'],
            "details": result_state['final_reasoning'],
            "health_insights": result_state['health_data'][:200] + "..." if result_state['health_data'] else "No data",
            "ai_analysis": result_state['analysis'],
            "references": result_state.get('health_links', []) + result_state.get('reddit_links', [])
        }
    except Exception as e:
        print(f"Agent execution failed: {e}")
        return {
            "status": "Error",
            "score": 0,
            "details": f"AI Verification failed: {str(e)}"
        }
