"""
APEX Agent Payroll System - Main Entry Point
Module ID: APEX-MAIN-000
Version: 0.1.0

This is the root __init__.py for the APEX Agent Payroll System.
Coordinates initialization of core subsystems: MCP, MCE, Soul Parser, and Hypervisor.

VERSION CONTROL FOOTER
File: src/__init__.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

__version__ = "0.1.0"
__author__ = "Apex Development Team"

# Core subsystem imports (lazy-loaded to avoid circular dependencies)
from src.core.constants import SYSTEM_CONFIG

__all__ = [
    "SYSTEM_CONFIG",
]
