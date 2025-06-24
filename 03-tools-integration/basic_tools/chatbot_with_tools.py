"""
LangGraph chatbot with basic tools demonstration.
Shows fundamental tool integration patterns in LangGraph.
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
from basic_tools.tools import ALL_TOOLS

# Validate environment before proceeding
validate_environment()

# Initialize model and bind tools
model = get_model().bind_tools(ALL_TOOLS)

# Create the graph
graph = create_tool_graph(model, ALL_TOOLS)

if __name__ == "__main__":
    # Display demo header
    create_demo_header(
        title="Basic Tools Chatbot Demo",
        description="Demonstrates fundamental tool usage in LangGraph.",
        tools_info=[
            "Math operations (add, multiply)",
            "Weather simulation",
            "Text analysis",
            "Date/time utilities",
            "Agricultural advice"
        ]
    )
    
    # Initialize with system message
    system_message = get_system_prompt(
        role="You are a helpful assistant with various tools.",
        instructions="Use the appropriate tools to answer questions about math, weather, text, dates, and agriculture."
    )
    
    # Example queries
    print("\nExample queries:")
    print("- What's 42 plus 17?")
    print("- What's the weather in Berlin?")
    print("- How many words are in 'hello world'?")
    
    # Run interactive loop
    run_interactive_loop(graph, initial_messages=[system_message])