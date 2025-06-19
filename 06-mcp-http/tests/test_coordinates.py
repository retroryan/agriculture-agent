#!/usr/bin/env python3
"""
Test script to verify coordinate handling in MCP servers.
Tests both location strings and direct latitude/longitude parameters.
"""

import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass


async def test_server(server_url: str, tool_name: str, params: dict):
    """Test a single MCP server endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            # FastMCP uses JSON-RPC format
            request_data = {
                "jsonrpc": "2.0",
                "method": f"tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": params
                },
                "id": 1
            }
            
            response = await client.post(
                server_url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "error" in result:
                    return f"❌ Error: {result['error']}"
                elif "result" in result:
                    data = result["result"]
                    if isinstance(data, dict) and "location_info" in data:
                        loc_info = data["location_info"]
                        return f"✅ Found: {loc_info.get('name', 'Unknown')} at ({loc_info['coordinates']['latitude']}, {loc_info['coordinates']['longitude']})"
                    elif isinstance(data, dict) and "error" in data:
                        return f"❌ API Error: {data['error']}"
                    else:
                        return f"✅ Response received (no location_info)"
                else:
                    return f"❌ Unexpected response format"
            else:
                return f"❌ HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return f"❌ Exception: {str(e)}"


async def test_coordinate_handling():
    """Test coordinate handling with various location formats."""
    
    print("🧪 Testing Coordinate Handling in MCP Servers")
    print("=" * 60)
    
    # Test locations with various formats
    test_locations = [
        # Standard formats
        ("New York", "Basic city name"),
        ("London, UK", "City with country"),
        ("Tokyo, Japan", "International city"),
        ("Des Moines, Iowa", "City with state"),
        
        # Edge cases
        ("paris", "Lowercase city"),
        ("BERLIN", "Uppercase city"),
        ("San Francisco, CA", "City with abbreviation"),
        ("New York, NY, USA", "Full format"),
        ("123 Main St, Boston", "Address format"),
        
        # Ambiguous locations
        ("Springfield", "Ambiguous city name"),
        ("Paris, Texas", "Non-capital Paris"),
        
        # Invalid locations
        ("XYZ123ABC", "Invalid location"),
        ("", "Empty string"),
        ("   ", "Whitespace only"),
    ]
    
    # Server configurations
    servers = [
        ("http://127.0.0.1:8000", "get_weather_forecast", lambda loc: {"location": loc, "days": 3}),
        ("http://127.0.0.1:8001", "get_historical_weather", lambda loc: {"location": loc, "start_date": "2024-01-01", "end_date": "2024-01-07"}),
        ("http://127.0.0.1:8002", "get_agricultural_conditions", lambda loc: {"location": loc, "days": 3}),
    ]
    
    for server_url, tool_name, param_func in servers:
        server_name = tool_name.replace("get_", "").replace("_", " ").title()
        print(f"\n📡 Testing {server_name} Server ({server_url})")
        print("-" * 40)
        
        for location, description in test_locations[:5]:  # Test first 5 for brevity
            params = param_func(location)
            result = await test_server(server_url, tool_name, params)
            print(f"{description:.<30} {location:.<20} {result}")
            await asyncio.sleep(0.1)  # Small delay to avoid rate limiting
    
    print("\n" + "=" * 60)
    print("✅ Coordinate handling test complete!")


async def test_geocoding_directly():
    """Test the geocoding API directly to understand its behavior."""
    print("\n🗺️ Testing Geocoding API Directly")
    print("=" * 60)
    
    from mcp_servers.api_utils import OpenMeteoClient
    
    client = OpenMeteoClient()
    
    test_cases = [
        "New York",
        "Paris",
        "Paris, Texas",
        "Springfield",
        "Des Moines, Iowa",
        "London, UK",
        "XYZ123ABC"
    ]
    
    async with client:
        for location in test_cases:
            try:
                # Test the geocode function directly
                results = await client.geocode(location, count=3)
                print(f"\n📍 {location}:")
                if results:
                    for i, result in enumerate(results[:3]):
                        print(f"  {i+1}. {result.get('name', 'Unknown')}, {result.get('admin1', '')}, {result.get('country', '')}")
                        print(f"     Lat: {result['latitude']}, Lon: {result['longitude']}")
                else:
                    print("  No results found")
                    
                # Test get_coordinates which picks the first result
                try:
                    lat, lon = await client.get_coordinates(location)
                    print(f"  → Selected: ({lat}, {lon})")
                except ValueError as e:
                    print(f"  → Error: {e}")
                    
            except Exception as e:
                print(f"  ❌ Exception: {e}")


async def test_direct_coordinates():
    """Test MCP servers with direct latitude/longitude parameters."""
    print("\n🌐 Testing Direct Coordinate Parameters")
    print("=" * 60)
    
    # Test cases with coordinates
    test_cases = [
        {
            "description": "Rural farm field",
            "location": "Farm Field",
            "latitude": 41.5868,
            "longitude": -93.6250
        },
        {
            "description": "Specific GPS location",
            "location": "GPS Point",
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        {
            "description": "Agricultural center",
            "location": "Field 42",
            "latitude": 42.3601,
            "longitude": -71.0589
        }
    ]
    
    # Server configurations for coordinate testing
    servers = [
        {
            "url": "http://127.0.0.1:8000",
            "tool": "get_weather_forecast",
            "params": lambda tc: {
                "location": tc["location"],
                "latitude": tc["latitude"],
                "longitude": tc["longitude"],
                "days": 3
            }
        },
        {
            "url": "http://127.0.0.1:8001",
            "tool": "get_historical_weather",
            "params": lambda tc: {
                "location": tc["location"],
                "latitude": tc["latitude"],
                "longitude": tc["longitude"],
                "start_date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                "end_date": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
            }
        },
        {
            "url": "http://127.0.0.1:8002",
            "tool": "get_agricultural_conditions",
            "params": lambda tc: {
                "location": tc["location"],
                "latitude": tc["latitude"],
                "longitude": tc["longitude"],
                "days": 3
            }
        }
    ]
    
    for server in servers:
        server_name = server["tool"].replace("get_", "").replace("_", " ").title()
        print(f"\n📡 Testing {server_name} Server with Coordinates")
        print("-" * 40)
        
        for test_case in test_cases:
            params = server["params"](test_case)
            result = await test_server(server["url"], server["tool"], params)
            
            # Check if coordinates were used
            if "✅" in result and "at (" in result:
                # Extract coordinates from result
                coords_str = result.split("at (")[1].split(")")[0]
                lat_str, lon_str = coords_str.split(", ")
                result_lat = float(lat_str)
                result_lon = float(lon_str)
                
                # Verify coordinates match
                if abs(result_lat - test_case["latitude"]) < 0.001 and abs(result_lon - test_case["longitude"]) < 0.001:
                    result += " [COORDS USED ✓]"
                else:
                    result += " [GEOCODED ✗]"
            
            print(f"{test_case['description']:.<30} {result}")
            await asyncio.sleep(0.1)
    
    print("\n" + "=" * 60)
    print("✅ Direct coordinate test complete!")


if __name__ == "__main__":
    print("🚀 Starting MCP Server Coordinate Handling Tests\n")
    print("⚠️  Make sure the MCP servers are running:")
    print("   1. Run ./start_servers.sh in another terminal")
    print("   2. Wait for servers to start")
    print("   3. Then run this test\n")
    
    asyncio.run(test_coordinate_handling())
    asyncio.run(test_direct_coordinates())
    asyncio.run(test_geocoding_directly())