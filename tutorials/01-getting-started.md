# Getting Started: AI Weather Intelligence Foundations

## Key Insight

**This project is actually a tutorial disguised as a weather application.** It teaches AI architecture patterns through progressive complexity, where each stage solves real limitations of the previous approach. The documentation guides you through this journey, not just documents the final system.

## What You'll Build

You're about to explore how AI transforms weather data into actionable insights. This isn't just another tutorial - it's your path from basic API calls to intelligent agricultural analysis.

The examples validate that your environment works and demonstrate the core patterns you'll use throughout this project.

## The Learning Journey

This project follows a deliberate progression from basic API testing to sophisticated multi-agent systems:

1. **01-foundations** - Foundation & API validation (you are here)
2. **02-domain-applications** - Traditional application patterns with direct workflows  
3. **03-tools-integration** - Dynamic agents with computational capabilities
4. **04-mcp-architecture** - Distributed, production-ready intelligent systems

Each stage reveals limitations that the next stage solves.

## Prerequisites

**Experience**: You already know LangChain. This is just validation and a brief LangGraph introduction.

**Setup**: Two minutes to get running:

```bash
# Python version management
pyenv local 3.12.10
pip install -r requirements.txt

# Add your Claude API key
echo 'ANTHROPIC_API_KEY=your-key-here' > .env
```

That's it. No complex configurations.

## The Learning Path

**01-foundations** validates two essential patterns:

1. **LangChain**: Direct LLM integration - the foundation you know
2. **LangGraph**: Stateful agents - the upgrade you need

## Quick Validation

Run everything to confirm your setup works:

```bash
# Test LangChain (30 seconds)
python 01-foundations/langchain/basic_example.py

# Test LangGraph interactively
python 01-foundations/langgraph/basic_chatbot.py

# Test single queries
python 01-foundations/langgraph/basic_chatbot.py "What's the weather pattern for corn planting season?"
```

If these run without errors, you're ready for the real work.

## LangChain Review: The Pattern You Know

**File**: `01-foundations/langchain/basic_example.py`

Classic LangChain in 10 lines:

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

model = ChatAnthropic(model="claude-3-5-sonnet-20241022")
response = model.invoke([HumanMessage(content="Analyze crop conditions")])
```

**Why start here?** Because complex agricultural AI starts with simple, reliable LLM calls. This pattern handles:
- Weather analysis requests
- Crop advisory queries  
- Data interpretation tasks

**When to use this pattern:**
- One-shot analysis
- Batch processing weather data
- Simple Q&A interfaces

**The limitation:** No memory. No context. No conversation flow.

That's why you need LangGraph.

## LangGraph: The Stateful Upgrade

**File**: `01-foundations/langgraph/basic_chatbot.py`

LangGraph treats conversations as state machines. Instead of isolated requests, you get persistent context and flow control.

### The Core Pattern

```python
# State definition
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Graph construction  
graph = StateGraph(State)
graph.add_node("chatbot", chatbot_node)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)
```

### Three Ways to Run It

**Interactive Mode** (default):
```bash
python 01-foundations/langgraph/basic_chatbot.py
```
Maintains conversation context. Ask follow-up questions about weather patterns, crop conditions, or agricultural recommendations.

**Demo Mode**:
```bash  
python 01-foundations/langgraph/basic_chatbot.py --demo
```
Runs predefined agricultural queries automatically. Perfect for showing stakeholders what's possible.

**Single Query**:
```bash
python 01-foundations/langgraph/basic_chatbot.py "Is soil moisture adequate for planting in Iowa?"
```
Command-line interface for integration with other tools.

### Why This Matters

Weather and agriculture require context:
- "How does this compare to last week?"
- "Based on the rainfall you mentioned, should I irrigate?"
- "What about frost risk for the crops we discussed?"

LangGraph remembers. LangChain doesn't.

## The Architecture Difference

**LangChain Flow:**
```
Question → Claude → Answer
```

**LangGraph Flow:**  
```
Question → State → Node → Edge → Updated State → Answer
```

The state persistence enables:
- Multi-turn agricultural consultations
- Context-aware weather analysis
- Progressive data exploration

## What You've Accomplished

In 5 minutes, you've validated:
- ✅ Environment configuration
- ✅ Claude API integration  
- ✅ Basic LangChain patterns
- ✅ Stateful LangGraph agents
- ✅ Multiple execution modes

## Next Steps

Now that foundations work, you're ready for real-world applications:

**02-domain-applications** - Apply AI to weather and agriculture data
```bash
python 02-domain-applications/main.py --demo
```

**03-tools-integration** - Add computational capabilities  
```bash
python 03-tools-integration/main.py
```

**04-mcp-architecture** - Build distributed AI systems
```bash
python 04-mcp-architecture/examples/quick_demo.py
```

## Key Takeaways

- **LangChain**: Perfect for stateless analysis
- **LangGraph**: Essential for conversational AI
- **State Management**: The key to meaningful agricultural AI
- **Multiple Interfaces**: Interactive, demo, and programmatic access

The foundations are simple. The applications are powerful.

Time to build something that helps farmers make better decisions.