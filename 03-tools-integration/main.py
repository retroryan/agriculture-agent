"""
Tool Chaining Example - Combined demonstration of basic and external tools working together.

NOTE: Review basic_tools and external_tools examples first!
This example shows how multiple tools can work together to accomplish complex tasks.

Run this example:
    python 03-tools-integration/main.py
"""

import sys
sys.path.append('03-tools-integration')

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os
from pathlib import Path

# Import tools from both modules
from basic_tools.tools import count_words, get_simulated_weather, agricultural_advice
from external_tools.fetch_tool import fetch_webpage, fetch_raw_content

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Define state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Combine tools from different modules
tools = [
    # External tools for fetching
    fetch_webpage,
    fetch_raw_content,
    # Basic tools for analysis
    count_words,
    get_simulated_weather,
    agricultural_advice
]

# Initialize model
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found. Please set it in your .env file.")

model = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    anthropic_api_key=api_key,
    temperature=0
).bind_tools(tools)

# Define chatbot node
def chatbot(state: State):
    """Process messages and potentially call tools."""
    return {"messages": [model.invoke(state["messages"])]}

# Build the graph
def create_combined_graph():
    """Create a graph that combines all tool types."""
    graph_builder = StateGraph(State)
    
    # Add nodes
    graph_builder.add_node("chatbot", chatbot)
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)
    
    # Add edges
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        {"tools": "tools", END: END}
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    
    return graph_builder.compile()

# Example: Weather-Based Agricultural Analysis
def weather_agriculture_demo():
    """Demonstrate fetching weather data and providing agricultural advice."""
    print("\n" + "="*60)
    print("Example 1: Weather-Based Agricultural Analysis")
    print("="*60)
    
    graph = create_combined_graph()
    
    messages = [
        SystemMessage(content="""You are an agricultural assistant that helps farmers.
        When asked about farming decisions, you should:
        1. Check the simulated weather for the location
        2. Provide appropriate agricultural advice based on conditions"""),
        HumanMessage(content="I'm growing corn in Iowa. What should I know about the current weather conditions and farming recommendations?")
    ]
    
    result = graph.invoke({"messages": messages})
    
    # Print the final response
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage) and not message.tool_calls:
            print(f"\nAssistant: {message.content}")
            break

# Example: Web Content Analysis
def web_content_analysis_demo():
    """Demonstrate fetching and analyzing web content."""
    print("\n" + "="*60)
    print("Example 2: Web Content Analysis")
    print("="*60)
    
    graph = create_combined_graph()
    
    messages = [
        SystemMessage(content="""You are a content analyst. When given a URL:
        1. Fetch the webpage content
        2. Analyze it using word count and other metrics
        3. Provide a summary of your findings"""),
        HumanMessage(content="How many stars to llamaindex have on github?")
    ]
    
    result = graph.invoke({"messages": messages})
    
    # Print the final response
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage) and not message.tool_calls:
            print(f"\nAssistant: {message.content}")
            break

# Example: Combined Analysis
def combined_analysis_demo():
    """Demonstrate multiple tools working together."""
    print("\n" + "="*60)
    print("Example 3: Combined Weather and Content Analysis")
    print("="*60)
    
    graph = create_combined_graph()
    
    messages = [
        SystemMessage(content="""You are a research assistant that combines information from multiple sources.
        Use all available tools to provide comprehensive answers."""),
        HumanMessage(content="""I found a weather API endpoint at https://api.open-meteo.com/v1/forecast?latitude=35&longitude=139&current=temperature_2m.
        Can you:
        1. Fetch the raw API response
        2. Tell me how many characters it contains
        3. Also check what the simulated weather shows for Tokyo
        4. Based on any weather patterns, what agricultural advice would you give?""")
    ]
    
    result = graph.invoke({"messages": messages})
    
    # Print the final response
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage) and not message.tool_calls:
            print(f"\nAssistant: {message.content}")
            break

# Interactive mode
def interactive_mode():
    """Run an interactive session with all tools available."""
    print("\n" + "="*60)
    print("Interactive Mode - All Tools Available")
    print("="*60)
    print("\nAvailable tools:")
    print("- fetch_webpage: Get and convert web content to markdown")
    print("- fetch_raw_content: Get raw API responses") 
    print("- count_words: Analyze text statistics")
    print("- get_simulated_weather: Get simulated weather data")
    print("- agricultural_advice: Get farming recommendations")
    print("\nTry combining tools in creative ways!")
    print("Type 'quit' to exit")
    print("="*60)
    
    graph = create_combined_graph()
    
    messages = [
        SystemMessage(content="""You are a helpful assistant with access to multiple tools.
        You can fetch web content, analyze text, check weather, and provide agricultural advice.
        Feel free to use multiple tools together to answer questions comprehensively.""")
    ]
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        messages.append(HumanMessage(content=user_input))
        result = graph.invoke({"messages": messages})
        messages = result["messages"]
        
        # Print the assistant's response
        for message in reversed(messages):
            if isinstance(message, AIMessage) and not message.tool_calls:
                print(f"\nAssistant: {message.content}")
                break

if __name__ == "__main__":
    print("Tool Chaining Demonstration")
    print("="*60)
    print("This example shows how different types of tools can work together")
    print("to accomplish complex tasks through tool chaining.\n")
    
    # Run demonstrations
    try:
        # Demo 1: Weather + Agriculture
        weather_agriculture_demo()
        
        # Demo 2: Web fetching + Analysis
        web_content_analysis_demo()
        
        # Demo 3: Everything combined
        combined_analysis_demo()
        
        # Interactive mode
        print("\n" + "="*60)
        response = input("\nWould you like to try interactive mode? (y/n): ")
        if response.lower() == 'y':
            interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure you have set ANTHROPIC_API_KEY in your .env file")