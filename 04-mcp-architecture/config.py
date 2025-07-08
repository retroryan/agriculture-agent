"""
Unified model configuration for MCP architecture.

This module demonstrates the use of LangChain's init_chat_model()
for runtime model flexibility in the MCP demo.
"""
import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

# Load environment variables
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


def get_model(model_name=None, temperature=0.7, **kwargs):
    """
    Initialize a chat model using the unified interface.
    
    This simple function demonstrates how to use init_chat_model()
    for flexible model configuration in educational demos.
    
    Args:
        model_name: Model identifier (e.g., "claude-3-5-sonnet-20241022")
                   If None, uses MODEL_NAME env var or default
        temperature: Model temperature (default 0.7 for conversational tone)
        **kwargs: Additional model parameters
    
    Returns:
        Initialized chat model ready for tool binding
    """
    # Use environment variable or default
    if model_name is None:
        model_name = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022")
    
    # Initialize model with unified interface
    # init_chat_model automatically handles provider detection
    model = init_chat_model(
        model_name,
        temperature=temperature,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        **kwargs
    )
    
    return model