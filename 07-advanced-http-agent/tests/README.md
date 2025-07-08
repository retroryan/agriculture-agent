# Tests for Weather Intelligence with MCP (HTTP Transport)

This directory contains comprehensive tests for the Weather Intelligence MCP system using HTTP transport.

## Test Organization

Tests are organized into categories for better maintainability:

### `/coordinates/`
Tests for coordinate handling and geocoding functionality:
- `test_simple_coordinate.py` - Basic smoke test for coordinate handling
- `test_coordinate_handling.py` - Tests coordinate handling in the MCP forecast server
- `test_coordinate_usage.py` - Tests whether LLM provides coordinates without geocoding
- `test_coordinates.py` - Comprehensive tests for coordinate and location handling

### `/mcp_servers/`
Tests for MCP server functionality:
- `test_mcp_servers.py` - Comprehensive tests for all MCP servers (forecast, historical, agricultural)
- `test_forecast_only.py` - Tests simplified forecast server using MCP client
- `test_mcp_client.py` - Tests using langchain_mcp_adapters client directly

### `/http_transport/`
Tests for HTTP-based MCP transport:
- `test_forecast_minimal.py` - Direct HTTP testing of the forecast server

### `/agent/`
Tests for LangGraph agent integration:
- `test_mcp_agent.py` - Comprehensive MCP Agent functionality tests
- `test_minimal_agent.py` - Full integration test with LangGraph ReAct agent

### `/integration/`
End-to-end integration tests:
- `test_diverse_cities.py` - Tests geographic knowledge for diverse global cities
- `test_structured_output_demo.py` - Demonstrates structured output using LangGraph
- `test_extended_queries.py` - Tests edge cases and various query types
- `test_docker_agent.py` - Tests Docker deployment (requires Docker)

## Running Tests

### Run All Tests
```bash
python run_all_tests.py
```

### Run Tests by Category
```bash
# Coordinate tests only
python -m pytest coordinates/

# MCP server tests only
python -m pytest mcp_servers/

# Integration tests only
python -m pytest integration/
```

### Run Individual Tests
```bash
# Example: Run the minimal agent test
python agent/test_minimal_agent.py

# Example: Run coordinate handling test
python coordinates/test_coordinate_handling.py
```

## Test Environment

- Tests start MCP servers as subprocesses
- Some tests make real API calls to Open-Meteo
- Ensure you have set your `ANTHROPIC_API_KEY` environment variable
- Tests use the HTTP transport layer (port 7071 by default)

## Notes

- The Docker integration test is commented out in `run_all_tests.py` by default
- Tests may take time due to LLM interactions and API calls
- Each test category can be run independently