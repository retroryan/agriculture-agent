import asyncio
from fastmcp import Client

async def main():
    # Connect to the local MCP server via HTTP
    http_url = "http://127.0.0.1:7070/mcp"
    async with Client(http_url) as client:
        # Call the tool 'get_example_data' as defined in the server
        result = await client.call_tool("get_example_data", {})
        # The result should be serialized as YAML
        print("Serialized tool result:\n", result[0].text)

if __name__ == "__main__":
    asyncio.run(main())
