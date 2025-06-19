#!/usr/bin/env python3
"""
Test error handling in the weather agent system.
"""

import asyncio
import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from weather_agent.mcp_agent import MCPWeatherAgent
from mcp_servers.api_utils import get_coordinates


async def test_error_handling():
    """Test various error scenarios."""
    print("🧪 Testing Error Handling")
    print("=" * 60)
    
    # Test 1: Invalid location geocoding
    print("\n1. Testing invalid location geocoding...")
    try:
        coords = get_coordinates("ThisCityDoesNotExist12345")
        print(f"❌ Expected error but got: {coords}")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")
    
    # Test 2: Agent with invalid query
    print("\n2. Testing agent with nonsensical query...")
    agent = MCPWeatherAgent()
    await agent.initialize()
    
    try:
        result = await agent.query("What is the square root of weather?")
        print(f"✅ Agent handled nonsensical query gracefully")
        print(f"   Response preview: {result[:100]}...")
    except Exception as e:
        print(f"❌ Agent failed with error: {e}")
    
    # Test 3: Empty location
    print("\n3. Testing empty location string...")
    try:
        result = await agent.query("What's the weather in ?")
        print(f"✅ Agent handled empty location gracefully")
        print(f"   Response preview: {result[:100]}...")
    except Exception as e:
        print(f"❌ Agent failed with error: {e}")
    
    # Test 4: Invalid coordinates
    print("\n4. Testing invalid coordinates...")
    try:
        result = await agent.query("What's the weather at latitude 200, longitude 500?")
        print(f"✅ Agent handled invalid coordinates")
        print(f"   Response preview: {result[:100]}...")
    except Exception as e:
        print(f"❌ Agent failed with error: {e}")
    
    await agent.cleanup()
    print("\n✅ All error handling tests completed")


if __name__ == "__main__":
    asyncio.run(test_error_handling())