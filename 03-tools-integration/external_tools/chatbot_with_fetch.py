"""
LangGraph chatbot with fetch tools - Phase 2 implementation.
This demonstrates how to use web fetching tools in a LangGraph chatbot.
"""

import sys
sys.path.append('03-tools-integration')

from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os
from pathlib import Path

# Import basic tools and fetch tools
from basic_tools.tools import get_current_time, count_words
from external_tools.fetch_tool import FETCH_TOOLS

# Load environment variables from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Define the state for our graph
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Combine basic and fetch tools
tools = [
    get_current_time,
    count_words,
    *FETCH_TOOLS  # Includes fetch_webpage and fetch_raw_content
]

# Initialize the Claude model with tools
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables. Please set it in your .env file.")

model = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    anthropic_api_key=api_key,
    temperature=0
).bind_tools(tools)

# Define the chatbot node function
def chatbot(state: State):
    """Process messages and potentially call tools."""
    return {"messages": [model.invoke(state["messages"])]}

# Build the graph
def create_fetch_chatbot_graph():
    """Create and compile the chatbot graph with fetch tools."""
    # Create a new graph
    graph_builder = StateGraph(State)
    
    # Add the chatbot node
    graph_builder.add_node("chatbot", chatbot)
    
    # Add the tool node
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)
    
    # Add conditional edge from chatbot
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        }
    )
    
    # Add edge from tools back to chatbot
    graph_builder.add_edge("tools", "chatbot")
    
    # Add edge from START to chatbot
    graph_builder.add_edge(START, "chatbot")
    
    # Compile the graph
    return graph_builder.compile()

# Main execution
if __name__ == "__main__":
    # Create the chatbot graph
    graph = create_fetch_chatbot_graph()
    
    print("External Tools Chatbot Demo")
    print("=" * 50)
    print("This chatbot can fetch and analyze web content.")
    print("Available tools:")
    print("- fetch_webpage: Fetches and converts web pages to markdown")
    print("- fetch_raw_content: Fetches raw content from URLs")
    print("- count_words: Analyzes text")
    print("- get_current_time: Shows current time")
    print("\nType 'quit' to exit")
    print("=" * 50)
    
    # Initialize conversation with system message
    messages = [
        SystemMessage(content="""You are a helpful assistant that can fetch and analyze web content.
        When users ask about web pages or online content, use the fetch_webpage tool to retrieve
        and analyze the content. Use fetch_raw_content for API responses or raw files.
        Always summarize key information from fetched content.""")
    ]
    
    # Example queries
    example_queries = [
        "What weather data can I get from the Open Meteo API?",
        "Fetch https://open-meteo.com/en/docs and tell me about the available APIs",
        "Get the content from https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m and analyze it",
        "How do I use the Open Meteo historical weather API?",
        "How does LlamaIndex compare to LangChain on Github and which has more stars?",
    ]
    
    print("\nExample queries you can try:")
    for query in example_queries[:2]:
        print(f"- {query}")
    print()
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        # Add user message
        messages.append(HumanMessage(content=user_input))
        
        # Run the graph
        result = graph.invoke({"messages": messages})
        
        # Update messages with the result
        messages = result["messages"]
        
        # Print the assistant's response
        for message in reversed(messages):
            if isinstance(message, AIMessage) and not message.tool_calls:
                print(f"\nAssistant: {message.content}")
                break