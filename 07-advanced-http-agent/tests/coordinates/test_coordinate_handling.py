#!/usr/bin/env python3
"""
Test script to verify coordinate handling in 05-advanced-mcp
"""
import asyncio
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_forecast_server():
    """Test if the forecast server accepts coordinates directly."""
    
    print("Testing 05-advanced-mcp Forecast Server coordinate handling...")
    print("=" * 60)
    
    # Path to the forecast server
    server_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_servers", "forecast_server.py")
    
    # Create server params
    server_params = StdioServerParameters(
        command="python",
        args=[server_path]
    )
    
    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Get available tools
            tools = await session.list_tools()
            print("\nAvailable tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}")
                if tool.name == "get_weather_forecast":
                    print(f"    Schema: {json.dumps(tool.inputSchema, indent=4)}")
            
            # Test 1: Location string only
            print("\n1. Testing with location string only:")
            try:
                result = await session.call_tool(
                    "get_weather_forecast",
                    {"location": "Des Moines, Iowa", "days": 3}
                )
                # Parse the response text to extract location info
                response_text = result.content[0].text
                print(f"✅ Success with location string")
                if "location_info" in response_text:
                    print("   Response includes location_info")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Test 2: Using coordinates directly (SHOULD WORK in 05-advanced-mcp)
            print("\n2. Testing with direct coordinates (SUPPORTED in 05-advanced-mcp):")
            try:
                result = await session.call_tool(
                    "get_weather_forecast",
                    {
                        "location": "Custom Location at Coordinates",
                        "latitude": 41.5908,
                        "longitude": -93.6208,
                        "days": 3
                    }
                )
                response_text = result.content[0].text
                print(f"✅ Success with coordinates!")
                # Check if the custom location name is preserved
                if "Custom Location at Coordinates" in response_text:
                    print("   ✅ Custom location name preserved")
                if "41.5908" in response_text and "-93.6208" in response_text:
                    print("   ✅ Coordinates used directly without geocoding")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Test 3: Coordinates only (no location name)
            print("\n3. Testing with coordinates only (no location name):")
            try:
                result = await session.call_tool(
                    "get_weather_forecast",
                    {
                        "location": "",  # Empty location
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                        "days": 2
                    }
                )
                response_text = result.content[0].text
                print(f"✅ Success with coordinates only!")
                if "40.7128,-74.006" in response_text:
                    print("   ✅ Fallback location name uses coordinates")
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing coordinate handling in 05-advanced-mcp...")
    asyncio.run(test_forecast_server())