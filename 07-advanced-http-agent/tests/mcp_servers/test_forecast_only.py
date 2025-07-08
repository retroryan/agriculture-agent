#!/usr/bin/env python3
"""
Test script for simplified forecast server.
Tests basic functionality before proceeding with full migration.
"""

import asyncio
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient


async def test_forecast_server():
    """Test the simplified forecast server."""
    print("🧪 Testing Simplified Forecast Server\n")
    
    # Create client for single server
    client = MultiServerMCPClient(
        {
            "forecast": {
                "url": "http://localhost:7071/mcp",
                "transport": "streamable_http"
            }
        }
    )
    
    try:
        # Test 1: Tool Discovery
        print("1. Testing tool discovery...")
        tools = await client.get_tools()
        print(f"   ✓ Found {len(tools)} tools")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description.split('.')[0]}")
        
        # Test 2: Get Forecast
        print("\n2. Testing get_forecast...")
        forecast_tool = next(t for t in tools if t.name == "forecast__get_forecast")
        result = await forecast_tool.ainvoke({
            "location": "San Francisco",
            "days": 3
        })
        print(f"   ✓ Got forecast for: {result.get('location', 'Unknown')}")
        print(f"   ✓ Days returned: {len(result.get('daily', {}).get('time', []))}")
        
        # Test 3: Get Current Weather
        print("\n3. Testing get_current_weather...")
        current_tool = next(t for t in tools if t.name == "forecast__get_current_weather")
        result = await current_tool.ainvoke({
            "location": "New York"
        })
        print(f"   ✓ Current temp in {result['location']}: {result['current']['temperature_2m']}°C")
        
        # Test 4: Error Handling
        print("\n4. Testing error handling...")
        result = await forecast_tool.ainvoke({
            "location": "Nonexistentcityxyz123"
        })
        if "error" in result:
            print(f"   ✓ Error handled gracefully: {result['error']}")
        
        print("\n✅ All tests passed! Simplified approach validated.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    finally:
        pass


if __name__ == "__main__":
    print("Make sure forecast_server_simple.py is running on port 7071!")
    print("Run with: python ../../mcp_servers/forecast_server_simple.py\n")
    
    success = asyncio.run(test_forecast_server())
    sys.exit(0 if success else 1)