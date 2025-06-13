#!/usr/bin/env python3
"""
Test MCP Integration

Simple test to verify MCP servers are working correctly.
"""

import asyncio
import sys
sys.path.append('04-mcp-architecture')

from weather_agent.mcp_agent import create_mcp_weather_agent


async def test_mcp():
    """Test basic MCP functionality."""
    print("🧪 Testing MCP Integration")
    print("=" * 50)
    
    # Initialize agent
    print("\n1️⃣ Initializing MCP Weather Agent...")
    try:
        agent = await create_mcp_weather_agent()
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Test queries
    test_queries = [
        "What's the weather in Ames, Iowa?",
        "Show me last week's temperatures for Fresno",
        "Are conditions good for planting in Grand Island?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n2️⃣ Test {i}: {query}")
        print("-" * 50)
        
        try:
            response = await agent.query(query)
            print(f"✅ Response: {response[:150]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Cleanup
    print("\n3️⃣ Cleaning up...")
    await agent.cleanup()
    print("✅ Test complete!")


if __name__ == "__main__":
    asyncio.run(test_mcp())
