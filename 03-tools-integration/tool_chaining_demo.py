"""
Tool Chaining Demo - Shows how multiple tools work together.

This example demonstrates the unique power of tool composition,
where tools build on each other's outputs to solve complex problems.

Run: python tool_chaining_demo.py
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from shared.base import (
    create_demo_header,
    create_tool_graph,
    get_system_prompt,
    print_assistant_response,
    validate_environment
)
from config import get_model
from langchain_core.messages import HumanMessage

# Import specific tools for chaining demonstrations
from basic_tools.tools import count_words, get_simulated_weather, agricultural_advice
from external_tools.fetch_tool import fetch_webpage, fetch_raw_content

# Validate environment before proceeding
validate_environment()

# Select tools that work well together
tools = [
    fetch_webpage,
    fetch_raw_content,
    count_words,
    get_simulated_weather,
    agricultural_advice
]

# Initialize model and create graph
model = get_model().bind_tools(tools)
graph = create_tool_graph(model, tools)


def demo_tool_chaining():
    """Run two focused examples that showcase tool chaining."""
    
    print("\n" + "="*60)
    print("Example 1: Multi-Step Web Analysis")
    print("="*60)
    print("Watch how the agent uses multiple tools in sequence...")
    
    system_msg = get_system_prompt(
        role="You are a research assistant.",
        instructions="Break down complex requests into steps using available tools."
    )
    
    # First demo: Web fetch → Analysis → Summary
    messages = [
        system_msg,
        HumanMessage(content="""
        Can you analyze the Open-Meteo weather API documentation?
        1. Fetch the content from https://open-meteo.com/en/docs
        2. Count how many words it contains
        3. Tell me what weather parameters are available
        """)
    ]
    
    result = graph.invoke({"messages": messages})
    print_assistant_response(result["messages"])
    
    print("\n" + "="*60)
    print("Example 2: Combined Analysis with Multiple Data Sources")
    print("="*60)
    print("Watch how the agent combines different tools for a complete answer...")
    
    # Second demo: Multiple tools for comprehensive analysis
    messages = [
        system_msg,
        HumanMessage(content="""
        I need a complete weather analysis for farming:
        1. Get the simulated weather for Des Moines, Iowa
        2. Fetch real weather from: https://api.open-meteo.com/v1/forecast?latitude=41.6&longitude=-93.6&current=temperature_2m,precipitation
        3. Based on both sources, what's your agricultural advice for corn farming?
        """)
    ]
    
    result = graph.invoke({"messages": messages})
    print_assistant_response(result["messages"])


if __name__ == "__main__":
    create_demo_header(
        title="Tool Chaining Demonstration",
        description="See how tools work together to solve complex problems.",
        tools_info=[
            "Web fetching + Text analysis",
            "Weather data + Agricultural advice",
            "Multi-step problem decomposition"
        ]
    )
    
    try:
        # Run the focused demonstrations
        demo_tool_chaining()
        
        print("\n" + "="*60)
        print("\nKey Takeaways:")
        print("- Tools can use outputs from other tools")
        print("- Complex queries are broken into steps automatically")
        print("- Different tool combinations solve different problems")
        print("\nTry your own multi-step queries in the basic or external demos!")
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")