"""
MCP Server Implementation
Module ID: APEX-MCP-SERVER-001
Version: 0.1.0

Implements the Model Context Protocol (MCP) server with tool execution
capabilities for the APEX Agent Payroll System.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class ToolStatus(Enum):
    """Tool execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Tool:
    """Represents an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable
    category: str = "general"
    timeout: float = 30.0
    async_handler: bool = False


@dataclass
class ToolExecution:
    """Represents a tool execution."""
    id: str
    tool_name: str
    arguments: Dict[str, Any]
    status: ToolStatus = ToolStatus.IDLE
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    """Registry for MCP tools."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Tool] = {}
        self._categories: Dict[str, List[str]] = {}
        
        logger.info("ToolRegistry initialized")
    
    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool to register
        """
        self._tools[tool.name] = tool
        
        # Add to category
        if tool.category not in self._categories:
            self._categories[tool.category] = []
        if tool.name not in self._categories[tool.category]:
            self._categories[tool.category].append(tool.name)
        
        logger.info(f"Registered tool: {tool.name} in category {tool.category}")
    
    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            name: Tool name
            
        Returns:
            True if unregistered successfully
        """
        if name not in self._tools:
            return False
        
        tool = self._tools[name]
        
        # Remove from category
        if tool.category in self._categories and name in self._categories[tool.category]:
            self._categories[tool.category].remove(name)
        
        # Remove tool
        del self._tools[name]
        
        logger.info(f"Unregistered tool: {name}")
        return True
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self, category: str = None) -> List[Tool]:
        """
        List tools, optionally filtered by category.
        
        Args:
            category: Category filter
            
        Returns:
            List of tools
        """
        if category:
            tool_names = self._categories.get(category, [])
            return [self._tools[name] for name in tool_names if name in self._tools]
        return list(self._tools.values())
    
    def get_categories(self) -> List[str]:
        """Get all tool categories."""
        return list(self._categories.keys())


class MCPServer:
    """
    MCP Server with tool execution capabilities.
    
    Provides a complete MCP implementation with tool registry,
    execution management, and protocol handling.
    """
    
    def __init__(self, name: str = "apex-mcp-server", version: str = "0.1.0"):
        """
        Initialize the MCP server.
        
        Args:
            name: Server name
            version: Server version
        """
        self.name = name
        self.version = version
        self.tool_registry = ToolRegistry()
        self._executions: Dict[str, ToolExecution] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        
        # Register built-in tools
        self._register_builtin_tools()
        
        logger.info(f"MCP Server initialized: {name} v{version}")
    
    def _register_builtin_tools(self) -> None:
        """Register built-in MCP tools."""
        
        # List tools tool
        self.tool_registry.register_tool(Tool(
            name="list_tools",
            description="List all available tools",
            input_schema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category"
                    }
                }
            },
            handler=self._handle_list_tools,
            category="system"
        ))
        
        # Get tool info tool
        self.tool_registry.register_tool(Tool(
            name="get_tool_info",
            description="Get information about a specific tool",
            input_schema={
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "Name of the tool"
                    }
                },
                "required": ["tool_name"]
            },
            handler=self._handle_get_tool_info,
            category="system"
        ))
        
        # Execute tool tool
        self.tool_registry.register_tool(Tool(
            name="execute_tool",
            description="Execute a tool",
            input_schema={
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "Name of the tool to execute"
                    },
                    "arguments": {
                        "type": "object",
                        "description": "Arguments for the tool"
                    }
                },
                "required": ["tool_name"]
            },
            handler=self._handle_execute_tool,
            category="system",
            async_handler=True
        ))
        
        # Get execution status tool
        self.tool_registry.register_tool(Tool(
            name="get_execution_status",
            description="Get status of a tool execution",
            input_schema={
                "type": "object",
                "properties": {
                    "execution_id": {
                        "type": "string",
                        "description": "Execution ID"
                    }
                },
                "required": ["execution_id"]
            },
            handler=self._handle_get_execution_status,
            category="system"
        ))
        
        # Cancel execution tool
        self.tool_registry.register_tool(Tool(
            name="cancel_execution",
            description="Cancel a running tool execution",
            input_schema={
                "type": "object",
                "properties": {
                    "execution_id": {
                        "type": "string",
                        "description": "Execution ID"
                    }
                },
                "required": ["execution_id"]
            },
            handler=self._handle_cancel_execution,
            category="system"
        ))
    
    def _handle_list_tools(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_tools request."""
        category = arguments.get("category")
        tools = self.tool_registry.list_tools(category)
        
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                    "category": tool.category
                }
                for tool in tools
            ],
            "categories": self.tool_registry.get_categories()
        }
    
    def _handle_get_tool_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_tool_info request."""
        tool_name = arguments["tool_name"]
        tool = self.tool_registry.get_tool(tool_name)
        
        if not tool:
            return {
                "error": f"Tool not found: {tool_name}"
            }
        
        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
            "category": tool.category,
            "timeout": tool.timeout,
            "async_handler": tool.async_handler
        }
    
    async def _handle_execute_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle execute_tool request."""
        tool_name = arguments["tool_name"]
        tool_args = arguments.get("arguments", {})
        
        # Create execution
        execution_id = str(uuid.uuid4())
        execution = ToolExecution(
            id=execution_id,
            tool_name=tool_name,
            arguments=tool_args
        )
        
        self._executions[execution_id] = execution
        
        # Get tool
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            execution.status = ToolStatus.FAILED
            execution.error = f"Tool not found: {tool_name}"
            execution.completed_at = datetime.utcnow()
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": execution.error
            }
        
        # Execute tool
        try:
            execution.status = ToolStatus.RUNNING
            execution.started_at = datetime.utcnow()
            
            if tool.async_handler:
                # Async execution
                task = asyncio.create_task(
                    self._execute_tool_async(tool, tool_args, execution)
                )
                self._running_tasks[execution_id] = task
                
                # Wait for completion or timeout
                try:
                    await asyncio.wait_for(task, timeout=tool.timeout)
                except asyncio.TimeoutError:
                    task.cancel()
                    execution.status = ToolStatus.FAILED
                    execution.error = f"Tool execution timed out after {tool.timeout}s"
                    execution.completed_at = datetime.utcnow()
            else:
                # Sync execution
                result = tool.handler(tool_args)
                execution.result = result
                execution.status = ToolStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
            
            # Calculate duration
            if execution.started_at and execution.completed_at:
                execution.duration = (execution.completed_at - execution.started_at).total_seconds()
            
            # Clean up
            if execution_id in self._running_tasks:
                del self._running_tasks[execution_id]
            
            return {
                "execution_id": execution_id,
                "status": execution.status.value,
                "result": execution.result,
                "error": execution.error,
                "duration": execution.duration
            }
            
        except Exception as e:
            execution.status = ToolStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()
            
            # Clean up
            if execution_id in self._running_tasks:
                del self._running_tasks[execution_id]
            
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": execution.error
            }
    
    async def _execute_tool_async(
        self,
        tool: Tool,
        arguments: Dict[str, Any],
        execution: ToolExecution
    ) -> None:
        """Execute an async tool."""
        try:
            result = await tool.handler(arguments)
            execution.result = result
            execution.status = ToolStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
        except Exception as e:
            execution.status = ToolStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()
    
    def _handle_get_execution_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_execution_status request."""
        execution_id = arguments["execution_id"]
        execution = self._executions.get(execution_id)
        
        if not execution:
            return {
                "error": f"Execution not found: {execution_id}"
            }
        
        return {
            "execution_id": execution.id,
            "tool_name": execution.tool_name,
            "status": execution.status.value,
            "result": execution.result,
            "error": execution.error,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "duration": execution.duration
        }
    
    def _handle_cancel_execution(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cancel_execution request."""
        execution_id = arguments["execution_id"]
        execution = self._executions.get(execution_id)
        
        if not execution:
            return {
                "error": f"Execution not found: {execution_id}"
            }
        
        if execution.status != ToolStatus.RUNNING:
            return {
                "error": f"Execution is not running: {execution_id}"
            }
        
        # Cancel task if running
        if execution_id in self._running_tasks:
            task = self._running_tasks[execution_id]
            task.cancel()
            del self._running_tasks[execution_id]
        
        # Update execution
        execution.status = ToolStatus.CANCELLED
        execution.completed_at = datetime.utcnow()
        
        return {
            "execution_id": execution_id,
            "status": "cancelled"
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP request.
        
        Args:
            request: MCP request
            
        Returns:
            MCP response
        """
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "tools/list":
                return self._handle_list_tools(params)
            elif method == "tools/get":
                return self._handle_get_tool_info(params)
            elif method == "tools/call":
                return await self._handle_execute_tool(params)
            elif method == "execution/status":
                return self._handle_get_execution_status(params)
            elif method == "execution/cancel":
                return self._handle_cancel_execution(params)
            else:
                return {
                    "error": f"Unknown method: {method}"
                }
                
        except Exception as e:
            logger.error(f"Error handling MCP request: {str(e)}")
            return {
                "error": str(e)
            }
    
    def get_executions(self, status: ToolStatus = None) -> List[ToolExecution]:
        """
        Get tool executions, optionally filtered by status.
        
        Args:
            status: Status filter
            
        Returns:
            List of executions
        """
        executions = list(self._executions.values())
        
        if status:
            executions = [e for e in executions if e.status == status]
        
        # Sort by start time (newest first)
        executions.sort(key=lambda e: e.started_at or datetime.min, reverse=True)
        
        return executions
    
    def cleanup_executions(self, max_age_hours: float = 24.0) -> int:
        """
        Clean up old executions.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of executions cleaned up
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        to_remove = [
            execution_id for execution_id, execution in self._executions.items()
            if execution.started_at and execution.started_at < cutoff_time
        ]
        
        for execution_id in to_remove:
            del self._executions[execution_id]
            if execution_id in self._running_tasks:
                self._running_tasks[execution_id].cancel()
                del self._running_tasks[execution_id]
        
        logger.info(f"Cleaned up {len(to_remove)} old executions")
        return len(to_remove)


# Global MCP server instance
mcp_server = MCPServer()
