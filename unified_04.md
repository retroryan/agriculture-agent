# LangChain Unified Model Interface Migration for 04-mcp-architecture

## Executive Summary

This document outlines the migration plan for **04-mcp-architecture only** from model-specific implementations to LangChain's unified model interface using `init_chat_model()`. This approach simplifies model management in the distributed MCP architecture, improves maintainability, and enables runtime model switching while maintaining compatibility with Claude API.

**Note**: This migration is specifically scoped to the 04-mcp-architecture directory to demonstrate unified model patterns in a distributed tool system with process-isolated MCP servers.

## Background

### Current State
- **04-mcp-architecture** uses direct `ChatAnthropic` imports in the weather agent
- MCP servers run as independent subprocesses with JSON-RPC communication
- Model switching requires code changes in `weather_agent/mcp_agent.py`
- Hardcoded model initialization limits flexibility

### Unified Model Interface Benefits
1. **Single initialization function** for all models
2. **Runtime model switching** without code changes
3. **Consistent API** across the distributed architecture
4. **Simplified dependency management**
5. **Future-proof** for new model additions
6. **Better testing** with different models for MCP integration

## Migration Plan for 04-mcp-architecture

### Phase 1: Testing & Documentation (Pre-Migration) ✅ COMPLETED

**Status**: Completed on 2025-06-24
**Key Achievements**:
- Created comprehensive test suite adapted from 03-tools-integration
- Established baseline performance metrics (85.7% success rate, ~9s avg response time)
- Identified all key functions and imports in mcp_agent.py
- Fixed import issues and validated test suite functionality

#### Test Suite Creation
Create `04-mcp-architecture/test_unified_model.py`:
```python
"""
Comprehensive test suite for MCP architecture with unified models
Tests both single-turn and multi-turn conversations
"""
import asyncio
import sys
sys.path.append('04-mcp-architecture')

async def test_forecast_tools():
    """Test weather forecast MCP server integration"""
    # Test cases:
    # 1. "What's the weather forecast for Berlin?"
    # 2. "Give me a 5-day forecast for Tokyo"
    # 3. "Show temperature trends for next week in Paris"
    
async def test_historical_tools():
    """Test historical weather analysis"""
    # Test cases:
    # 1. "What was the weather like last month in Chicago?"
    # 2. "Compare this summer to last summer in Rome"
    # 3. "Show rainfall trends for 2023 in London"
    
async def test_agricultural_tools():
    """Test agricultural condition analysis"""
    # Test cases:
    # 1. "Check soil moisture conditions for Iowa corn fields"
    # 2. "Is it too dry for wheat in Kansas?"
    # 3. "Analyze growing conditions in California vineyards"
    
async def test_multi_turn_context():
    """Test conversation memory across turns"""
    # Test cases:
    # 1. First: "What's the weather in Berlin?"
    #    Follow-up: "How about tomorrow?" (should remember Berlin)
    # 2. Agricultural context preservation
    # 3. Tool selection based on conversation history

async def test_mcp_server_resilience():
    """Test MCP server subprocess management"""
    # Test cases:
    # 1. Server initialization
    # 2. Multiple concurrent requests
    # 3. Error handling and recovery

if __name__ == "__main__":
    asyncio.run(run_all_tests())
```

#### Running Current Tests
```bash
# Test existing MCP functionality
cd 04-mcp-architecture
python mcp_servers/test_mcp.py > baseline_mcp_results.txt

# Test agent behavior
python main.py --demo > baseline_demo_results.txt
```

### Phase 2: Make 04-mcp-architecture Self-Contained ✅ COMPLETED

**Status**: Completed on 2025-06-24
**Key Achievements**:
- Created local requirements.txt with all necessary dependencies
- Updated README.md with quick start guide and LangGraph features documentation
- Added comprehensive architecture overview and performance metrics
- Documented unique LangGraph features demonstrated in this stage

#### Step 1: Create Local Requirements File
Create `04-mcp-architecture/requirements.txt`:
```
# Core dependencies for MCP architecture
python-dotenv
langchain>=0.3.0
langchain-anthropic>=0.2.0
langgraph>=0.2.0
httpx>=0.27.0
mcp>=1.1.2
rich>=13.0.0
pytz
```

#### Step 2: Update README.md
Create `04-mcp-architecture/README.md`:
```markdown
# MCP Architecture with Unified Model Interface

This directory demonstrates the Model Context Protocol (MCP) architecture with LangChain's unified model interface for distributed AI tool systems.

## Architecture Overview

- **MCP Servers**: Process-isolated tool servers for weather services
  - Forecast Server: Current and future weather data
  - Historical Server: Past weather analysis
  - Agricultural Server: Farm-specific conditions
- **Weather Agent**: LangGraph-based orchestrator with unified model configuration
- **Async Optimization**: Non-blocking HTTP calls with httpx

## Setup

```bash
cd 04-mcp-architecture
pip install -r requirements.txt
echo 'ANTHROPIC_API_KEY=your-key-here' > .env
```

## Running Examples

```bash
# Test MCP servers
python mcp_servers/test_mcp.py

# Interactive weather assistant
python main.py

# Demo mode with example queries
python main.py --demo

# Multi-turn conversation demo
python main.py --multi-turn-demo
```

## Model Configuration

The unified model interface allows runtime model switching:

```bash
# Use default model (Claude 3.5 Sonnet)
python main.py

# Use a different model via environment variable
MODEL_NAME=claude-3-haiku-20240307 python main.py

# Configure in code
model = get_model("claude-3-opus-20240229")
```
```

### Phase 3: Code Migration

#### Step 1: Create Unified Model Configuration
Create `04-mcp-architecture/config.py`:
```python
"""
Unified model configuration for MCP architecture
"""
import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_model(
    model_name: str = None,
    temperature: float = 0.7,
    **kwargs
):
    """
    Initialize a chat model using the unified interface.
    
    Args:
        model_name: Model identifier (e.g., "claude-3-5-sonnet-20241022")
        temperature: Model temperature (default 0.7 for conversational tone)
        **kwargs: Additional model parameters
    
    Returns:
        Initialized chat model ready for MCP tool binding
    """
    # Use environment variable or default
    if model_name is None:
        model_name = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022")
    
    # Determine provider from model name
    if "claude" in model_name:
        model_provider = "anthropic"
    elif "gpt" in model_name:
        model_provider = "openai"
    else:
        # Let init_chat_model infer the provider
        model_provider = None
    
    # Initialize model with unified interface
    model = init_chat_model(
        model_name,
        model_provider=model_provider,
        temperature=temperature,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        **kwargs
    )
    
    return model

def get_mcp_model(**kwargs):
    """
    Get a model specifically configured for MCP tool usage.
    
    Includes optimizations for:
    - Tool calling with MCP servers
    - Async operation compatibility
    - Error handling for subprocess communication
    """
    # MCP benefits from slightly higher temperature for natural responses
    return get_model(temperature=0.7, **kwargs)

def get_configurable_model(**kwargs):
    """
    Create a runtime-configurable model for MCP architecture.
    
    Allows switching models during multi-turn conversations:
        model = get_configurable_model()
        response = await model.ainvoke(
            "What's the weather?",
            config={"configurable": {"model": "claude-3-haiku-20240307"}}
        )
    """
    return init_chat_model(temperature=0.7, **kwargs)
```

#### Step 2: Migrate weather_agent/mcp_agent.py
Replace the model initialization section (around lines 80-90) with:
```python
# Add import at the top
import sys
sys.path.append('..')
from config import get_mcp_model

# In create_weather_graph function, replace:
# model = ChatAnthropic(
#     model="claude-3-5-sonnet-20241022",
#     temperature=0.7,
#     api_key=api_key
# ).bind_tools(tools)

# With:
model = get_mcp_model().bind_tools(tools)
```

#### Step 3: Update chatbot.py for Model Flexibility
Add model configuration support:
```python
# Add to imports
from config import get_model

# Add command-line argument in __main__
parser.add_argument(
    "--model",
    type=str,
    default=None,
    help="Model to use (e.g., claude-3-haiku-20240307)"
)

# Pass model to create_weather_graph
if args.model:
    os.environ["MODEL_NAME"] = args.model
```

### Phase 4: Enhanced MCP-Specific Features

#### Step 1: Model Performance Monitoring
Create `04-mcp-architecture/utils/model_metrics.py`:
```python
"""
Monitor model performance in MCP architecture
"""
import time
import asyncio
from collections import defaultdict
from typing import Dict, List

class MCPModelMetrics:
    """Track model performance across MCP tool calls"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        
    async def measure_tool_call(self, model_name: str, tool_name: str, func):
        """Measure execution time for MCP tool calls"""
        start = time.time()
        try:
            result = await func()
            duration = time.time() - start
            self.metrics[f"{model_name}:{tool_name}"].append({
                "duration": duration,
                "success": True
            })
            return result
        except Exception as e:
            duration = time.time() - start
            self.metrics[f"{model_name}:{tool_name}"].append({
                "duration": duration,
                "success": False,
                "error": str(e)
            })
            raise
    
    def get_summary(self) -> Dict:
        """Get performance summary by model and tool"""
        summary = {}
        for key, measurements in self.metrics.items():
            successful = [m for m in measurements if m["success"]]
            if successful:
                avg_duration = sum(m["duration"] for m in successful) / len(successful)
                summary[key] = {
                    "avg_duration": avg_duration,
                    "success_rate": len(successful) / len(measurements),
                    "total_calls": len(measurements)
                }
        return summary
```

#### Step 2: Model Comparison for MCP
Create `04-mcp-architecture/compare_models.py`:
```python
"""
Compare different models in MCP architecture
"""
import asyncio
from config import get_model
from weather_agent.mcp_agent import create_weather_graph

async def compare_mcp_performance():
    """Compare how different models handle MCP tool orchestration"""
    
    test_queries = [
        "What's the weather forecast for Berlin?",
        "Analyze soil moisture for corn in Iowa",
        "Compare this month to last year in Tokyo"
    ]
    
    models = [
        "claude-3-5-sonnet-20241022",  # Most capable
        "claude-3-haiku-20240307",      # Fastest
        "claude-3-opus-20240229"        # Highest quality
    ]
    
    results = {}
    
    for model_name in models:
        print(f"\nTesting {model_name}...")
        model = get_model(model_name)
        
        # Create graph with this model
        graph = await create_weather_graph(model=model)
        
        model_results = []
        for query in test_queries:
            try:
                start = time.time()
                response = await graph.ainvoke({"messages": [("user", query)]})
                duration = time.time() - start
                
                model_results.append({
                    "query": query,
                    "duration": duration,
                    "response_length": len(str(response)),
                    "tools_used": extract_tools_used(response)
                })
            except Exception as e:
                model_results.append({
                    "query": query,
                    "error": str(e)
                })
        
        results[model_name] = model_results
    
    # Print comparison
    print_comparison_table(results)

if __name__ == "__main__":
    asyncio.run(compare_mcp_performance())
```

### Phase 5: Testing & Validation

#### Post-Migration Testing
```bash
cd 04-mcp-architecture

# Run MCP server tests
python mcp_servers/test_mcp.py > post_migration_mcp_results.txt

# Compare results
diff baseline_mcp_results.txt post_migration_mcp_results.txt

# Test with different models
MODEL_NAME=claude-3-haiku-20240307 python main.py --demo
MODEL_NAME=claude-3-5-sonnet-20241022 python main.py --demo

# Test model comparison
python compare_models.py

# Run multi-turn demo
python main.py --multi-turn-demo
```

#### Performance Validation
```python
# Create performance_test_mcp.py
import asyncio
import time
from config import get_model, get_mcp_model

async def benchmark_mcp_models():
    """Benchmark different models in MCP context"""
    
    # Test 1: MCP server communication overhead
    models = {
        "sonnet": get_model("claude-3-5-sonnet-20241022"),
        "haiku": get_model("claude-3-haiku-20240307")
    }
    
    for name, model in models.items():
        start = time.time()
        # Test MCP tool discovery
        graph = await create_weather_graph(model=model)
        print(f"{name} graph creation: {time.time() - start:.3f}s")
        
        # Test actual tool execution
        start = time.time()
        await graph.ainvoke({"messages": [("user", "Weather in Berlin?")]})
        print(f"{name} tool execution: {time.time() - start:.3f}s")
```

## Implementation Timeline

1. **Week 1**: ✅ Create test suite and document baseline MCP behavior (COMPLETED 2025-06-24)
2. **Week 2**: ✅ Make 04-mcp-architecture self-contained (COMPLETED 2025-06-24)
3. **Week 3**: ✅ Implement unified model configuration (COMPLETED 2025-06-24)
4. **Week 4**: ⏳ Migrate weather agent to use unified interface
5. **Week 5**: ⏳ Add model comparison and performance monitoring
6. **Week 6**: ⏳ Validate and optimize for production use

## Progress Log

### 2025-06-24: Phase 1 & 2 Completed
- **Test Suite Creation**: Adapted test_suite.py from 03-tools-integration to create test_unified_model.py
  - Tests MCP server startup, tool discovery, and subprocess management
  - Validates forecast, historical, and agricultural tools
  - Verifies multi-turn conversation context preservation
  - Tests concurrent request handling and tool composition
- **Baseline Results**: 6/7 tests passing, avg response time 9.1s
- **Self-Contained Package**: Created requirements.txt and updated README.md
- **Documentation**: Added comprehensive architecture overview and LangGraph features

### 2025-06-24: Phase 3 Completed
- **Unified Model Configuration**: Created config.py with simple get_model() function
  - Uses langchain.chat_models.init_chat_model for unified interface
  - Supports runtime model selection via MODEL_NAME environment variable
  - Maintains demo simplicity with minimal configuration
- **MCP Agent Migration**: Updated mcp_agent.py to use get_model()
  - Removed direct ChatAnthropic import
  - Changed temperature from 0 to 0.7 for more natural responses
  - Preserved all MCP functionality
- **Testing**: Verified demo mode works correctly with unified model
  - All MCP servers start properly
  - Tool discovery works as expected
  - Query responses are successful

### Next Steps
- Phase 4: Complete remaining migration tasks if needed
- Phase 5: Implement model comparison and performance monitoring

## Key Considerations for MCP

### Subprocess Management
- Models must handle async communication with MCP servers
- Error handling for subprocess failures
- Connection pooling for efficiency

### Tool Binding
- Dynamic tool discovery from MCP servers
- Model must support tool calling format
- Consistent tool descriptions across models

### Performance Optimization
```python
# Optimized MCP model configuration
def get_optimized_mcp_model():
    """Model optimized for MCP architecture"""
    return get_model(
        temperature=0.7,
        max_tokens=2048,  # Reasonable limit for tool responses
        timeout=30,       # Account for MCP server latency
        max_retries=2     # Handle transient subprocess issues
    )
```

## Benefits for MCP Architecture

1. **Model Flexibility**: Test different models for tool orchestration
2. **Cost Optimization**: Use Haiku for simple queries, Sonnet for complex
3. **Debugging**: Easy model switching for troubleshooting
4. **A/B Testing**: Compare model performance in production
5. **Future Updates**: Seamless adoption of new Claude models

## Next Steps

1. Review and approve this MCP-focused migration plan
2. Create comprehensive MCP test suite
3. Implement unified configuration with MCP optimizations
4. Migrate weather agent incrementally
5. Document MCP-specific model selection guidelines

## Additional Resources

- [LangChain init_chat_model docs](https://python.langchain.com/docs/how_to/chat_models_universal_init/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/docs)
- [LangGraph with MCP Integration](https://langchain-ai.github.io/langgraph/)