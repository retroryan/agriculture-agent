from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os
from pathlib import Path
import sys
import argparse

# Load environment variables from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Check if API key is loaded
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in environment variables")
    print(f"Looking for .env file at: {env_path.absolute()}")
    print("Please ensure you have a .env file with ANTHROPIC_API_KEY=your-api-key")
    exit(1)

# Define the state for our graph
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the Claude model
model = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    anthropic_api_key=api_key,
    temperature=0
)

# Define the chatbot node function
def chatbot(state: State):
    """Process messages and generate a response."""
    return {"messages": [model.invoke(state["messages"])]}

# Build the graph
def create_chatbot_graph():
    """Create and compile the chatbot graph."""
    # Create a new graph
    graph_builder = StateGraph(State)
    
    # Add the chatbot node
    graph_builder.add_node("chatbot", chatbot)
    
    # Add edge from START to chatbot
    graph_builder.add_edge(START, "chatbot")
    
    # Add edge from chatbot to END
    graph_builder.add_edge("chatbot", END)
    
    # Compile the graph
    return graph_builder.compile()

def run_interactive_mode(graph):
    """Run the chatbot in interactive mode."""
    print("Open Meteo API Expert - Interactive Mode")
    print("=" * 50)
    print("This chatbot can help you understand Open Meteo API data")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    # Initialize conversation with system message
    messages = [
        SystemMessage(content="""You are a helpful assistant that specializes in Open Meteo API data. 
        You can help users understand weather forecasts, historical weather data, climate models, 
        and various meteorological parameters available through https://open-meteo.com/en/docs.""")
    ]
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        # Add user message to conversation
        messages.append(HumanMessage(content=user_input))
        
        # Run the graph with current messages
        result = graph.invoke({"messages": messages})
        
        # Get the last message (AI response)
        ai_message = result["messages"][-1]
        
        # Print the response
        print(f"\nAssistant: {ai_message.content}")
        
        # Update messages list with the full conversation
        messages = result["messages"]

def run_demo_mode(graph):
    """Run the chatbot in demo mode with predefined queries."""
    print("Open Meteo API Expert - Demo Mode")
    print("=" * 50)
    print("Running automated demo queries...")
    print("=" * 50)
    
    # Define demo queries
    demo_queries = [
        "What is Open Meteo API and what weather data does it provide?",
        "How can I get a 7-day weather forecast for New York City using the API?",
        "What's the difference between temperature_2m and apparent_temperature in the API response?",
        "Can you show me how to get historical weather data for the past month?"
    ]
    
    # Initialize conversation with system message
    messages = [
        SystemMessage(content="""You are a helpful assistant that specializes in Open Meteo API data. 
        You can help users understand weather forecasts, historical weather data, climate models, 
        and various meteorological parameters available through https://open-meteo.com/en/docs.""")
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n[Demo Query {i}]: {query}")
        print("-" * 40)
        
        # Add query to messages
        messages.append(HumanMessage(content=query))
        
        # Run the graph
        result = graph.invoke({"messages": messages})
        
        # Get and print the response
        ai_message = result["messages"][-1]
        print(f"Assistant: {ai_message.content}")
        
        # Update messages for context
        messages = result["messages"]
        
        # Add a separator between queries
        if i < len(demo_queries):
            print("\n" + "=" * 50)
            input("Press Enter for next query...")

def run_single_query(graph, query):
    """Run a single query and return the response."""
    # Initialize conversation with system message
    messages = [
        SystemMessage(content="""You are a helpful assistant that specializes in Open Meteo API data. 
        You can help users understand weather forecasts, historical weather data, climate models, 
        and various meteorological parameters available through https://open-meteo.com/en/docs."""),
        HumanMessage(content=query)
    ]
    
    # Run the graph
    result = graph.invoke({"messages": messages})
    
    # Print the response
    print(f"Query: {query}")
    print("=" * 50)
    print(result["messages"][-1].content)

# Main execution
if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Open Meteo API Expert Chatbot - LangGraph implementation',
        epilog='Examples:\n'
               '  python basic_chatbot.py                    # Run in interactive mode\n'
               '  python basic_chatbot.py --demo             # Run demo mode\n'
               '  python basic_chatbot.py "Your question"    # Single query mode',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('query', nargs='*', help='Query to ask (if not provided, runs in interactive mode)')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode with example queries')
    
    args = parser.parse_args()
    
    # Create the chatbot graph
    graph = create_chatbot_graph()
    
    # Determine which mode to run
    if args.demo:
        run_demo_mode(graph)
    elif args.query:
        # Join all query parts into a single string
        query = " ".join(args.query)
        run_single_query(graph, query)
    else:
        run_interactive_mode(graph)