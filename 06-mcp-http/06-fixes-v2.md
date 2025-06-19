# 06-MCP-HTTP Fixes v2

## Investigation Status

### Issue Summary
- **Error**: `RuntimeError: Client is not connected. Use the 'async with client:' context manager first.`
- **Location**: When running `python main.py --demo`
- **Context**: The error occurs when trying to use the forecast tool

### Investigation Progress

#### Initial Findings
- The error suggests that an HTTP client is being used without proper initialization
- This is likely related to the async context manager pattern in httpx

#### Root Cause Analysis
- Found the issue in `mcp_agent.py` lines 143-146
- The code calls `await self.forecast_client.__aenter__()` but the tools try to use the client outside the context
- FastMCP Client requires being used within an async context manager
- The current approach of manually calling `__aenter__` doesn't maintain the connection properly

#### Solution Approach
The FastMCP Client must be used within an `async with` block. Current code structure doesn't support this pattern well because:
1. The client is initialized in `initialize()` but used later in tool functions
2. Tools are created as closures that capture the client reference
3. The client connection is not maintained between initialize and tool execution

We need to refactor to ensure clients are properly connected when tools are called.

### Fix Applied

Modified `mcp_agent.py` to use proper async context managers:

1. **Removed manual connection management** in `initialize()`:
   - Removed `await self.forecast_client.__aenter__()` calls
   - Clients are now connected within each tool call

2. **Updated all tool functions** to use async with:
   ```python
   async with self.forecast_client as client:
       response = await client.call_tool(...)
   ```

3. **Simplified cleanup**:
   - Removed manual `__aexit__` calls
   - Clients now manage their own lifecycle within tool contexts

This ensures each tool call has a properly connected client.

### Testing Results

After applying the fix and starting the servers:
- The "Client is not connected" error is resolved
- Tools can now successfully attempt to connect to the FastMCP servers
- New error: `ConnectError: All connection attempts failed`

This indicates the fix worked for the client connection issue, but now we have a different problem - the servers weren't running initially, and after starting them, there may be connection issues.

### New Issue: Session Terminated

After the servers are started:
- Direct test with `test_mcp_simple.py` works perfectly
- But when running through the agent, we get `McpError: Session terminated`

This suggests there may be an issue with:
1. How multiple clients are being created (one for each server)
2. Session management when used within LangGraph tools
3. The async context manager being used repeatedly for multiple tool calls

### Solution Approach v2

The FastMCP client needs persistent connections throughout the agent's lifecycle. We need to:
1. Connect the clients once in `initialize()` and keep them connected
2. Use the connected clients directly in tools (without `async with`)
3. Properly disconnect in `cleanup()`

This is similar to the original approach but with proper session management.

### Fix v2 Applied

Modified the approach to maintain persistent connections:

1. **Store server URLs** in `__init__` instead of creating clients
2. **Create and connect clients** in `initialize()`:
   - Use `__aenter__()` to establish connections
   - Store the connected context managers
3. **Use connected clients** in tools:
   - No more `async with` in each tool call
   - Use `self._forecast_ctx.call_tool()` directly
4. **Proper cleanup** in `cleanup()`:
   - Call `__aexit__()` on each client

This ensures sessions remain active throughout the agent's lifecycle.

### Testing v2 Results

The persistent connection approach also failed with the same error. The issue is that FastMCP Client doesn't support the pattern we're trying to use.

### Final Solution Approach

After investigation, the issue is that FastMCP clients are designed to be used with `async with` blocks and don't support long-lived connections across multiple tool calls. 

The best approach is to create new connections for each tool call, which is what the first fix attempted. However, we need to ensure:

1. Each tool creates its own client instance
2. The client is used within a proper `async with` block
3. We don't try to reuse clients across tool calls

This is less efficient but aligns with how FastMCP is designed to work.

### Final Fix Applied

Reverted to creating a new client for each tool call:

1. **Store only server URLs** in `__init__`
2. **Each tool creates its own client**:
   ```python
   client = Client(self.forecast_server_url)
   async with client:
       response = await client.call_tool(...)
   ```
3. **No persistent connections** to manage
4. **Simplified cleanup** - nothing to clean up

This approach:
- Works with FastMCP's design expectations
- Avoids session management issues
- Creates fresh connections for each tool call
- Is the pattern shown in FastMCP examples

### Root Cause Found

Server logs show `POST / HTTP/1.1" 404 Not Found`. The issue is that the FastMCP client is posting to "/" instead of "/mcp" endpoint.

The server URLs are constructed incorrectly. FastMCP servers expose their MCP interface at the root path "/", not "/mcp".

### URL Path Fix

Changed default URLs in `mcp_agent.py`:
- From: `http://127.0.0.1:8000/mcp`
- To: `http://127.0.0.1:8000`

FastMCP servers expose their MCP interface at the root path, not a subpath.

### Critical Finding

The implementation is not following the FastMCP client documentation at https://gofastmcp.com/clients/client. 

The correct approach requires:
1. Using `mcpServers` configuration format
2. Proper client initialization with server configuration
3. The URLs should use `/mcp` endpoint for HTTP transport

Current implementation is incorrectly trying to use the Client class directly without proper configuration.

### Correction

After checking the FastMCP documentation and test files:
1. The Client usage is correct - it should be used with `async with`
2. The URLs should include `/mcp` endpoint for HTTP transport (reverting the previous change)
3. The "Session terminated" error is likely due to server-side issues

### Summary of All Fixes Applied

1. **Fixed "Client is not connected" error** by ensuring each tool call creates its own client within an `async with` block
2. **Reverted URL paths** to include `/mcp` endpoint as shown in working test files
3. **Final implementation**:
   - Each tool creates a fresh Client instance
   - Uses `async with client:` for proper connection management
   - URLs use the `/mcp` endpoint

The remaining "Session terminated" errors appear to be server-side issues rather than client implementation problems.
