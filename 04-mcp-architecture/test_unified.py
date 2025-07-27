"""Simple tests for unified weather server."""

import httpx
import asyncio


async def test_forecast():
    """Test forecast endpoint with location name."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:7071/mcp/call-tool",
            json={
                "name": "get_weather_forecast",
                "arguments": {
                    "location": "Chicago, IL",
                    "days": 3
                }
            }
        )
        print("Forecast Test (location name):")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Summary: {data.get('summary', 'No summary')}")
        else:
            print(f"Error: {response.text}")
        print()


async def test_forecast_coords():
    """Test forecast endpoint with coordinates."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:7071/mcp/call-tool",
            json={
                "name": "get_weather_forecast",
                "arguments": {
                    "latitude": 41.8781,
                    "longitude": -87.6298,
                    "days": 3
                }
            }
        )
        print("Forecast Test (coordinates):")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Summary: {data.get('summary', 'No summary')}")
        else:
            print(f"Error: {response.text}")
        print()


async def test_historical():
    """Test historical weather endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:7071/mcp/call-tool",
            json={
                "name": "get_historical_weather",
                "arguments": {
                    "location": "Des Moines, IA",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07"
                }
            }
        )
        print("Historical Test:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Summary: {data.get('summary', 'No summary')}")
        else:
            print(f"Error: {response.text}")
        print()


async def test_agricultural():
    """Test agricultural conditions endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:7071/mcp/call-tool",
            json={
                "name": "get_agricultural_conditions",
                "arguments": {
                    "location": "Ames, Iowa",
                    "days": 5
                }
            }
        )
        print("Agricultural Test:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Summary: {data.get('summary', 'No summary')}")
        else:
            print(f"Error: {response.text}")
        print()


async def main():
    """Run all tests."""
    print("Testing Unified Weather Server")
    print("=" * 40)
    print("Make sure server is running: python -m mcp_servers.weather_server")
    print("=" * 40)
    print()
    
    await test_forecast()
    await test_forecast_coords()
    await test_historical()
    await test_agricultural()


if __name__ == "__main__":
    asyncio.run(main())