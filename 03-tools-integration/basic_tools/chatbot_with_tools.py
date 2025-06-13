"""
LangGraph chatbot with tools - Tutorial 2 implementation.
This demonstrates how to add tools to a LangGraph chatbot.
Based on: https://langchain-ai.github.io/langgraph/tutorials/get-started/2-add-tools/
"""

import sys
sys.path.append('03-tools-integration')

from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from dotenv import load_dotenv
import os
from pathlib import Path

# Import our basic tools
from basic_tools.tools import (
    add_numbers,
    multiply_numbers,
    get_simulated_weather,
    count_words,
    get_current_time,
    calculate_days_between,
    agricultural_advice
)

# Load environment variables from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Define the state for our graph
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Select which tools to use for this example
tools = [
    add_numbers,
    multiply_numbers,
    get_simulated_weather,
    count_words,
    get_current_time,
    calculate_days_between,
    agricultural_advice
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
    # Check if the last message is a tool message
    # If so, we need to call the model to generate a response
    messages = state["messages"]
    last_message = messages[-1] if messages else None
    
    # Only invoke the model if we need a response
    # (i.e., after user input or after tool execution)
    if isinstance(last_message, (HumanMessage, ToolMessage)):
        return {"messages": [model.invoke(messages)]}
    
    # If the last message is already an AI message without tool calls,
    # don't invoke the model again
    return {"messages": []}

# Build the graph
def create_tool_chatbot_graph():
    """Create and compile the chatbot graph with tools."""
    # Create a new graph
    graph_builder = StateGraph(State)
    
    # Add the chatbot node
    graph_builder.add_node("chatbot", chatbot)
    
    # Add the tool node - this will execute tools when called
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)
    
    # Add conditional edge from chatbot
    # This decides whether to call tools or end
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        {
            "tools": "tools",    # If tools should be called
            END: END,           # If no tools needed
        }
    )
    
    # Add edge from tools back to chatbot
    # After tools are executed, go back to chatbot
    graph_builder.add_edge("tools", "chatbot")
    
    # Add edge from START to chatbot
    graph_builder.add_edge(START, "chatbot")
    
    # Compile the graph
    return graph_builder.compile()

# Main execution
if __name__ == "__main__":
    # Create the chatbot graph
    graph = create_tool_chatbot_graph()
    
    # Example conversation
    print("Basic Tools Chatbot Demo")
    print("=" * 50)
    print("This chatbot has access to basic tools including:")
    print("- Mathematical operations (add, multiply)")
    print("- Simulated weather data (demo only)")
    print("- Text analysis (word count)")
    print("- Date/time operations")
    print("- Agricultural advice")
    print("\nType 'quit' to exit")
    print("=" * 50)
    
    # Initialize conversation with system message
    messages = [
        SystemMessage(content="""You are a helpful assistant with access to various tools.
        You can help with calculations, weather information, text analysis, date/time queries,
        and basic agricultural advice. When users ask questions, use the appropriate tools
        to provide accurate answers.""")
    ]
    
    # Example queries to demonstrate
    example_queries = [
        "What's 42 plus 17?",
        "What's the simulated weather for Berlin, Germany?",
        "How many words are in this sentence?",
        "What's the current time?",
        "How many days between 2024-01-01 and 2024-12-31?",
        "Should I water my corn if it's dry?",
        "Calculate 15.5 multiplied by 3.2"
    ]
    
    print("\nExample queries you can try:")
    for query in example_queries[:3]:
        print(f"- {query}")
    print("...and more!\n")
    
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
        
        # Print the assistant's response (last non-tool message)
        for message in reversed(messages):
            if isinstance(message, AIMessage) and not message.tool_calls:
                print(f"\nAssistant: {message.content}")
                break