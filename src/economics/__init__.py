"""
Economics Module - Financial State Management
Module ID: APEX-ECON-000
Version: 0.1.0

VERSION CONTROL FOOTER
File: src/economics/__init__.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

from src.economics.ledger import (
    MasterCompensationEngine,
    get_mce,
    AgentFinancials,
    AgentPerformance,
    AgentMetadata,
    Transaction,
)

__all__ = [
    "MasterCompensationEngine",
    "get_mce",
    "AgentFinancials",
    "AgentPerformance",
    "AgentMetadata",
    "Transaction",
]
