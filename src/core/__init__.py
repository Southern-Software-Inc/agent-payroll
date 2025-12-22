"""
Core Subsystems Module
Module ID: APEX-CORE-000
Version: 0.1.0

Exports core constants and utilities.

VERSION CONTROL FOOTER
File: src/core/__init__.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

from src.core.constants import (
    SYSTEM_CONFIG,
    PROJECT_ROOT,
    SRC_DIR,
    TESTS_DIR,
    DOCS_DIR,
    AGENTS_DIR,
    HOOKS_DIR,
    SCRIPTS_DIR,
    TEMP_DIR,
    WORKFLOW_DIR,
    LEDGER_FILE,
    ensure_directories_exist,
    get_config,
)

from src.core.dream_cycle import (
    DreamCycle,
    DreamCycleScheduler,
    DreamSessionResult,
    get_dream_cycle,
    get_dream_scheduler,
)

__all__ = [
    "SYSTEM_CONFIG",
    "PROJECT_ROOT",
    "SRC_DIR",
    "TESTS_DIR",
    "DOCS_DIR",
    "AGENTS_DIR",
    "HOOKS_DIR",
    "SCRIPTS_DIR",
    "TEMP_DIR",
    "WORKFLOW_DIR",
    "LEDGER_FILE",
    "ensure_directories_exist",
    "get_config",
    "DreamCycle",
    "DreamCycleScheduler",
    "DreamSessionResult",
    "get_dream_cycle",
    "get_dream_scheduler",
]
