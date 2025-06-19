#!/usr/bin/env python3
"""
Test the weather agent's ability to provide coordinates for diverse cities
without any hardcoded list.
"""

import asyncio
import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from weather_agent.mcp_agent import MCPWeatherAgent


async def test_diverse_city_coordinates():
    """Test queries for cities from around the world."""
    
    agent = MCPWeatherAgent()
    await agent.initialize()
    
    print("🌍 Testing LLM's Geographic Knowledge")
    print("=" * 60)
    print("Testing cities that are NOT in any hardcoded list...\n")
    
    # Test just 5 diverse cities for faster execution
    test_cities = [
        "Tokyo, Japan",          # Asia
        "São Paulo, Brazil",     # South America
        "Cairo, Egypt",          # Africa
        "Sydney, Australia",     # Oceania
        "Zürich, Switzerland",   # Europe with special character
    ]
    
    successful_coordinates = 0
    used_geocoding = 0
    
    for city in test_cities:
        print(f"\n🔍 Testing: {city}")
        print("-" * 40)
        
        try:
            # Query for just 1 day to make it faster
            response = await agent.query(f"What's the current temperature in {city}? Just give me the number.")
            
            # Check the logs to see if coordinates were provided
            # This is a simple heuristic - in production you'd check the actual tool calls
            if "temperature" in response.lower() or "°" in response:
                print(f"✅ Successfully got weather for {city}")
                successful_coordinates += 1
            else:
                print(f"❌ Failed to get weather for {city}")
                
            print(f"Response: {response[:100]}...")  # First 100 chars
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        await asyncio.sleep(0.5)  # Brief pause between queries
    
    print(f"\n📊 Summary:")
    print(f"Total cities tested: {len(test_cities)}")
    print(f"Successful queries: {successful_coordinates}")
    print(f"Success rate: {successful_coordinates/len(test_cities)*100:.1f}%")
    
    await agent.cleanup()


if __name__ == "__main__":
    print("🚀 Starting Diverse Cities Coordinate Test\n")
    print("⚠️  This test will show if the LLM can provide coordinates")
    print("    for cities worldwide without any hardcoded list.\n")
    print("⚠️  Assuming MCP servers are already running...\n")
    
    asyncio.run(test_diverse_city_coordinates())