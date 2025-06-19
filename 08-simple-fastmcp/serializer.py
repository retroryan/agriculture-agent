from typing import Any
import yaml
from fastmcp import FastMCP


def custom_dict_serializer(data: Any) -> str:
    """Custom serializer that outputs YAML format instead of JSON."""
    return yaml.dump(data, width=100, sort_keys=False)


# Initialize FastMCP server with custom YAML serializer
server = FastMCP(
    name="SimpleFastMCPDemo", 
    tool_serializer=custom_dict_serializer
)


@server.tool
def get_example_data() -> dict:
    """Returns example structured data to demonstrate serialization."""
    return {
        "name": "Weather Station Alpha", 
        "temperature": 23.5,
        "humidity": 65,
        "conditions": ["partly_cloudy", "mild"],
        "timestamp": "2025-01-19T08:00:00Z"
    }


@server.tool 
def calculate_comfort_index(temperature: float, humidity: float) -> dict:
    """Calculate a simple comfort index based on temperature and humidity.
    
    Args:
        temperature: Temperature in Celsius
        humidity: Relative humidity percentage
    
    Returns:
        Comfort assessment with score and description
    """
    # Simple comfort calculation
    comfort_score = 100 - abs(temperature - 22) * 3 - abs(humidity - 50) * 0.5
    comfort_score = max(0, min(100, comfort_score))
    
    if comfort_score >= 80:
        description = "Very comfortable"
    elif comfort_score >= 60:
        description = "Comfortable"
    elif comfort_score >= 40:
        description = "Moderately comfortable"
    else:
        description = "Uncomfortable"
    
    return {
        "score": round(comfort_score, 1),
        "description": description,
        "temperature": temperature,
        "humidity": humidity
    }


if __name__ == "__main__":
    # Start the server with HTTP transport
    server.run(transport="streamable-http", host="127.0.0.1", port=7070, path="/mcp")
