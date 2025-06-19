# 06-MCP-HTTP Test Suite

This directory contains the 5 most important tests for the MCP HTTP implementation with coordinate handling.

## Test Files

1. **test_mcp_simple.py** - Core MCP functionality test
   - Tests direct FastMCP client connection
   - Validates JSON-RPC communication
   - Tests tool listing and calling
   - Verifies coordinate parameter handling at protocol level

2. **test_agent_simple.py** - Basic agent integration test
   - Tests end-to-end agent initialization and query flow
   - Quick smoke test for regression testing
   - Verifies the core user-facing functionality

3. **test_coordinates.py** - Comprehensive coordinate handling test
   - Tests all three MCP servers (forecast, historical, agricultural)
   - Tests geocoding API directly
   - Tests both location strings and direct coordinate parameters
   - Includes edge cases (empty strings, invalid locations, ambiguous cities)

4. **test_diverse_cities.py** - Geographic knowledge test
   - Tests 5 diverse cities from different continents
   - Verifies the agent's geographic knowledge
   - Tests special characters in city names
   - Provides success rate metrics

5. **test_error_handling.py** - Error scenario test
   - Tests invalid location geocoding
   - Tests nonsensical queries
   - Tests empty locations
   - Tests invalid coordinates

## Running Tests

### Prerequisites
1. Ensure MCP servers are running:
   ```bash
   cd ..
   ./start_servers.sh
   ```

2. Ensure environment variables are set:
   ```bash
   export ANTHROPIC_API_KEY=your-key-here
   ```

### Run All Tests
```bash
python run_all_tests.py
```

### Run Individual Tests
```bash
python test_mcp_simple.py
python test_agent_simple.py
python test_coordinates.py
python test_diverse_cities.py
python test_error_handling.py
```

## Expected Results
All tests should pass with a summary showing:
```
Test Summary: 5 passed, 0 failed
```

## Notes
- Tests require the MCP servers to be running on ports 8000, 8001, and 8002
- Some tests make API calls to Open-Meteo and require internet connectivity
- The diverse cities test has been optimized to test only 5 cities for faster execution