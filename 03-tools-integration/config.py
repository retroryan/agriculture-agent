"""
Unified model configuration for demo applications.
Simple, clean interface for model initialization using init_chat_model.
"""

import os
from typing import Optional
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def get_model(temperature: float = 0.0) -> BaseChatModel:
    """
    Get a configured model instance for demos.
    
    This simple function handles model initialization with sensible defaults.
    Uses environment variables for configuration:
    - ANTHROPIC_API_KEY: Required API key
    - MODEL_NAME: Optional model override (defaults to Claude 3.5 Sonnet)
    
    Args:
        temperature: Model temperature (0-1), defaults to 0 for consistency
        
    Returns:
        Initialized chat model ready for use with tools
        
    Example:
        model = get_model()
        model_with_tools = model.bind_tools(tools)
    """
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    
    # Get model name with sensible default
    model_name = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022")
    
    # Initialize model with unified interface
    return init_chat_model(
        model_name,
        temperature=temperature,
        api_key=api_key
    )