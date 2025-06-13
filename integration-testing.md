# Integration Testing for LLM-Based Applications

## Basic Demo Testing Approach

For this tutorial project, we'll implement minimal smoke tests that simply verify each application runs without throwing errors. This approach:

- **Validates basic functionality** without complex assertions
- **Minimizes LLM costs** by using mocked responses or environment variables
- **Provides quick feedback** during development
- **Demonstrates testing concepts** without overengineering

### Simple Integration Test Structure

```bash
# Each stage will have an integration/ directory with basic tests
01-foundations/integration/
├── test_smoke.py          # Simple "does it run?" tests
└── run_tests.sh          # Convenience script

# Basic test pattern
def test_app_runs_without_error():
    """Verify the application starts and processes a simple input"""
    try:
        # Import and run the app
        result = run_app_with_test_input()
        assert result is not None
        assert "error" not in str(result).lower()
    except Exception as e:
        pytest.fail(f"Application failed to run: {e}")
```

### Environment Setup for Tests

```bash
# Use test environment variables to avoid LLM calls
export USE_MOCK_LLM=true
export ANTHROPIC_API_KEY=test-key-for-mocking

# Run tests
pytest 01-foundations/integration/test_smoke.py -v
```

---

## Comprehensive Testing Guide

Below is a detailed guide for production-grade LLM application testing, provided for reference and learning purposes.

## Overview

Testing applications that integrate with Large Language Models (LLMs) presents unique challenges due to their non-deterministic nature, API costs, and response variability. This document outlines best practices for integration testing LLM-based applications in the agriculture-agent project.

## Key Challenges

1. **Non-determinism**: LLMs can produce different outputs for the same input
2. **API Costs**: Each LLM call incurs costs, making extensive testing expensive
3. **Latency**: LLM API calls can be slow (1-10+ seconds)
4. **Rate Limits**: API providers impose rate limits
5. **Output Validation**: Validating free-form text responses is complex

## Industry Best Practices

### 1. Test Strategy Layers

```
┌─────────────────────────────────┐
│      End-to-End Tests          │ ← Run on merge to main
│   (Real LLM, Full Pipeline)    │
├─────────────────────────────────┤
│    Integration Tests           │ ← Run on PR (selected)
│  (Mock/Real LLM, Components)   │
├─────────────────────────────────┤
│      Unit Tests               │ ← Run on every commit
│  (Mocked LLM, Pure Logic)     │
└─────────────────────────────────┘
```

### 2. Mock vs Real LLM Calls

#### Development & CI Pipeline
- **Unit Tests**: Always use mocked LLM responses
- **Integration Tests**: Use configurable mocking with option for real calls
- **PR Tests**: Run subset with mocked responses, optional real LLM tests
- **Merge to Main**: Run full suite including real LLM tests

#### Mock Strategies
```python
# 1. Response Recording (VCR Pattern)
# Record real responses and replay in tests
class LLMRecorder:
    def record_mode(self):
        # Save real API responses to fixtures
    
    def replay_mode(self):
        # Return saved responses

# 2. Behavioral Mocking
# Mock based on expected behavior patterns
class LLMMock:
    def generate(self, prompt):
        if "weather" in prompt:
            return {"type": "weather_query", "location": "extracted_location"}
        elif "calculate" in prompt:
            return {"type": "math_query", "operation": "extracted_operation"}

# 3. Snapshot Testing
# Compare outputs against known good snapshots
def test_weather_query():
    response = agent.process("What's the weather in Iowa?")
    assert_matches_snapshot(response)
```

### 3. Cost Management Strategies

#### Tiered Testing Approach
```yaml
# .github/workflows/tests.yml
on:
  pull_request:
    runs-on: ubuntu-latest
    steps:
      - name: Unit Tests (No LLM)
        run: pytest tests/unit -m "not llm"
      
      - name: Integration Tests (Mocked)
        run: pytest tests/integration --mock-llm
      
      - name: Smoke Tests (Real LLM)
        if: github.event.pull_request.draft == false
        run: pytest tests/integration -m "smoke" --real-llm
        env:
          LLM_TEST_BUDGET: "1.00"  # $1 limit

  push:
    branches: [main]
    runs-on: ubuntu-latest
    steps:
      - name: Full Integration Suite
        run: pytest tests/integration --real-llm
        env:
          LLM_TEST_BUDGET: "10.00"  # $10 limit
```

#### Test Budget Enforcement
```python
class LLMTestBudget:
    def __init__(self, max_cost=1.0):
        self.max_cost = max_cost
        self.current_cost = 0.0
    
    def track_call(self, model, tokens):
        cost = calculate_cost(model, tokens)
        self.current_cost += cost
        if self.current_cost > self.max_cost:
            pytest.skip(f"Test budget exceeded: ${self.current_cost:.2f}")
```

### 4. Testing Non-Deterministic Outputs

#### Structural Validation
```python
def test_weather_query_structure():
    response = agent.process("What's the weather in Des Moines?")
    
    # Don't test exact text, test structure
    assert response["query_type"] == "weather"
    assert "location" in response
    assert "Des Moines" in response["location"]
    assert response["confidence"] > 0.8
```

#### Semantic Validation
```python
def test_weather_response_semantics():
    response = agent.process("Is it good weather for planting corn?")
    
    # Test semantic properties
    assert any(keyword in response.lower() 
              for keyword in ["temperature", "moisture", "conditions"])
    assert len(response) > 50  # Meaningful response
    assert response.count('.') >= 2  # Multiple sentences
```

#### Property-Based Testing
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=10, max_size=100))
def test_agent_handles_any_input(user_input):
    # Test that agent doesn't crash on any input
    response = agent.process(user_input)
    assert isinstance(response, dict)
    assert "error" in response or "result" in response
```

### 5. Integration Test Patterns

#### Test Fixtures
```python
# tests/fixtures/llm_responses.py
WEATHER_QUERY_RESPONSES = {
    "simple_weather": {
        "prompt_contains": ["weather", "temperature"],
        "response": {"type": "weather", "requires": ["temperature_api"]}
    },
    "agricultural_query": {
        "prompt_contains": ["corn", "planting", "soil"],
        "response": {"type": "agricultural", "requires": ["soil_moisture_api"]}
    }
}
```

#### Environment-Based Configuration
```python
# tests/conftest.py
import os
import pytest

@pytest.fixture
def llm_client():
    if os.getenv("USE_REAL_LLM", "false").lower() == "true":
        return RealLLMClient()
    else:
        return MockLLMClient()

@pytest.fixture(scope="session")
def test_mode():
    # Detect test mode from environment
    if os.getenv("CI"):
        return "ci"
    elif os.getenv("INTEGRATION_TEST_FULL"):
        return "full"
    else:
        return "local"
```

### 6. Specific Test Categories

#### Smoke Tests (Quick, Essential)
- Basic connectivity to LLM API
- Simple query classification
- Core tool execution
- Error handling for common failures

#### Regression Tests
- Specific queries that previously failed
- Edge cases discovered in production
- Format compatibility tests

#### Contract Tests
- API response format validation
- Tool interface compliance
- Error response structures

#### Performance Tests
```python
@pytest.mark.performance
def test_response_time():
    start = time.time()
    response = agent.process("What's the weather?")
    duration = time.time() - start
    
    assert duration < 5.0  # Should respond within 5 seconds
    assert "cached" in response or duration > 0.1  # Real call takes time
```

### 7. Monitoring & Observability

#### Test Metrics Collection
```python
class TestMetricsCollector:
    def __init__(self):
        self.metrics = {
            "total_llm_calls": 0,
            "total_cost": 0.0,
            "response_times": [],
            "error_rate": 0.0
        }
    
    def pytest_runtest_teardown(self, item):
        # Collect metrics after each test
        if hasattr(item, "llm_metrics"):
            self.update_metrics(item.llm_metrics)
```

## Implementation Guidelines

### 1. Directory Structure
```
agriculture-agent/
├── tests/
│   ├── unit/              # No LLM calls
│   ├── integration/       # Component integration tests
│   │   ├── __init__.py
│   │   ├── conftest.py    # Shared fixtures
│   │   ├── test_*.py      # Test files
│   │   └── fixtures/      # Response fixtures
│   └── e2e/              # End-to-end tests
├── 01-foundations/
│   └── integration/      # Stage-specific tests
│       ├── __init__.py
│       ├── test_langchain_basic.py
│       └── test_langgraph_chatbot.py
```

### 2. Test Markers
```python
# pytest.ini
[pytest]
markers =
    llm: Tests that make real LLM calls
    smoke: Quick smoke tests for CI
    slow: Tests that take >5 seconds
    expensive: Tests that cost >$0.10
    integration: Integration tests
    unit: Unit tests
```

### 3. Cost Tracking
```python
# tests/utils/cost_tracking.py
def track_llm_cost(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        monitor = LLMCostMonitor()
        try:
            result = func(*args, **kwargs)
            cost = monitor.get_cost()
            print(f"Test cost: ${cost:.4f}")
            return result
        finally:
            monitor.stop()
    return wrapper
```

## CI/CD Pipeline Recommendations

### 1. PR Pipeline (Fast, Cheap)
```yaml
- Unit tests: All, no LLM
- Integration tests: Mocked LLM only
- Smoke tests: 2-3 real LLM calls max
- Total time: <5 minutes
- Total cost: <$0.10
```

### 2. Main Branch Pipeline (Comprehensive)
```yaml
- All unit tests
- All integration tests with real LLM
- Performance benchmarks
- Cost tracking and reporting
- Total time: <15 minutes
- Total cost: <$5.00
```

### 3. Nightly Pipeline (Extensive)
```yaml
- Full regression suite
- Edge case testing
- Multi-model compatibility tests
- Performance regression tests
- Total cost: <$20.00
```

## Cost Optimization Tips

1. **Cache LLM Responses**: Use Redis or similar for development
2. **Use Smaller Models for Tests**: GPT-3.5 for tests, GPT-4 for production
3. **Batch Similar Tests**: Group tests to reuse context
4. **Skip Redundant Tests**: Don't test the same prompt variations
5. **Use Deterministic Seeds**: When possible, use temperature=0

## Example Test Implementation

```python
# 01-foundations/integration/test_langgraph_chatbot.py
import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestLangGraphChatbot:
    @pytest.mark.integration
    @pytest.mark.llm
    def test_basic_conversation_real(self):
        """Test with real LLM - runs on merge to main"""
        from langgraph.basic_chatbot import create_chatbot
        
        app = create_chatbot()
        response = app.invoke({
            "messages": [{"role": "user", "content": "Hello"}]
        })
        
        assert len(response["messages"]) == 2
        assert response["messages"][1]["role"] == "assistant"
        assert len(response["messages"][1]["content"]) > 0
    
    @pytest.mark.integration
    def test_basic_conversation_mocked(self):
        """Test with mocked LLM - runs on every PR"""
        with patch('langchain_anthropic.ChatAnthropic') as mock_llm:
            mock_llm.return_value.invoke.return_value.content = "Hello! How can I help?"
            
            from langgraph.basic_chatbot import create_chatbot
            app = create_chatbot()
            
            response = app.invoke({
                "messages": [{"role": "user", "content": "Hello"}]
            })
            
            assert response["messages"][1]["content"] == "Hello! How can I help?"
```

## Summary

Effective LLM testing requires a balanced approach:
- **Develop with mocks** to iterate quickly
- **Test with real LLMs** selectively
- **Monitor costs** continuously
- **Validate behavior**, not exact outputs
- **Run expensive tests** only when necessary

This strategy ensures reliable applications while managing costs and development velocity.