#!/usr/bin/env python3
"""
Test script for the fast location coordinate feature.
Tests both direct coordinate usage and fallback to geocoding.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_agent.mcp_agent import MCPWeatherAgent


async def test_coordinates():
    """Test various coordinate and location scenarios."""
    agent = MCPWeatherAgent()
    await agent.initialize()
    
    print("\n" + "="*60)
    print("🧪 Testing Fast Location Coordinate Feature")
    print("="*60 + "\n")
    
    # Test cases
    test_cases = [
        {
            "name": "1. Location name only (traditional geocoding)",
            "query": "What's the weather in Des Moines, Iowa?",
            "expected": "Should use geocoding API"
        },
        {
            "name": "2. Coordinates provided by user",
            "query": "What's the weather at latitude 41.5868, longitude -93.6250 (Des Moines)?",
            "expected": "Should use provided coordinates directly"
        },
        {
            "name": "3. Ambiguous location requiring geocoding",
            "query": "What's the weather in Springfield?",
            "expected": "Should attempt geocoding (may fail due to ambiguity)"
        },
        {
            "name": "4. Farm coordinates",
            "query": "Check soil moisture at coordinates 42.0, -94.0 (my corn field in Iowa)",
            "expected": "Should use coordinates for agricultural data"
        },
        {
            "name": "5. Historical weather with coordinates",
            "query": "What was the weather like last month at lat 40.7128, lon -74.0060 (New York)?",
            "expected": "Should use coordinates for historical data"
        },
        {
            "name": "6. Invalid location fallback",
            "query": "What's the weather in Atlantis?",
            "expected": "Should fail gracefully with geocoding error"
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print(f"Query: {test['query']}")
        print(f"Expected: {test['expected']}")
        print("-" * 60)
        
        try:
            response = await agent.query(test['query'])
            print(f"✅ Response: {response[:200]}...")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    # Test direct tool performance comparison
    print("\n\n" + "="*60)
    print("⏱️  Performance Comparison")
    print("="*60 + "\n")
    
    import time
    
    # Test with location name (requires geocoding)
    start = time.time()
    await agent.query("What's the current temperature in Chicago?")
    geocoding_time = time.time() - start
    print(f"With geocoding: {geocoding_time:.2f} seconds")
    
    # Test with coordinates (no geocoding)
    start = time.time()
    await agent.query("What's the current temperature at 41.8781, -87.6298 (Chicago)?")
    direct_time = time.time() - start
    print(f"With coordinates: {direct_time:.2f} seconds")
    
    print(f"\n🚀 Speed improvement: {geocoding_time/direct_time:.1f}x faster with coordinates!")
    
    await agent.cleanup()


if __name__ == "__main__":
    print("Starting coordinate feature tests...")
    asyncio.run(test_coordinates())