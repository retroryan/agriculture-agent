import asyncio
from typing import Any

import yaml

from fastmcp import FastMCP


# Define a simple custom serializer
def custom_dict_serializer(data: Any) -> str:
    return yaml.dump(data, width=100, sort_keys=False)


server = FastMCP(name="CustomSerializerExample", tool_serializer=custom_dict_serializer)


from typing import Optional

@server.tool
def get_example_data(dummy: Optional[str] = None) -> dict:
    """Returns some example data."""
    return {"name": "Test", "value": 123, "status": True}


if __name__ == "__main__":
    # Start the server with HTTP transport for remote clients
    print("Starting FastMCP server on http://127.0.0.1:8000/mcp")
    print("Press Ctrl+C to stop")
    server.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")
