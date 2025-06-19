#!/usr/bin/env python3
"""
Demo script showing how the weather agent uses coordinate parameters.
This demonstrates the fast-location approach where the LLM provides coordinates.
"""

import asyncio
from weather_agent.mcp_agent import MCPWeatherAgent


async def demo_coordinate_queries():
    """Demonstrate queries where the LLM can provide coordinates."""
    
    agent = MCPWeatherAgent()
    await agent.initialize()
    
    print("🌍 Weather Agent with Fast Location (Coordinate) Support")
    print("=" * 60)
    
    # Test queries that should trigger coordinate usage
    test_queries = [
        # Well-known cities
        "What's the weather forecast for Des Moines?",
        "Show me Chicago weather for the next 3 days",
        "Is it raining in New York right now?",
        
        # Coordinate-based queries
        "What's the weather at latitude 41.5868, longitude -93.6250?",
        "Get forecast for coordinates 40.7128, -74.0060",
        "Show agricultural conditions at 42.36,-71.06",
        
        # Agricultural queries
        "What's the soil moisture in Chicago for farming?",
        "Is it good planting weather in Des Moines this week?",
        "Show me historical rainfall in New York for last month"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 60)
        
        try:
            response = await agent.query(query)
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
        await asyncio.sleep(1)  # Brief pause between queries
    
    print("\n✅ Demo complete!")
    
    # Show how the agent would call tools with coordinates
    print("\n📊 Example Tool Calls with Coordinates:")
    print("=" * 60)
    print("""
When the agent recognizes a well-known city or coordinates, it calls tools like:

1. For "Chicago weather":
   get_weather_forecast(
       location="Chicago",
       latitude=41.88,
       longitude=-87.63,
       days=7
   )

2. For "coordinates 40.7128, -74.0060":
   get_weather_forecast(
       location="40.7128, -74.0060",
       latitude=40.7128,
       longitude=-74.0060,
       days=7
   )

This bypasses the geocoding API for faster, more reliable results!
""")


if __name__ == "__main__":
    print("🚀 Starting Weather Agent Coordinate Demo\n")
    print("⚠️  Assuming MCP servers are already running...\n")
    
    asyncio.run(demo_coordinate_queries())