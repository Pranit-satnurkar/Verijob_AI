import pytest
from unittest.mock import MagicMock, patch
from agent import agent_graph, AgentState

@pytest.mark.asyncio
async def test_agent_workflow_mocked():
    # Mock data
    initial_state = {
        "url": "http://example.com",
        "metadata": {"company": "Test Corp", "title": "Dev", "description": "We are hiring"},
        "health_data": "",
        "analysis": {},
        "final_score": 0,
        "final_reasoning": ""
    }

    # Patch tools
    with patch('tools.search_company_health') as mock_search, \
         patch('tools.analyze_job_description') as mock_analyze:
        
        mock_search.return_value = "No layoffs found."
        mock_analyze.return_value = {"ghost_probability": 10, "analysis": "Looks real."}

        # Run Graph
        result = await agent_graph.ainvoke(initial_state)

        # Assertions
        assert result['final_score'] > 0
        assert "health_data" in result
        assert "analysis" in result

@pytest.mark.asyncio
async def test_agent_stale_job():
    initial_state = {
        "url": "http://example.com/old",
        "metadata": {
            "company": "Old Corp", 
            "title": "Dev", 
            "description": "Hiring",
            "posted_date": "2023-01-01" # Stale date
        },
        "health_data": "",
        "analysis": {},
        "temporal_analysis": {},
        "final_score": 0,
        "final_reasoning": ""
    }

    with patch('tools.search_company_health') as mock_search, \
         patch('tools.analyze_job_description') as mock_analyze:
        
        mock_search.return_value = "Everything is fine."
        mock_analyze.return_value = {"ghost_probability": 0}

        result = await agent_graph.ainvoke(initial_state)

        # Check for penalty
        # Base 50 + 10 (Health) + 10 (Analysis) - 30 (Stale) = 40
        assert result['final_score'] == 40
        assert result['temporal_analysis']['is_stale'] is True
