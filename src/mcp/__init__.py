"""
MCP Module - Model Context Protocol Implementation
Module ID: APEX-ARCH-000
Version: 0.1.0

VERSION CONTROL FOOTER
File: src/mcp/__init__.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

from src.mcp.server import (
    MCPServer,
    mcp_server,
)

__all__ = [
    "MCPServer",
    "mcp_server",
]
