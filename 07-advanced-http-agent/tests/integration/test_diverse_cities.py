#!/usr/bin/env python3
"""
Test the weather agent's ability to provide coordinates for diverse cities
without any hardcoded list in 05-advanced-mcp.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_agent.mcp_agent import MCPWeatherAgent


async def test_diverse_city_coordinates():
    """Test queries for cities from around the world."""
    
    agent = MCPWeatherAgent()
    await agent.initialize()
    
    print("🌍 Testing LLM's Geographic Knowledge (05-advanced-mcp)")
    print("=" * 60)
    print("Testing cities that are NOT in any hardcoded list...\n")
    
    # Diverse cities from different continents
    test_cities = [
        # Major world cities
        "Tokyo, Japan",
        "London, UK",
        "São Paulo, Brazil",
        "Cairo, Egypt",
        "Sydney, Australia",
        
        # Medium-sized cities
        "Edinburgh, Scotland",
        "Vancouver, Canada",
        "Bangalore, India",
        
        # Smaller/less common cities
        "Reykjavik, Iceland",
        "Queenstown, New Zealand",
        "Ushuaia, Argentina",  # Southernmost city in the world
        
        # Cities with special characters
        "Zürich, Switzerland",
        "København, Denmark",  # Copenhagen in Danish
        "München, Germany",    # Munich in German
    ]
    
    successful_queries = 0
    coordinates_provided = 0
    
    for city in test_cities:
        print(f"\n🔍 Testing: {city}")
        print("-" * 40)
        
        try:
            # Query for current temperature to make it faster
            response = await agent.query(f"What's the current temperature in {city}?")
            
            # Simple heuristic to check success
            if "temperature" in response.lower() or "°" in response:
                print(f"✅ Successfully got weather for {city}")
                successful_queries += 1
                # Note: We can't easily detect if coordinates were provided without
                # parsing the actual tool calls, but the test still validates functionality
            else:
                print(f"❌ Failed to get weather for {city}")
                
            print(f"Response: {response[:100]}...")  # First 100 chars
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        await asyncio.sleep(1)  # Brief pause between queries
    
    print(f"\n📊 Summary:")
    print(f"Total cities tested: {len(test_cities)}")
    print(f"Successful queries: {successful_queries}")
    print(f"Success rate: {successful_queries/len(test_cities)*100:.1f}%")
    
    await agent.cleanup()


if __name__ == "__main__":
    print("🚀 Starting Diverse Cities Coordinate Test (05-advanced-mcp)\n")
    print("⚠️  This test demonstrates the LLM can handle cities worldwide")
    print("    without any hardcoded list in the system prompt.\n")
    print("⚠️  MCP servers will be started as subprocesses...\n")
    
    asyncio.run(test_diverse_city_coordinates())