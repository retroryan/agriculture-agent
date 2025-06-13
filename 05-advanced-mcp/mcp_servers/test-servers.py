#!/usr/bin/env python3
"""Test all MCP servers to ensure they're working correctly."""

import asyncio
import sys
import os

# Add the 05-advanced-mcp directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_agent.mcp_agent import MCPWeatherAgent


async def test_weather_queries():
    """Test queries that exercise all MCP servers."""
    print("🧪 Testing MCP Weather Servers (05-advanced-mcp)")
    print("=" * 60)
    
    # Initialize agent
    print("\n1️⃣ Initializing MCP Weather Agent...")
    try:
        agent = MCPWeatherAgent()
        await agent.initialize()
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Test queries that exercise different servers using valid agricultural locations
    test_queries = [
        # Tests forecast server
        ("Forecast Server", "What's the current weather in Ames, Iowa?"),
        
        # Tests historical server  
        ("Historical Server", "What was the temperature in Fresno, California last week?"),
        
        # Tests agricultural server
        ("Agricultural Server", "What are the soil conditions in Grand Island, Nebraska?"),
        
        # Tests forecast server again
        ("Forecast Server", "Give me a 3-day forecast for Lubbock, Texas"),
        
        # Tests historical comparison
        ("Historical Server", "Compare June 2023 vs June 2024 temperatures in Cedar Rapids, Iowa"),
        
        # Tests agricultural analysis
        ("Agricultural Server", "Analyze growing conditions in Amarillo, Texas for April 2024")
    ]
    
    success_count = 0
    
    for i, (server_name, query) in enumerate(test_queries, 1):
        print(f"\n2️⃣ Test {i} ({server_name}): {query}")
        print("-" * 70)
        
        try:
            response = await agent.query(query)
            if response and len(response.strip()) > 10:
                print(f"✅ Success: {response[:100]}...")
                success_count += 1
            else:
                print(f"⚠️ Warning: Empty or short response")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Cleanup
    print(f"\n3️⃣ Test Results: {success_count}/{len(test_queries)} passed")
    await agent.cleanup()
    
    if success_count == len(test_queries):
        print("✅ All server tests passed!")
        return True
    else:
        print(f"❌ {len(test_queries) - success_count} tests failed")
        return False


async def main():
    """Run all server tests."""
    try:
        success = await test_weather_queries()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())