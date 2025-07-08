"""
Unified model configuration for advanced MCP with structured output.

This module demonstrates the use of LangChain's init_chat_model()
for runtime model flexibility in educational demos.
"""
import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def get_model(temperature=0.7, model_name=None, **kwargs):
    """
    Initialize a chat model using the unified interface.
    
    Following best practices for demo simplicity:
    - Single function for model initialization
    - Runtime model switching via MODEL_NAME env var
    - Sensible defaults for educational clarity
    
    Args:
        temperature: Model temperature (default 0.7 for conversational tone)
        model_name: Optional model override (defaults to Claude 3.5 Sonnet)
        **kwargs: Additional model parameters
    
    Returns:
        Initialized chat model ready for tool binding
    """
    # Use environment variable or default
    if model_name is None:
        model_name = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022")
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    
    # Initialize model with unified interface
    # init_chat_model automatically handles provider detection
    return init_chat_model(
        model_name,
        temperature=temperature,
        api_key=api_key,
        **kwargs
    )