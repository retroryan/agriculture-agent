import asyncio
from fastmcp import Client

async def main():
    # Connect to the complex_inputs server via HTTP
    http_url = "http://127.0.0.1:8001/mcp"
    async with Client(http_url) as client:
        # Prepare input data matching the ShrimpTank model
        tank = {
            "shrimp": [
                {"name": "Bubbles"},
                {"name": "Spot"}
            ]
        }
        extra_names = ["Tiny", "Biggie"]
        # Call the tool 'name_shrimp' as defined in the server
        result = await client.call_tool("name_shrimp", {"tank": tank, "extra_names": extra_names})
        print("Shrimp names:", result[0].text)

if __name__ == "__main__":
    asyncio.run(main())
