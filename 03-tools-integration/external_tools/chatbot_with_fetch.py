"""
LangGraph chatbot with external fetch tools.
Demonstrates web content fetching and analysis.
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from shared.base import (
    create_demo_header,
    create_tool_graph,
    run_interactive_loop,
    get_system_prompt,
    validate_environment
)
from config import get_model
from basic_tools.tools import count_words
from external_tools.fetch_tool import FETCH_TOOLS

# Validate environment before proceeding
validate_environment()

# Combine analysis and fetch tools
tools = [count_words, *FETCH_TOOLS]

# Initialize model and bind tools
model = get_model().bind_tools(tools)

# Create the graph
graph = create_tool_graph(model, tools)

if __name__ == "__main__":
    # Display demo header
    create_demo_header(
        title="External Tools Chatbot Demo",
        description="Fetch and analyze web content with LangGraph.",
        tools_info=[
            "fetch_webpage: Convert web pages to markdown",
            "fetch_raw_content: Get raw API responses",
            "count_words: Analyze text statistics"
        ]
    )
    
    # Initialize with system message
    system_message = get_system_prompt(
        role="You are a web content analyst.",
        instructions="Fetch and analyze web content when asked. Summarize key information from fetched content."
    )
    
    # Example queries
    print("\nExample queries:")
    print("- What's on the OpenAI homepage?")
    print("- Fetch weather data from Open-Meteo API")
    print("- How many stars does LangChain have on GitHub?")
    
    # Run interactive loop
    run_interactive_loop(graph, initial_messages=[system_message])