#!/usr/bin/env python3
"""
FastMCP Examples - Main Entry Point
Orchestrates server startup and client demos
"""
import asyncio
import subprocess
import sys
import os
import time
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("\n" + "="*60)
    print("FastMCP Examples")
    print("="*60)
    print("Demonstrates FastMCP server-client integration patterns")
    print("-"*60)

def start_server(server_name):
    """Start an MCP server"""
    server_path = Path("servers") / f"{server_name}.py"
    if not server_path.exists():
        print(f"Error: Server {server_name} not found at {server_path}")
        return None
    
    print(f"Starting {server_name} server...")
    process = subprocess.Popen([
        sys.executable, str(server_path)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Give server time to start
    time.sleep(2)
    
    if process.poll() is None:  # Still running
        print(f"✅ {server_name} server started (PID: {process.pid})")
        return process
    else:
        stdout, stderr = process.communicate()
        print(f"❌ Failed to start {server_name} server")
        if stderr:
            print(f"Error: {stderr.decode()}")
        return None

def run_client_demo():
    """Run the client demo"""
    demo_path = Path("client") / "demo.py"
    if not demo_path.exists():
        print(f"Error: Demo not found at {demo_path}")
        return False
    
    print("\nStarting client demo...")
    result = subprocess.run([sys.executable, str(demo_path)])
    return result.returncode == 0

def run_complex_inputs_client():
    """Run the complex inputs client"""
    client_path = Path("client") / "client_complex_inputs.py"
    if not client_path.exists():
        print(f"Error: Complex inputs client not found at {client_path}")
        return False
    
    print("\nStarting complex inputs client...")
    result = subprocess.run([sys.executable, str(client_path)])
    return result.returncode == 0

def check_requirements():
    """Check if requirements are installed"""
    try:
        import fastmcp
        import langchain_anthropic
        return True
    except ImportError as e:
        print(f"❌ Missing requirements: {e}")
        print("Please install requirements:")
        print("  pip install -r requirements.txt")
        return False

def main():
    """Main entry point"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check for .env file if needed for demo
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚠️  Warning: .env file not found")
        print("For Claude integration demos, create .env with:")
        print("ANTHROPIC_API_KEY=your_api_key_here")
    
    server_process = None
    
    try:
        print("\nAvailable options:")
        print("1. Run serializer server + demo client")
        print("2. Run complex inputs server + client")
        print("3. Start serializer server only")
        print("4. Start complex inputs server only")
        print("5. Run demo client only (requires running server)")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            # Start serializer server and run demo
            server_process = start_server("serializer")
            if server_process:
                run_client_demo()
        
        elif choice == "2":
            # Start complex inputs server and run client
            server_process = start_server("complex_inputs")
            if server_process:
                run_complex_inputs_client()
        
        elif choice == "3":
            # Start serializer server only
            server_process = start_server("serializer")
            if server_process:
                print("\nServer running. Press Ctrl+C to stop.")
                try:
                    server_process.wait()
                except KeyboardInterrupt:
                    pass
        
        elif choice == "4":
            # Start complex inputs server only
            server_process = start_server("complex_inputs")
            if server_process:
                print("\nServer running. Press Ctrl+C to stop.")
                try:
                    server_process.wait()
                except KeyboardInterrupt:
                    pass
        
        elif choice == "5":
            # Run demo client only
            run_client_demo()
        
        elif choice == "6":
            print("\nGoodbye!")
            return
        
        else:
            print("\nInvalid choice. Please enter 1-6.")
    
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    
    finally:
        # Clean up server process
        if server_process and server_process.poll() is None:
            print("Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("Server stopped.")

if __name__ == "__main__":
    main()