"""
Common utilities for LangGraph tool examples.
Reduces boilerplate while keeping demos clear and educational.
"""

from typing import Annotated, List, Optional, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
import os


# Standard state definition for all demos
class State(TypedDict):
    """Standard state for message-based conversations."""
    messages: Annotated[list, add_messages]


def create_demo_header(title: str, description: str, tools_info: List[str]) -> None:
    """Print a formatted header for demo applications."""
    print(f"\n{title}")
    print("=" * 50)
    print(description)
    print("\nAvailable tools:")
    for info in tools_info:
        print(f"- {info}")
    print("\nType 'quit' to exit")
    print("=" * 50)


def create_tool_graph(model_with_tools: Any, tools: List[BaseTool]) -> Any:
    """
    Create a standard LangGraph with tools.
    
    Simple pattern that covers 90% of use cases for demos.
    """
    graph = StateGraph(State)
    
    # Define a simple agent that calls the model
    def agent(state: State):
        return {"messages": [model_with_tools.invoke(state["messages"])]}
    
    # Add nodes
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(tools=tools))
    
    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "tools", END: END}
    )
    graph.add_edge("tools", "agent")
    
    return graph.compile()


def run_interactive_loop(
    graph: Any,
    initial_messages: Optional[List] = None
) -> None:
    """Run an interactive chat loop with the graph."""
    messages = initial_messages or []
    
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


def print_assistant_response(messages: List) -> None:
    """Print the latest assistant response from a message list."""
    for message in reversed(messages):
        if isinstance(message, AIMessage) and not message.tool_calls:
            print(f"\nAssistant: {message.content}")
            break


def get_system_prompt(role: str, instructions: str) -> SystemMessage:
    """Create a system prompt for demos."""
    return SystemMessage(content=f"{role}\n\n{instructions}")


def validate_environment() -> None:
    """Check that required environment variables are set."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  Missing API Key")
        print("=" * 50)
        print("Please set ANTHROPIC_API_KEY in your .env file")
        print("Get your key from: https://console.anthropic.com/")
        raise ValueError("ANTHROPIC_API_KEY not found")