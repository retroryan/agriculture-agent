#!/usr/bin/env python3
"""
Test if the LLM provides coordinates for various cities in 05-advanced-mcp.
Check the MCP server outputs to see if geocoding API is called or if coordinates are provided directly.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_agent.mcp_agent import MCPWeatherAgent


async def test_coordinate_provision():
    """Test a few diverse cities and check coordinate usage."""
    
    agent = MCPWeatherAgent()
    await agent.initialize()
    
    print("🌍 Testing Coordinate Provision by LLM (05-advanced-mcp)")
    print("=" * 60)
    print("Watch the terminal output to see if geocoding is used or coordinates provided directly\n")
    
    # Test cities - mix of well-known and less common
    test_queries = [
        ("Tokyo", "What's the weather in Tokyo?"),
        ("Paris", "Tell me the temperature in Paris, France"),
        ("Mumbai", "Is it raining in Mumbai?"),
        ("Reykjavik", "What's the forecast for Reykjavik, Iceland?"),
        ("Cape Town", "Show me the weather in Cape Town, South Africa"),
        ("Coordinates", "What's the weather at latitude 35.6762, longitude 139.6503?"),  # Tokyo coordinates
    ]
    
    for city_name, query in test_queries:
        print(f"\n📍 Testing: {city_name}")
        print(f"Query: {query}")
        print("-" * 60)
        
        try:
            response = await agent.query(query)
            print(f"Response: {response[:150]}...")
            print("\n✅ Check output above to see if geocoding was used or coordinates provided")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Pause to make output easier to read
        await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("📋 In the output above, look for:")
    print("  - 'Geocoding location' = LLM didn't provide coordinates")
    print("  - Direct weather API call = LLM provided coordinates!")
    print("=" * 60)
    
    await agent.cleanup()


if __name__ == "__main__":
    print("🚀 Starting Coordinate Provision Test (05-advanced-mcp)\n")
    print("⚠️  This will start MCP servers as subprocesses\n")
    
    asyncio.run(test_coordinate_provision())