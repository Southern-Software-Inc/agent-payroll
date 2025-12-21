"""
Core Constants and Configuration
Module ID: APEX-CONFIG-000
Version: 0.1.0

Central configuration point for all APEX subsystems.

VERSION CONTROL FOOTER
File: src/core/constants.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

from typing import Dict, Any
from pathlib import Path
import os

# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"
DOCS_DIR = PROJECT_ROOT / "docs"
AGENTS_DIR = PROJECT_ROOT / "agents"
HOOKS_DIR = PROJECT_ROOT / "hooks"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TEMP_DIR = PROJECT_ROOT / "temp"
WORKFLOW_DIR = PROJECT_ROOT / "workflow"
TODO_DIR = WORKFLOW_DIR / "[TODO]"
COMPLETED_DIR = WORKFLOW_DIR / "completed"

# ============================================================================
# MCP AND TRANSPORT
# ============================================================================

MAX_MESSAGE_SIZE = 512 * 1024  # 512 KB
BUFFER_SIZE = 2 * 1024 * 1024  # 2 MB circular buffer
BUFFER_BACKPRESSURE_THRESHOLD = 0.90  # 90% capacity triggers SIG_BUSY
REQUEST_TIMEOUT_SECONDS = 60
GARBAGE_COLLECTION_INTERVAL = 5

# ============================================================================
# MASTER COMPENSATION ENGINE (MCE)
# ============================================================================

LEDGER_FILE = PROJECT_ROOT / "ledger_master.json"
LEDGER_BACKUP_DIR = TEMP_DIR / "ledger_backups"
LEDGER_VERSION = "3.0.1"
SYSTEM_CURRENCY = "APX"

# Economic Parameters
DEFAULT_BASE_PAY_RATE = 85.00  # APX per hour equivalent
DEFAULT_COMPLEXITY_ACCESS = 3  # Max complexity level (1-5)
DEFAULT_BOND_RATE = 0.25  # 25% stake required
DEFAULT_ROYALTY_SHARE = 0.05  # 5% of future code reuse revenue
DEFAULT_PENALTY_MULTIPLIER = 1.5  # Severity of fines

INITIAL_SYSTEM_BANK_BALANCE = 10000.00
INITIAL_AGENT_BALANCE = 100.00

# Complexity multipliers
COMPLEXITY_MULTIPLIERS = {
    "simple": 1.0,
    "medium": 1.5,
    "complex": 2.5,
    "expert": 5.0,
}

# Agent Tiers
AGENT_TIERS = ["novice", "established", "advanced", "expert", "master"]

# ============================================================================
# SOUL PARSER & AGENT PERSONAS
# ============================================================================

PERSONA_FILE_EXTENSION = ".md"
PERSONA_FRONTMATTER_DELIMITER = "---"

# Required YAML fields in agent personas
REQUIRED_PERSONA_FIELDS = {
    "agent_id": str,
    "name": str,
    "role": str,
    "tier": str,
    "economics": dict,
    "cognition": dict,
    "permissions": dict,
    "evolution": dict,
}

# ============================================================================
# HYPERVISOR & HOOKS
# ============================================================================

HOOKS_MANIFEST_FILE = PROJECT_ROOT / "hooks" / "hooks_manifest.json"
DEFAULT_HOOK_POLICY = "strict-isolation"

# Hook priority ranges
HOOK_PRIORITY_SYSTEM_INTEGRITY = range(1, 21)  # 1-20
HOOK_PRIORITY_SECURITY_SAFETY = range(21, 51)  # 21-50
HOOK_PRIORITY_OPTIMIZATION = range(51, 81)  # 51-80
HOOK_PRIORITY_RECOVERY_LOGGING = range(81, 101)  # 81-100

# ============================================================================
# SEMANTIC MEMORY & VECTOR STORE
# ============================================================================

VECTOR_STORE_BACKEND = "chromadb"  # Options: "chromadb", "faiss"
VECTOR_EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_DIMENSION = 1536
VECTOR_DISTANCE_METRIC = "cosine"

# HNSW Parameters
HNSW_M = 16  # Max connections per node
HNSW_EF_CONSTRUCTION = 200  # Index construction parameter
HNSW_EF_SEARCH = 100  # Search parameter

# Semantic Sieve Thresholds
SEMANTIC_UTILITY_THRESHOLD = 0.3  # Minimum utility score to be embedded
CHUNK_SIZE_TOKENS = 1024
CHUNK_OVERLAP_TOKENS = 128

# ============================================================================
# LOGGING AND DEBUGGING
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = TEMP_DIR / "apex.log"
ENABLE_PERFORMANCE_PROFILING = False

# ============================================================================
# JSON-RPC CONFIGURATION
# ============================================================================

JSONRPC_VERSION = "2.0"

# Error codes
ERROR_CODES = {
    "fiscal_insolvency": -32000,
    "sandbox_escape_attempt": -32001,
    "z3_verification_failure": -32002,
    "context_window_exceeded": -32003,
    "persona_corruption": -32004,
    "ledger_integrity_violation": -32005,
}

# ============================================================================
# DOCKER SANDBOX (future)
# ============================================================================

DOCKER_IMAGE_BASE = "apex-sandbox:latest"
SANDBOX_TIMEOUT_SECONDS = 30
SANDBOX_MEMORY_LIMIT = "512m"
SANDBOX_CPU_LIMIT = "1"

# ============================================================================
# SYSTEM CONFIGURATION OBJECT
# ============================================================================

SYSTEM_CONFIG: Dict[str, Any] = {
    "version": "0.1.0",
    "project_root": str(PROJECT_ROOT),
    "environment": os.getenv("APEX_ENV", "development"),
    "debug": os.getenv("APEX_DEBUG", "true").lower() == "true",
    "paths": {
        "project_root": str(PROJECT_ROOT),
        "src": str(SRC_DIR),
        "tests": str(TESTS_DIR),
        "docs": str(DOCS_DIR),
        "agents": str(AGENTS_DIR),
        "hooks": str(HOOKS_DIR),
        "scripts": str(SCRIPTS_DIR),
        "ledger": str(LEDGER_FILE),
    },
    "ledger": {
        "file": str(LEDGER_FILE),
        "version": LEDGER_VERSION,
        "currency": SYSTEM_CURRENCY,
        "initial_system_balance": INITIAL_SYSTEM_BANK_BALANCE,
    },
    "mce": {
        "default_base_pay_rate": DEFAULT_BASE_PAY_RATE,
        "default_complexity_access": DEFAULT_COMPLEXITY_ACCESS,
        "default_bond_rate": DEFAULT_BOND_RATE,
        "default_royalty_share": DEFAULT_ROYALTY_SHARE,
    },
    "vector_store": {
        "backend": VECTOR_STORE_BACKEND,
        "embedding_model": VECTOR_EMBEDDING_MODEL,
        "dimension": VECTOR_DIMENSION,
        "distance_metric": VECTOR_DISTANCE_METRIC,
    },
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def ensure_directories_exist() -> None:
    """Create all necessary project directories if they don't exist."""
    directories = [
        SRC_DIR,
        TESTS_DIR,
        DOCS_DIR,
        AGENTS_DIR,
        HOOKS_DIR,
        SCRIPTS_DIR,
        TEMP_DIR,
        WORKFLOW_DIR,
        TODO_DIR,
        COMPLETED_DIR,
        LEDGER_BACKUP_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def get_config() -> Dict[str, Any]:
    """Return system configuration dictionary."""
    return SYSTEM_CONFIG.copy()
