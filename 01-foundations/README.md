# 01-Foundations Overview

## Purpose

This section introduces the fundamental concepts of AI integration, progressing from basic LLM API calls to stateful conversational agents. It provides the building blocks for all advanced patterns that follow.

## Prerequisites

- Python 3.12.10 (via pyenv)
- Anthropic API key in environment

## Quick Start

```bash
# Test LangChain integration
python 01-foundations/langchain/basic_example.py

# Run LangGraph chatbot in interactive mode (default)
python 01-foundations/langgraph/basic_chatbot.py

# Run LangGraph chatbot in demo mode
python 01-foundations/langgraph/basic_chatbot.py --demo

# Run single query
python 01-foundations/langgraph/basic_chatbot.py "Can you show me how to get historical weather data for the past month?"
```

## Architecture Overview

```
01-foundations/
├── langchain/       # Direct LLM integration
│   └── basic_example.py
└── langgraph/       # Stateful agent framework
    └── basic_chatbot.py  # Supports interactive, demo, and single-query modes
```

## Learning Path

1. **LangChain** - Learn how to make direct API calls to Claude
   - Simple, stateless interactions
   - Basic prompt engineering
   - Response handling

2. **LangGraph** - Introduction to stateful agents
   - Graph-based conversation flow
   - State management
   - Interactive and non-interactive patterns

## Key Concepts

### LangChain: Direct LLM Integration

LangChain provides a straightforward abstraction for LLM interactions. For those familiar with LangChain, this is a minimal refresher on Claude integration.

#### Quick Reference
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

model = ChatAnthropic(model="claude-3-5-sonnet-20241022")
response = model.invoke([HumanMessage(content="Your question")])
```

#### Key Points
- **Purpose**: Simple API wrapper for Claude
- **Use Case**: One-shot queries, simple integrations  
- **Architecture**: Request → LangChain → Claude API → Response
- **Message Types**: HumanMessage, AIMessage, SystemMessage
- **Best For**: Prototyping, single-turn Q&A, batch processing

For stateful conversations and complex workflows, use LangGraph instead.

### LangGraph: Stateful Agents
- **Purpose**: Build conversational agents with memory
- **Use Case**: Multi-turn conversations, complex workflows
- **Architecture**: State → Graph → Nodes → Edges → State'

## LangGraph Architecture Deep Dive

LangGraph introduces a graph-based approach to building AI agents, where conversation flow is modeled as state transitions through a directed graph. This enables complex, stateful interactions that go beyond simple request-response patterns.

### Core Architecture

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       v
┌─────────────┐     ┌─────────────┐
│   State     │<--->│   Graph     │
│  (Messages) │     │  Definition │
└──────┬──────┘     └─────────────┘
       │                    |
       v                    v
┌─────────────┐     ┌─────────────┐
│    Node     │     │    Edge     │
│  (Chatbot)  │     │   (Flow)    │
└──────┬──────┘     └─────────────┘
       │
       v
┌─────────────┐
│     END     │
└─────────────┘
```

### Key LangGraph Concepts

#### State Management
- **TypedDict**: Defines the shape of conversation state
- **Messages**: List of conversation history
- **Persistence**: State maintained across interactions

#### Graph Components
- **Nodes**: Processing units (e.g., chatbot function)
- **Edges**: Define flow between nodes
- **Conditional Edges**: Dynamic routing based on state

#### Execution Model
- **Checkpointing**: Save and restore conversation state
- **Streaming**: Real-time response generation
- **Interruption**: Pause and resume workflows

### Implementation Patterns

#### Basic Chatbot Pattern
```python
# Define state
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Create graph
graph = StateGraph(State)
graph.add_node("chatbot", chatbot_node)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)
```

#### Execution Modes in basic_chatbot.py

1. **Interactive Mode** (default):
   - Maintains conversation loop
   - Handles user input with quit commands
   - Preserves context across turns

2. **Demo Mode** (`--demo` flag):
   - Runs predefined weather-related queries
   - Shows AI capabilities automatically
   - Useful for testing and demonstrations

3. **Single Query Mode** (with arguments):
   - Command-line interface for one-off questions
   - Stateless operation
   - Quick answers without interaction

### Advantages Over Direct LLM Calls

1. **State Management**: Automatic conversation history
2. **Flow Control**: Complex routing and branching
3. **Extensibility**: Easy to add tools and capabilities
4. **Debugging**: Visualizable execution flow
5. **Checkpointing**: Save/resume conversations

### Use Cases

Ideal for:
- Multi-turn conversations
- Workflow automation
- Tool-using agents
- Complex decision trees
- Stateful applications

### Graph Visualization

LangGraph can visualize execution flow:
```
START -> chatbot -> END
```

This becomes more valuable with complex graphs involving tools and conditional routing.

## Next Steps

After mastering these foundations, proceed to:
- **02-domain-applications**: Apply AI to real-world weather and agriculture problems
- **03-tools-integration**: Add computational capabilities to your agents