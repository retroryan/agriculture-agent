#!/usr/bin/env python3
"""
Simple test to verify coordinate handling works in 05-advanced-mcp
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_agent.mcp_agent import MCPWeatherAgent


async def test_simple():
    """Test a single query to verify the system works."""
    
    print("🧪 Testing 05-advanced-mcp coordinate handling\n")
    
    agent = MCPWeatherAgent()
    await agent.initialize()
    
    # Test with a city not in any hardcoded list
    print("📍 Testing: Berlin, Germany")
    response = await agent.query("What's the current temperature in Berlin, Germany?")
    print(f"\nResponse: {response}")
    
    # Test with explicit coordinates
    print("\n📍 Testing: Coordinates (52.52, 13.405) - Berlin")
    response = await agent.query("What's the weather at latitude 52.52, longitude 13.405?")
    print(f"\nResponse: {response}")
    
    await agent.cleanup()
    print("\n✅ Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_simple())