"""
MCP Server - Model Context Protocol Hub
Module ID: APEX-ARCH-001
Version: 0.1.0

The nervous system of the Apex ecosystem. Manages JSON-RPC 2.0 communication,
asynchronous I/O, and orchestration of agents and tools.

VERSION CONTROL FOOTER
File: src/mcp/server.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timezone, timedelta
from src.core.constants import (
    JSONRPC_VERSION,
    REQUEST_TIMEOUT_SECONDS,
    GARBAGE_COLLECTION_INTERVAL,
    ERROR_CODES,
    LEDGER_FILE,
)
from src.economics import get_mce


class JSONRPCError(Exception):
    """Base class for JSON-RPC errors."""

    def __init__(self, code: int, message: str, data: Optional[Dict[str, Any]] = None):
        """Initialize JSON-RPC error."""
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-RPC error object."""
        error_dict = {"code": self.code, "message": self.message}
        if self.data:
            error_dict["data"] = self.data
        return error_dict


class ActiveRequestRegistry:
    """
    Tracks active JSON-RPC requests with TTL and timeout handling.

    Stores request metadata and automatically garbage-collects expired requests.
    """

    def __init__(self, ttl_seconds: int = REQUEST_TIMEOUT_SECONDS):
        """Initialize registry."""
        self.ttl_seconds = ttl_seconds
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def register_request(
        self, request_id: str, method: str, params: Dict[str, Any]
    ) -> None:
        """Register a new request."""
        async with self._lock:
            self._registry[request_id] = {
                "method": method,
                "params": params,
                "registered_at": datetime.now(timezone.utc),
            }

    async def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get request metadata."""
        async with self._lock:
            return self._registry.get(request_id)

    async def complete_request(self, request_id: str) -> None:
        """Mark request as completed."""
        async with self._lock:
            if request_id in self._registry:
                del self._registry[request_id]

    async def garbage_collect(self) -> list[str]:
        """
        Remove expired requests and return list of expired IDs.

        Returns:
            List of request IDs that expired.
        """
        expired = []
        now = datetime.now(timezone.utc)

        async with self._lock:
            for request_id, metadata in list(self._registry.items()):
                age = now - metadata["registered_at"]
                if age.total_seconds() > self.ttl_seconds:
                    expired.append(request_id)
                    del self._registry[request_id]

        return expired


class MCPServer:
    """
    Model Context Protocol (MCP) Server.

    Core hub for JSON-RPC 2.0 communication with LLM clients.
    Implements asynchronous I/O, request routing, and error handling.
    """

    def __init__(self):
        """Initialize MCP Server."""
        self.request_registry = ActiveRequestRegistry()
        self._handlers: Dict[str, Callable] = {}
        self._resources: Dict[str, Callable] = {}
        self._tools: Dict[str, Callable] = {}
        self._mce = get_mce()

    def register_handler(self, method: str, handler: Callable) -> None:
        """
        Register a JSON-RPC method handler.

        Args:
            method: JSON-RPC method name.
            handler: Async callable that handles the method.
        """
        self._handlers[method] = handler

    def register_resource(self, uri_scheme: str, handler: Callable) -> None:
        """
        Register a resource handler.

        Args:
            uri_scheme: URI scheme (e.g., "payroll://").
            handler: Async callable that retrieves the resource.
        """
        self._resources[uri_scheme] = handler

    def register_tool(self, tool_name: str, tool_handler: Callable) -> None:
        """
        Register a tool.

        Args:
            tool_name: Tool identifier.
            tool_handler: Async callable that executes the tool.
        """
        self._tools[tool_name] = tool_handler

    async def handle_request(self, raw_message: str) -> str:
        """
        Process a JSON-RPC 2.0 request.

        Args:
            raw_message: JSON-RPC request string.

        Returns:
            JSON-RPC response string.
        """
        try:
            request = json.loads(raw_message)
        except json.JSONDecodeError:
            return self._error_response(None, -32700, "Parse error")

        # Validate JSON-RPC structure
        if not isinstance(request, dict):
            return self._error_response(None, -32600, "Invalid Request")

        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        jsonrpc = request.get("jsonrpc")

        # Check version
        if jsonrpc != JSONRPC_VERSION:
            return self._error_response(request_id, -32600, "Invalid Request: jsonrpc version")

        if not method:
            return self._error_response(request_id, -32600, "Invalid Request: missing method")

        # Register request
        if request_id:
            await self.request_registry.register_request(request_id, method, params)

        try:
            # Route to handler
            if method in self._handlers:
                result = await self._handlers[method](params)
                if request_id:
                    return self._success_response(request_id, result)
                return ""  # Notification, no response
            else:
                return self._error_response(request_id, -32601, "Method not found")
        except JSONRPCError as e:
            return self._error_response(request_id, e.code, e.message, e.data)
        except Exception as e:
            return self._error_response(request_id, -32603, "Internal error", str(e))
        finally:
            if request_id:
                await self.request_registry.complete_request(request_id)

    def _success_response(self, request_id: str, result: Any) -> str:
        """Create a JSON-RPC success response."""
        response = {"jsonrpc": JSONRPC_VERSION, "result": result, "id": request_id}
        return json.dumps(response)

    def _error_response(
        self, request_id: Optional[str], code: int, message: str, data: Optional[str] = None
    ) -> str:
        """Create a JSON-RPC error response."""
        error = {"code": code, "message": message}
        if data:
            error["data"] = data
        response = {"jsonrpc": JSONRPC_VERSION, "error": error, "id": request_id}
        return json.dumps(response)

    async def start_garbage_collection(self) -> None:
        """Start background garbage collection task."""
        while True:
            await asyncio.sleep(GARBAGE_COLLECTION_INTERVAL)
            expired = await self.request_registry.garbage_collect()
            if expired:
                # TODO: Log expired requests and trigger performance penalties
                pass


# Global MCP Server instance
_mcp_server_instance: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """Get or create the global MCP Server instance."""
    global _mcp_server_instance
    if _mcp_server_instance is None:
        _mcp_server_instance = MCPServer()
    return _mcp_server_instance
