#!/usr/bin/env python3
"""Test Claude directly with tool calling"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Define a simple tool
tools = [
    {
        "name": "get_weather",
        "description": "Get weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location to get weather for"
                }
            },
            "required": ["location"]
        }
    }
]

# Test query
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What's the weather in Ames, Iowa?"}
    ],
    tools=tools
)

print("Response:")
print(response)
print("\nContent:")
for content in response.content:
    print(f"Type: {type(content)}")
    print(f"Content: {content}")