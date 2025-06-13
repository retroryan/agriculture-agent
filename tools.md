# LangGraph with Claude Tool Use: Complete Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Setup and Installation](#setup-and-installation)
3. [Understanding Tool Use](#understanding-tool-use)
4. [Creating Tools](#creating-tools)
5. [Building Agents with LangGraph](#building-agents-with-langgraph)
6. [Advanced Patterns](#advanced-patterns)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Complete Examples](#complete-examples)

## Introduction

LangGraph is a powerful framework for building stateful, multi-actor applications with Large Language Models (LLMs). When combined with Claude's native tool-calling capabilities, it enables the creation of sophisticated AI agents that can interact with external systems, perform calculations, fetch data, and execute complex workflows.

### Key Benefits
- **Native Tool Support**: Claude models have built-in support for function calling
- **Stateful Workflows**: LangGraph manages conversation state and execution flow
- **Flexible Architecture**: Build anything from simple tools to complex multi-agent systems
- **Production Ready**: Built-in error handling, streaming, and deployment support

## Setup and Installation

### Prerequisites
```bash
# Core dependencies
pip install langchain langchain-anthropic langgraph

# Optional dependencies for specific use cases
pip install langchain-community  # For additional tools
pip install langgraph-checkpoint  # For persistence
pip install python-dotenv  # For environment management
```

### Environment Configuration
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Set your Anthropic API key
os.environ["ANTHROPIC_API_KEY"] = "your-api-key-here"
```

## Understanding Tool Use

Claude's tool use allows the model to:
1. Understand when a tool should be called
2. Extract the necessary parameters from user input
3. Format the tool call correctly
4. Interpret the tool's response
5. Integrate the result into its response

### Tool Call Flow
```
User Input → Claude analyzes → Decides to use tool → Extracts parameters 
    ↓                                                        ↓
Response ← Claude integrates result ← Tool returns result ← Tool executes
```

## Creating Tools

### Method 1: Using Pydantic Models (Recommended)
```python
from pydantic import BaseModel, Field
from typing import Optional

class WeatherTool(BaseModel):
    """Get the current weather for a location"""
    location: str = Field(description="The city and state, e.g., San Francisco, CA")
    unit: Optional[str] = Field(default="fahrenheit", description="Temperature unit")

class CalculatorTool(BaseModel):
    """Perform mathematical calculations"""
    operation: str = Field(description="The operation: add, subtract, multiply, divide")
    a: float = Field(description="First number")
    b: float = Field(description="Second number")
```


## Building Agents with LangGraph

### Simple ReAct Agent
```python
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

# Initialize Claude model
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0,
    max_tokens=4096
)

# Create agent with tools
agent = create_react_agent(
    model=llm,
    tools=[search_web, get_current_time, multiply],
    state_modifier="You are a helpful assistant that can search the web, tell time, and do math."
)

# Use the agent
response = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in Tokyo and what time is it there?"}]
})
```

### Custom Agent with State Management
```python
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    context: dict  # Custom context for our agent

def create_custom_agent(llm, tools):
    # Create tool node
    tool_node = ToolNode(tools)
    
    # Initialize graph
    workflow = StateGraph(AgentState)
    
    # Define the agent node
    def agent_node(state: AgentState):
        messages = state["messages"]
        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Define conditional edge
    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "__end__"
    
    # Add edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    # Compile
    return workflow.compile()
```

## Advanced Patterns

### Multi-Tool Agent with Specialized Capabilities
```python
from typing import List, Dict, Any
import json

class MultiToolAgent:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.tools = self._create_tools()
        self.agent = self._build_agent()
    
    def _create_tools(self):
        @tool
        def analyze_data(data: str, analysis_type: str) -> str:
            """Analyze data with specified analysis type"""
            # Mock implementation
            return f"Analysis of type {analysis_type} completed on data"
        
        @tool
        def generate_report(title: str, sections: List[str]) -> str:
            """Generate a structured report"""
            report = f"# {title}\n\n"
            for i, section in enumerate(sections, 1):
                report += f"## Section {i}: {section}\n\n"
            return report
        
        @tool
        def execute_code(code: str, language: str = "python") -> str:
            """Execute code safely (mock implementation)"""
            if language == "python":
                # In production, use proper sandboxing
                return f"Code executed successfully"
            return f"Language {language} not supported"
        
        return [analyze_data, generate_report, execute_code]
    
    def _build_agent(self):
        return create_react_agent(
            model=self.llm,
            tools=self.tools,
            state_modifier="""You are an advanced AI assistant capable of:
            1. Analyzing complex data
            2. Generating structured reports
            3. Writing and explaining code
            Always break down complex tasks into steps and use tools appropriately."""
        )
```

### Agent with Memory and Persistence
```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START

def create_persistent_agent(llm, tools):
    # Create memory saver
    memory = MemorySaver()
    
    workflow = StateGraph(AgentState)
    
    def agent_with_memory(state: AgentState):
        # Access previous conversations from state
        messages = state["messages"]
        context = state.get("context", {})
        
        # Add context to the prompt if needed
        if context:
            system_message = f"Previous context: {json.dumps(context)}"
            messages = [{"role": "system", "content": system_message}] + messages
        
        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke(messages)
        
        # Update context based on conversation
        new_context = context.copy()
        # Add logic to update context
        
        return {
            "messages": [response],
            "context": new_context
        }
    
    # Build the graph
    tool_node = ToolNode(tools)
    workflow.add_node("agent", agent_with_memory)
    workflow.add_node("tools", tool_node)
    
    # Add conditional routing
    def route_tools(state: AgentState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "__end__"
    
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", route_tools)
    workflow.add_edge("tools", "agent")
    
    # Compile with memory
    return workflow.compile(checkpointer=memory)
```

### Parallel Tool Execution
```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

class ParallelToolAgent:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    async def execute_tools_parallel(self, tool_calls):
        """Execute multiple tool calls in parallel"""
        tasks = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["arguments"]
            
            # Create async task for each tool
            task = asyncio.create_task(
                self._execute_tool_async(tool_name, tool_args)
            )
            tasks.append(task)
        
        # Wait for all tools to complete
        results = await asyncio.gather(*tasks)
        return results
    
    async def _execute_tool_async(self, tool_name, args):
        """Execute a single tool asynchronously"""
        # Tool execution logic here
        return f"Result from {tool_name}"
```

## Error Handling

### Robust Tool Error Handling
```python
from langchain_core.tools import ToolException
from langgraph.prebuilt import ToolNode

@tool
def safe_calculator(operation: str, a: float, b: float) -> float:
    """Safely perform mathematical operations"""
    try:
        if operation == "divide" and b == 0:
            raise ToolException("Cannot divide by zero")
        
        operations = {
            "add": a + b,
            "subtract": a - b,
            "multiply": a * b,
            "divide": a / b
        }
        
        if operation not in operations:
            raise ToolException(f"Unknown operation: {operation}")
        
        return operations[operation]
    
    except ToolException:
        raise
    except Exception as e:
        raise ToolException(f"Calculation error: {str(e)}")

# Configure error handling in ToolNode
tool_node = ToolNode(
    [safe_calculator],
    handle_tool_errors=True  # Automatically handle errors
)

# Custom error handling
def custom_error_handler(error: Exception) -> str:
    """Custom error message for the LLM"""
    if isinstance(error, ToolException):
        return f"Tool error: {str(error)}. Please try a different approach."
    return f"Unexpected error: {str(error)}"

tool_node_custom = ToolNode(
    [safe_calculator],
    handle_tool_errors=custom_error_handler
)
```

### Agent-Level Error Recovery
```python
def create_resilient_agent(llm, tools, max_retries=3):
    """Create an agent that can recover from errors"""
    
    workflow = StateGraph(AgentState)
    
    def agent_with_retry(state: AgentState):
        messages = state["messages"]
        retry_count = state.get("retry_count", 0)
        
        try:
            llm_with_tools = llm.bind_tools(tools)
            response = llm_with_tools.invoke(messages)
            
            # Reset retry count on success
            return {
                "messages": [response],
                "retry_count": 0
            }
        
        except Exception as e:
            if retry_count < max_retries:
                # Add error message and retry
                error_msg = AIMessage(
                    content=f"I encountered an error: {str(e)}. Let me try again."
                )
                return {
                    "messages": [error_msg],
                    "retry_count": retry_count + 1
                }
            else:
                # Max retries reached
                final_msg = AIMessage(
                    content="I'm having trouble completing this task. Please try rephrasing your request."
                )
                return {"messages": [final_msg]}
    
    # Build the workflow
    tool_node = ToolNode(tools, handle_tool_errors=True)
    workflow.add_node("agent", agent_with_retry)
    workflow.add_node("tools", tool_node)
    
    # Routing logic
    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        retry_count = state.get("retry_count", 0)
        
        if retry_count >= max_retries:
            return "__end__"
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        
        return "__end__"
    
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()
```

## Best Practices

### 1. Tool Design Guidelines
```python
# Good tool design
@tool
def fetch_user_data(
    user_id: str,
    fields: Optional[List[str]] = None,
    include_metadata: bool = False
) -> Dict[str, Any]:
    """
    Fetch user data from the database.
    
    Args:
        user_id: The unique identifier for the user
        fields: Specific fields to retrieve. If None, returns all fields
        include_metadata: Whether to include metadata like timestamps
        
    Returns:
        Dictionary containing user data
        
    Raises:
        ValueError: If user_id is invalid
        LookupError: If user not found
    """
    # Validation
    if not user_id or not isinstance(user_id, str):
        raise ValueError("Invalid user_id")
    
    # Implementation
    user_data = {"id": user_id, "name": "John Doe"}  # Mock
    
    if fields:
        user_data = {k: v for k, v in user_data.items() if k in fields}
    
    if include_metadata:
        user_data["_metadata"] = {
            "retrieved_at": datetime.now().isoformat(),
            "version": "1.0"
        }
    
    return user_data
```

### 2. Prompt Engineering for Tool Use
```python
def create_specialized_agent(domain: str):
    """Create an agent with domain-specific prompting"""
    
    prompts = {
        "research": """You are a research assistant with access to various tools.
        Always verify information from multiple sources when possible.
        Cite your sources and indicate confidence levels in your findings.""",
        
        "technical": """You are a technical assistant specializing in software development.
        When using code execution tools, always validate inputs and handle errors.
        Provide clear explanations of technical concepts.""",
        
        "analyst": """You are a data analyst with expertise in statistical analysis.
        Use data analysis tools to provide insights and visualizations.
        Always specify assumptions and limitations in your analysis."""
    }
    
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.1  # Lower temperature for more consistent tool use
    )
    
    return create_react_agent(
        model=llm,
        tools=get_tools_for_domain(domain),
        state_modifier=prompts.get(domain, "You are a helpful assistant.")
    )
```

### 3. Tool Selection Strategy
```python
class SmartToolSelector:
    """Dynamically select relevant tools based on user query"""
    
    def __init__(self, all_tools: List):
        self.all_tools = all_tools
        self.tool_embeddings = self._create_tool_embeddings()
    
    def select_tools(self, query: str, max_tools: int = 5) -> List:
        """Select most relevant tools for the query"""
        # Simple keyword matching (in production, use embeddings)
        relevant_tools = []
        
        query_lower = query.lower()
        tool_scores = []
        
        for tool in self.all_tools:
            score = self._calculate_relevance(tool, query_lower)
            tool_scores.append((tool, score))
        
        # Sort by relevance and return top tools
        tool_scores.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, _ in tool_scores[:max_tools]]
    
    def _calculate_relevance(self, tool, query: str) -> float:
        """Calculate tool relevance score"""
        tool_desc = (tool.__doc__ or "").lower()
        tool_name = tool.__name__.lower()
        
        score = 0
        # Check for keyword matches
        keywords = query.split()
        for keyword in keywords:
            if keyword in tool_desc:
                score += 2
            if keyword in tool_name:
                score += 3
        
        return score
```

### 4. Monitoring and Logging
```python
import logging
from datetime import datetime
from typing import Any
import json

class ToolUsageMonitor:
    """Monitor and log tool usage for debugging and optimization"""
    
    def __init__(self):
        self.logger = logging.getLogger("tool_usage")
        self.usage_stats = {}
    
    def log_tool_call(self, tool_name: str, args: Dict, result: Any, duration: float):
        """Log a tool call with details"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "args": args,
            "success": result is not None,
            "duration_ms": duration * 1000
        }
        
        self.logger.info(json.dumps(log_entry))
        
        # Update statistics
        if tool_name not in self.usage_stats:
            self.usage_stats[tool_name] = {
                "calls": 0,
                "failures": 0,
                "total_duration": 0
            }
        
        stats = self.usage_stats[tool_name]
        stats["calls"] += 1
        stats["total_duration"] += duration
        if result is None:
            stats["failures"] += 1
    
    def get_statistics(self) -> Dict:
        """Get tool usage statistics"""
        return {
            tool: {
                **stats,
                "avg_duration": stats["total_duration"] / stats["calls"] if stats["calls"] > 0 else 0,
                "success_rate": (stats["calls"] - stats["failures"]) / stats["calls"] if stats["calls"] > 0 else 0
            }
            for tool, stats in self.usage_stats.items()
        }
```

## Complete Examples

### Example 1: Research Assistant Agent
```python
from typing import List, Dict
import json
from datetime import datetime

class ResearchAssistant:
    """A complete research assistant implementation"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.1
        )
        self.tools = self._create_research_tools()
        self.agent = self._build_agent()
        self.research_history = []
    
    def _create_research_tools(self):
        @tool
        def search_academic_papers(query: str, max_results: int = 5) -> str:
            """Search for academic papers on a topic"""
            # Mock implementation
            papers = [
                {"title": f"Paper about {query} #{i}", "year": 2024, "citations": i*10}
                for i in range(1, max_results + 1)
            ]
            return json.dumps(papers, indent=2)
        
        @tool
        def analyze_paper(paper_id: str) -> str:
            """Analyze a specific paper in detail"""
            return f"Detailed analysis of paper {paper_id}: Key findings, methodology, limitations..."
        
        @tool
        def create_bibliography(papers: List[str], format: str = "APA") -> str:
            """Create a formatted bibliography"""
            bibliography = f"Bibliography in {format} format:\n\n"
            for i, paper in enumerate(papers, 1):
                bibliography += f"{i}. {paper}\n"
            return bibliography
        
        @tool
        def summarize_findings(topic: str, key_points: List[str]) -> str:
            """Create a summary of research findings"""
            summary = f"Research Summary: {topic}\n\n"
            summary += "Key Findings:\n"
            for point in key_points:
                summary += f"• {point}\n"
            return summary
        
        return [search_academic_papers, analyze_paper, create_bibliography, summarize_findings]
    
    def _build_agent(self):
        return create_react_agent(
            model=self.llm,
            tools=self.tools,
            state_modifier="""You are an expert research assistant. Your goals:
            1. Find relevant academic papers and sources
            2. Analyze and synthesize information
            3. Create well-structured summaries and bibliographies
            4. Always cite sources and indicate confidence levels
            
            Break down complex research tasks into steps and use tools systematically."""
        )
    
    def research(self, topic: str, depth: str = "standard") -> Dict:
        """Conduct research on a topic"""
        start_time = datetime.now()
        
        # Adjust prompt based on depth
        depth_prompts = {
            "quick": "Provide a brief overview with 2-3 key sources.",
            "standard": "Conduct a thorough research with 5-10 sources and detailed analysis.",
            "comprehensive": "Perform an exhaustive research with 10+ sources, comparative analysis, and critical evaluation."
        }
        
        prompt = f"""Research the topic: {topic}
        
        Depth level: {depth}
        {depth_prompts.get(depth, depth_prompts["standard"])}
        
        Please:
        1. Search for relevant papers
        2. Analyze key findings
        3. Create a summary
        4. Generate a bibliography
        """
        
        response = self.agent.invoke({
            "messages": [{"role": "user", "content": prompt}]
        })
        
        # Store research in history
        research_record = {
            "topic": topic,
            "timestamp": start_time.isoformat(),
            "duration": (datetime.now() - start_time).total_seconds(),
            "depth": depth,
            "response": response
        }
        self.research_history.append(research_record)
        
        return research_record

# Usage
assistant = ResearchAssistant()
result = assistant.research(
    "Impact of LLMs on software development productivity",
    depth="comprehensive"
)
```

### Example 2: DevOps Automation Agent
```python
class DevOpsAgent:
    """Agent for DevOps automation tasks"""
    
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.tools = self._create_devops_tools()
        self.agent = self._build_agent()
    
    def _create_devops_tools(self):
        @tool
        def check_system_status(service: str) -> str:
            """Check the status of a system service"""
            # Mock implementation
            statuses = {
                "web_server": "running",
                "database": "running",
                "cache": "stopped",
                "queue": "running"
            }
            return f"Service {service}: {statuses.get(service, 'unknown')}"
        
        @tool
        def analyze_logs(
            service: str,
            time_range: str = "1h",
            severity: str = "all"
        ) -> str:
            """Analyze service logs"""
            return f"Log analysis for {service} (last {time_range}, severity: {severity}): No critical errors found"
        
        @tool
        def deploy_service(
            service: str,
            version: str,
            environment: str = "staging"
        ) -> str:
            """Deploy a service to specified environment"""
            return f"Deployment initiated: {service} v{version} to {environment}"
        
        @tool
        def run_diagnostics(service: str) -> Dict:
            """Run comprehensive diagnostics on a service"""
            return {
                "service": service,
                "cpu_usage": "45%",
                "memory_usage": "62%",
                "disk_usage": "73%",
                "network_latency": "12ms",
                "error_rate": "0.02%",
                "recommendations": [
                    "Consider scaling if CPU usage exceeds 80%",
                    "Monitor disk usage - approaching threshold"
                ]
            }
        
        return [check_system_status, analyze_logs, deploy_service, run_diagnostics]
    
    def _build_agent(self):
        workflow = StateGraph(AgentState)
        
        def agent_node(state: AgentState):
            messages = state["messages"]
            
            # Add system context
            system_msg = """You are a DevOps automation assistant. You can:
            1. Monitor system health and status
            2. Analyze logs and identify issues
            3. Deploy services safely
            4. Run diagnostics and provide recommendations
            
            Always prioritize system stability and follow best practices.
            For deployments, always check system status first."""
            
            full_messages = [{"role": "system", "content": system_msg}] + messages
            
            llm_with_tools = self.llm.bind_tools(self.tools)
            response = llm_with_tools.invoke(full_messages)
            
            return {"messages": [response]}
        
        # Add nodes and edges
        tool_node = ToolNode(self.tools)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        
        def should_continue(state: AgentState):
            last_message = state["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            return "__end__"
        
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()

# Usage
devops = DevOpsAgent()
response = devops.agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Check the health of our web services and deploy the API service v2.1 to staging if everything looks good"
    }]
})
```

### Example 3: Data Analysis Agent with Streaming
```python
class DataAnalysisAgent:
    """Agent for data analysis with streaming support"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            streaming=True
        )
        self.tools = self._create_analysis_tools()
        self.agent = self._build_streaming_agent()
    
    def _create_analysis_tools(self):
        @tool
        def load_dataset(name: str, filters: Optional[Dict] = None) -> str:
            """Load a dataset with optional filters"""
            # Mock implementation
            return f"Loaded dataset '{name}' with {1000} rows"
        
        @tool
        def statistical_analysis(
            dataset: str,
            metrics: List[str]
        ) -> Dict:
            """Perform statistical analysis on dataset"""
            results = {}
            for metric in metrics:
                if metric == "mean":
                    results[metric] = 42.5
                elif metric == "std":
                    results[metric] = 15.3
                elif metric == "correlation":
                    results[metric] = 0.67
            return results
        
        @tool
        def create_visualization(
            data: str,
            chart_type: str,
            title: str
        ) -> str:
            """Create a data visualization"""
            return f"Created {chart_type} chart: '{title}'"
        
        return [load_dataset, statistical_analysis, create_visualization]
    
    def _build_streaming_agent(self):
        workflow = StateGraph(AgentState)
        
        def streaming_agent_node(state: AgentState):
            messages = state["messages"]
            llm_with_tools = self.llm.bind_tools(self.tools)
            
            # For streaming, we need to handle the response differently
            response_content = ""
            tool_calls = []
            
            for chunk in llm_with_tools.stream(messages):
                if chunk.content:
                    response_content += chunk.content
                    yield {"content": chunk.content}  # Stream content
                
                if hasattr(chunk, "tool_calls"):
                    tool_calls.extend(chunk.tool_calls)
            
            # Create the full message
            if tool_calls:
                response = AIMessage(content=response_content, tool_calls=tool_calls)
            else:
                response = AIMessage(content=response_content)
            
            return {"messages": [response]}
        
        # Build the graph
        tool_node = ToolNode(self.tools)
        workflow.add_node("agent", streaming_agent_node)
        workflow.add_node("tools", tool_node)
        
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            lambda x: "tools" if x["messages"][-1].tool_calls else "__end__"
        )
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    async def analyze_streaming(self, query: str):
        """Analyze data with streaming response"""
        initial_state = {
            "messages": [{"role": "user", "content": query}]
        }
        
        async for event in self.agent.astream_events(initial_state, version="v2"):
            if event["event"] == "on_llm_stream":
                content = event["data"]["chunk"].content
                if content:
                    print(content, end="", flush=True)

# Usage
async def main():
    analyst = DataAnalysisAgent()
    await analyst.analyze_streaming(
        "Load the sales dataset and perform a complete statistical analysis including correlations"
    )
```

## Conclusion

LangGraph with Claude's tool use capabilities provides a powerful framework for building sophisticated AI agents. Key takeaways:

1. **Start Simple**: Begin with basic tools and gradually add complexity
2. **Error Handling**: Always implement robust error handling for production use
3. **Monitor Usage**: Track tool performance and usage patterns
4. **Optimize Prompts**: Well-crafted prompts significantly improve tool selection and usage
5. **Test Thoroughly**: Test edge cases and error scenarios

The combination of LangGraph's stateful workflow management and Claude's advanced reasoning capabilities enables the creation of AI agents that can handle complex, multi-step tasks while maintaining context and recovering from errors gracefully.