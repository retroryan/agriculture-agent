#!/usr/bin/env python3
"""Simple test of native tool calling"""

import asyncio
import sys
sys.path.append('.')

from weather_agent.mcp_agent import MCPWeatherAgent


async def test_simple_query():
    """Test a simple weather query with native tools."""
    print("🧪 Testing Simple Native Tool Call")
    print("=" * 50)
    
    # Create agent
    agent = MCPWeatherAgent()
    
    try:
        # Initialize
        print("\n🔌 Initializing MCP connections...")
        await agent.initialize()
        
        # Test query
        query = "What's the weather forecast for Ames, Iowa for the next 3 days?"
        print(f"\n📝 Query: {query}")
        print("\n💭 Processing with native tools...")
        
        response = await agent.query_with_native_tools(query)
        
        print(f"\n🤖 Response: {response}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(test_simple_query())