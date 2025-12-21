"""
Agents Module - Agent Management and Personas
Module ID: APEX-SOUL-000
Version: 0.1.0

VERSION CONTROL FOOTER
File: src/agents/__init__.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

from src.agents.soul_parser import (
    SoulParser,
    get_soul_parser,
    AgentGenotype,
    AgentEconomics,
    AgentCognition,
    AgentPermissions,
    AgentEvolution,
    PersonaCorruptionError,
)

__all__ = [
    "SoulParser",
    "get_soul_parser",
    "AgentGenotype",
    "AgentEconomics",
    "AgentCognition",
    "AgentPermissions",
    "AgentEvolution",
    "PersonaCorruptionError",
]
