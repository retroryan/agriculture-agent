# AI Weather Intelligence: A Progressive Tutorial

> **📋 See a live demo in action: [sample_multi-turn-demo-output.md](sample_multi-turn-demo-output.md)**

## Key Insight

**This project is actually a tutorial disguised as a weather application.** It teaches AI architecture patterns through progressive complexity, where each stage solves real limitations of the previous approach.

## Project Learning Path

Learn AI development through four progressive stages:

1. **01-foundations** - Validate LangChain setup and introduce LangGraph
2. **02-domain-applications** - Build real-world weather analysis with AI
3. **03-tools-integration** - Add dynamic capabilities with tools
4. **04-mcp-architecture** - Create distributed, production-ready systems

Each stage builds on the previous, revealing limitations and introducing solutions.

## Quick Start

```bash
# Setup
pyenv local 3.12.10
pip install -r requirements.txt
echo 'ANTHROPIC_API_KEY=your-key-here' > .env

# Run each stage
python 01-foundations/langgraph/basic_chatbot.py              # Stage 1
python 02-domain-applications/main.py --demo                  # Stage 2
python 03-tools-integration/main.py                           # Stage 3
python 04-mcp-architecture/main.py --demo                     # Stage 4
```

## Stage 1: Foundations

**Purpose**: Validate your environment and learn stateful AI patterns

**Quick Test**:
```bash
# Validate LangChain
python 01-foundations/langchain/basic_example.py

# Interactive chatbot
python 01-foundations/langgraph/basic_chatbot.py

# Single query
python 01-foundations/langgraph/basic_chatbot.py "What's the weather forecast?"
```

**Key Takeaways**: Stateful agents vs stateless API calls

[→ Detailed Overview](01-foundations/OVERVIEW.md) | [→ Tutorial](tutorials/01-getting-started.md)

## Stage 2: Domain Applications

**Purpose**: Apply AI to real weather and agricultural problems

**Quick Test**:
```bash
# Interactive agricultural advisor
python 02-domain-applications/main.py

# Demo mode with examples
python 02-domain-applications/main.py --demo

# Single agricultural query
python 02-domain-applications/main.py --query "Is it too dry for corn in Iowa?"
```

**Key Takeaways**: Traditional AI patterns and their limitations

[→ Detailed Overview](02-domain-applications/OVERVIEW.md) | [→ Tutorial](tutorials/02-weather-domain.md)

## Stage 3: Tools Integration

**Purpose**: Transform static workflows into dynamic agents with tools

**Quick Test**:
```bash
# Basic tools (math, text, dates)
python 03-tools-integration/basic_tools/chatbot_with_tools.py

# External tools (web fetching)
python 03-tools-integration/external_tools/chatbot_with_fetch.py

# Tool chaining demo
python 03-tools-integration/main.py
```

**Key Takeaways**: Tools as capabilities, dynamic decision-making

[→ Detailed Overview](03-tools-integration/OVERVIEW.md) | [→ Tutorial](tutorials/03-building-agents.md)

## Stage 4: MCP Architecture

**Purpose**: Introduction to distributed AI systems and the MCP paradigm - a foundational step towards production-ready architectures

**Quick Test**:
```bash
# Test complete system
python 04-mcp-architecture/mcp_servers/test_mcp.py

# Interactive mode (default)
python 04-mcp-architecture/main.py

# Demo mode with examples
python 04-mcp-architecture/main.py --demo

# Multi-turn demo scenarios
python 04-mcp-architecture/weather_agent/demo_scenarios.py
```

**Key Takeaways**: MCP fundamentals, distributed tool concepts, stepping stone to production systems

[→ Detailed Overview](04-mcp-architecture/OVERVIEW.md) | [→ Tutorial](tutorials/04-distributed-tools.md)

## Architecture Evolution

```
Stage 1: Basic Chatbot
├── Simple state management
└── Conversational memory

Stage 2: Domain Application  
├── Direct API integration
├── Query classification
└── Static workflows

Stage 3: Agent with Tools
├── Dynamic tool selection
├── Capability extension
└── Flexible responses

Stage 4: MCP Introduction
├── MCP protocol basics
├── Process-isolated tools
├── Distributed architecture concepts
└── Foundation for production systems
```

## Key Technologies

- **LangChain/LangGraph**: AI application framework
- **Claude (Anthropic)**: Advanced language model
- **OpenMeteo API**: Free weather data (no auth required)
- **MCP (Model Context Protocol)**: Distributed tool architecture

## Environment Setup

```bash
# Python version
pyenv local 3.12.10

# Install dependencies
pip install -r requirements.txt

# Configure API key
export ANTHROPIC_API_KEY="your-claude-api-key"
```

## Tutorial Progression

1. [**Getting Started**](tutorials/01-getting-started.md) - Environment validation and foundations
2. [**Weather Domain**](tutorials/02-weather-domain.md) - Real-world AI applications
3. [**Building Agents**](tutorials/03-building-agents.md) - Dynamic tools and capabilities
4. [**Distributed Tools**](tutorials/04-distributed-tools.md) - Production architecture with MCP

## Project Structure

```
weatherdata/
├── 01-foundations/          # Basic LangChain/LangGraph patterns
├── 02-domain-applications/  # Weather and agricultural AI
├── 03-tools-integration/    # Dynamic agent capabilities
├── 04-mcp-architecture/     # Distributed tool systems
└── tutorials/              # Progressive learning guides
```

## Running Tests

Each stage includes comprehensive tests:

```bash
# Stage 2: Domain applications
python 02-domain-applications/main.py --demo

# Stage 3: Tool integration
python 03-tools-integration/main.py

# Stage 4: MCP architecture
python 04-mcp-architecture/mcp_servers/test_mcp.py
```

## Key Concepts by Stage

| Stage | Concept | Implementation |
|-------|---------|----------------|
| 1 | Stateful Agents | LangGraph StateGraph |
| 2 | Domain AI | Query classification + API integration |
| 3 | Dynamic Tools | @tool decorator + conditional routing |
| 4 | MCP Fundamentals | Process isolation + distributed tool patterns |

## Quick Command Reference

```bash
# Interactive modes
python 01-foundations/langgraph/basic_chatbot.py              # Basic chat
python 02-domain-applications/main.py                         # Agricultural advisor
python 03-tools-integration/basic_tools/chatbot_with_tools.py # Tool-enabled chat

# Demo modes
python 01-foundations/langgraph/basic_chatbot.py --demo       # LangGraph examples
python 02-domain-applications/main.py --demo                  # Agricultural scenarios
python 04-mcp-architecture/main.py --demo                     # MCP demonstration

# Single queries
python 01-foundations/langgraph/basic_chatbot.py "Question?"
python 02-domain-applications/main.py --query "Agricultural question?"
```

## Next Steps

1. Start with [01-getting-started.md](tutorials/01-getting-started.md)
2. Run each stage's examples
3. Read the OVERVIEW.md in each directory for architecture details
4. Experiment with modifications
5. Build your own domain-specific AI application

## Additional Resources

- [LangGraph Tutorial](langgraph-tutorial.md) - Original comprehensive guide
- [Advanced Patterns](advanced-langgraph-tutorial.md) - Deep dive into complex scenarios
- [Claude Documentation](CLAUDE.md) - Project-specific Claude integration notes

---

Remember: This is a learning journey. Each stage prepares you for the next. By the end, you'll understand how to build production AI systems that scale.