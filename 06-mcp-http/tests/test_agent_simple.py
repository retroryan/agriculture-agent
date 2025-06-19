#!/usr/bin/env python3
"""
Simple test of the weather agent
"""

import asyncio
import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from weather_agent.mcp_agent import MCPWeatherAgent

async def test_agent():
    """Test a simple query"""
    agent = None
    try:
        print("Creating weather agent...")
        agent = MCPWeatherAgent()
        
        print("Initializing agent...")
        await agent.initialize()
        
        print("Querying for Des Moines weather...")
        response = await agent.query("What's the weather forecast for Des Moines?")
        
        print(f"\nResponse:\n{response}")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if agent:
            await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(test_agent())