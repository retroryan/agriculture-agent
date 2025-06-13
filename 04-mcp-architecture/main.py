#!/usr/bin/env python3
"""
MCP Weather Demo - stdio Subprocess Architecture

This demonstrates MCP servers running as subprocesses with stdio communication.

Usage:
    python 04-mcp-architecture/main.py          # Interactive mode
    python 04-mcp-architecture/main.py --demo   # Demo mode
"""

import sys
import argparse
sys.path.append('04-mcp-architecture')

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MCP Weather Demo - stdio Subprocess Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This demo shows how MCP servers work:
- Servers run as stdio subprocesses
- Communication via JSON-RPC over stdin/stdout
- Tools are discovered dynamically
- Automatic subprocess cleanup
        """
    )
    
    parser.add_argument(
        '--demo', 
        action='store_true',
        help='Run demo with example queries'
    )
    
    parser.add_argument(
        '--multi-turn-demo',
        action='store_true',
        help='Run multi-turn conversation demo'
    )
    
    args = parser.parse_args()
    
    import asyncio
    
    # Handle multi-turn demo
    if args.multi_turn_demo:
        from weather_agent.demo_scenarios import run_mcp_multi_turn_demo
        asyncio.run(run_mcp_multi_turn_demo())
    else:
        # Import and run the chatbot
        from weather_agent.chatbot import main as chatbot_main
        
        # Pass demo flag if provided
        if args.demo:
            sys.argv = [sys.argv[0], '--demo']
        else:
            sys.argv = [sys.argv[0]]
        
        asyncio.run(chatbot_main())


if __name__ == "__main__":
    main()