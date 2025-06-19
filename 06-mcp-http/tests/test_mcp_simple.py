#!/usr/bin/env python3
"""
Simple test of MCP FastMCP client
"""

import asyncio
from fastmcp import Client
import json

async def test_fastmcp():
    """Test if we can connect to the FastMCP servers"""
    
    print("Testing FastMCP servers...")
    
    # Test forecast server
    try:
        client = Client("http://127.0.0.1:8000/mcp")
        
        async with client:
            # List available tools
            print("\n1. Testing forecast server tools list...")
            tools = await client.list_tools()
            print(f"Number of tools: {len(tools)}")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description[:60]}...")
            
            # Call the tool with coordinates
            print("\n2. Testing get_weather_forecast with coordinates...")
            result = await client.call_tool(
                "get_weather_forecast",
                {
                    "location": "Des Moines",
                    "latitude": 41.59,
                    "longitude": -93.62,
                    "days": 3
                }
            )
            print(f"Result type: {type(result)}")
            
            # FastMCP returns a list of content items
            if isinstance(result, list) and len(result) > 0:
                # Get the first TextContent item
                content = result[0]
                if hasattr(content, 'text'):
                    try:
                        data = json.loads(content.text)
                        print(f"✅ Successfully parsed JSON response")
                        print(f"Parsed JSON keys: {list(data.keys())[:5]}...")
                        if "location_info" in data:
                            print(f"✅ Location info: {data['location_info']}")
                            print(f"   → Using coordinates: ({data['location_info']['coordinates']['latitude']}, {data['location_info']['coordinates']['longitude']})")
                        if "current" in data:
                            current = data["current"]
                            print(f"✅ Current weather: {current.get('temperature_2m', 'N/A')}°C")
                    except Exception as e:
                        print(f"Failed to parse JSON: {e}")
                        print(f"Content (first 200 chars): {content.text[:200]}")
            else:
                print(f"Unexpected result format: {str(result)[:200]}")
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fastmcp())