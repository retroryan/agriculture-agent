"""
Base MCP server class with structured response support.

This provides common functionality for all MCP weather servers including:
- Structured response formatting
- Error handling
- Caching support
- Logging
"""

import sys
import asyncio
import logging
from typing import List, Dict, Any, Optional, Type
from datetime import datetime
from abc import ABC, abstractmethod

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from pydantic import BaseModel, ValidationError

# Add parent directory for imports
sys.path.append('..')

from models.responses import (
    ToolResponse,
    ResponseMetadata,
    ErrorResponse,
    ResponseStatus,
    DataQualityAssessment,
)
from models.weather import LocationInfo


class BaseWeatherServer(ABC):
    """
    Base class for MCP weather servers with structured response support.
    
    Subclasses should implement:
    - get_tool_definitions(): Return tool schemas
    - handle_tool_call(): Process tool invocations
    """
    
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.app = Server(server_name)
        self.logger = self._setup_logger()
        self._setup_handlers()
    
    def _setup_logger(self) -> logging.Logger:
        """Configure server logging."""
        logger = logging.getLogger(self.server_name)
        logger.setLevel(logging.INFO)
        
        # Log to stderr to avoid interfering with stdio protocol
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter(f'[{self.server_name}] %(asctime)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(handler)
        
        return logger
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers."""
        @self.app.list_tools()
        async def list_tools():
            return self.get_tool_definitions()
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict):
            return await self._handle_tool_with_validation(name, arguments)
    
    @abstractmethod
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Return list of tool definitions for this server.
        
        Each tool should include:
        - name: Tool identifier
        - description: Human-readable description
        - inputSchema: JSON Schema for validation
        """
        pass
    
    @abstractmethod
    async def handle_tool_call(self, tool_name: str, validated_input: BaseModel) -> ToolResponse:
        """
        Handle a validated tool call.
        
        Args:
            tool_name: Name of the tool being called
            validated_input: Validated Pydantic model instance
            
        Returns:
            ToolResponse with structured data
        """
        pass
    
    @abstractmethod
    def get_input_model(self, tool_name: str) -> Type[BaseModel]:
        """
        Get the Pydantic model class for validating tool input.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Pydantic model class for input validation
        """
        pass
    
    async def _handle_tool_with_validation(self, name: str, arguments: dict) -> List[Dict[str, Any]]:
        """
        Handle tool call with input validation and error handling.
        
        This method:
        1. Validates input using Pydantic models
        2. Calls the tool implementation
        3. Formats response for MCP protocol
        4. Handles errors gracefully
        """
        start_time = datetime.utcnow()
        
        try:
            # Get the appropriate input model
            input_model_class = self.get_input_model(name)
            
            # Validate input
            try:
                validated_input = input_model_class(**arguments)
            except ValidationError as e:
                # Create user-friendly error message
                errors = []
                for error in e.errors():
                    field = " -> ".join(str(f) for f in error['loc'])
                    msg = error['msg']
                    errors.append(f"{field}: {msg}")
                
                error_response = ErrorResponse(
                    error_type="ValidationError",
                    error_message=f"Invalid input for {name}",
                    error_details={"validation_errors": errors},
                    suggestions=[
                        "Check the input parameters match the expected format",
                        "Ensure all required fields are provided",
                    ]
                )
                
                return error_response.to_tool_response().to_legacy_format()
            
            # Call the actual tool implementation
            self.logger.info(f"Calling tool: {name}")
            response = await self.handle_tool_call(name, validated_input)
            
            # Add processing time to metadata
            if response.metadata is None:
                response.metadata = ResponseMetadata(source=self.server_name)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            response.metadata.processing_time_ms = processing_time
            
            # Log successful call
            self.logger.info(
                f"Tool {name} completed in {processing_time:.0f}ms"
            )
            
            # Return in MCP format
            return response.to_legacy_format()  # Use legacy format for compatibility
            
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"Error in tool {name}: {str(e)}", exc_info=True)
            
            error_response = ErrorResponse(
                error_type=type(e).__name__,
                error_message=str(e),
                retry_possible=True,
                suggestions=["Check your input and try again", "Contact support if the issue persists"]
            )
            
            return error_response.to_tool_response().to_legacy_format()
    
    def create_response(
        self,
        text: str,
        data: BaseModel,
        status: ResponseStatus = ResponseStatus.SUCCESS,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        Helper to create a standard tool response.
        
        Args:
            text: Human-readable summary
            data: Structured data model
            status: Response status
            metadata: Additional metadata
            
        Returns:
            Configured ToolResponse
        """
        response_metadata = ResponseMetadata(
            source=self.server_name,
            cache_hit=False,
        )
        
        if metadata:
            for key, value in metadata.items():
                setattr(response_metadata, key, value)
        
        return ToolResponse(
            type="structured",
            text=text,
            data=data,
            status=status,
            metadata=response_metadata
        )
    
    async def run(self):
        """Run the MCP server."""
        self.logger.info(f"Starting {self.server_name} MCP Server...")
        self.logger.info(f"Available at: stdio://python {sys.argv[0]}")
        
        try:
            async with stdio_server() as streams:
                await self.app.run(
                    streams[0],
                    streams[1],
                    InitializationOptions(
                        server_name=self.server_name,
                        server_version="2.0.0",  # Updated for structured responses
                        capabilities={
                            "tools": {},
                            "experimental": {
                                "structured_responses": True
                            }
                        }
                    )
                )
        except Exception as e:
            self.logger.error(f"Server error: {e}", exc_info=True)
            raise