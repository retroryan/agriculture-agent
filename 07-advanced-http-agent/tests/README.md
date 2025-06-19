# 05-advanced-mcp Tests

This directory contains all tests for the 05-advanced-mcp stage of the weather intelligence system.

## Test Files

### Coordinate Handling Tests
- **test_coordinate_handling.py** - Basic coordinate parameter testing
- **test_coordinate_usage.py** - Tests if LLM provides coordinates vs using geocoding
- **test_coordinates.py** - General coordinate functionality tests  
- **test_simple_coordinate.py** - Simple verification of coordinate handling
- **test_diverse_cities.py** - Tests global city coverage without hardcoded lists

### MCP Integration Tests
- **test_mcp_servers.py** - Tests for MCP server functionality (forecast, historical, agricultural)
- **test_mcp_agent.py** - Tests for the MCP weather agent integration

### Structured Output Tests
- **test_structured_output_demo.py** - Tests for structured data output with Pydantic models

## Running Tests

### Run All Tests
```bash
# Run all async tests in sequence with summary
cd 05-advanced-mcp
python tests/run_all_tests.py
```

### Run Individual Tests
```bash
# Run individual tests
cd 05-advanced-mcp
python tests/test_simple_coordinate.py
python tests/test_diverse_cities.py
python tests/test_mcp_servers.py

# Test coordinate provision tracking
python tests/test_coordinate_usage.py
```

### Run with pytest
```bash
# Run with pytest (note: some async tests may not work properly)
cd 05-advanced-mcp
pytest tests/ -v
```

## Notes
- Tests require MCP servers to be started as subprocesses
- Ensure ANTHROPIC_API_KEY is set in your .env file
- Some tests make real API calls to Open-Meteo