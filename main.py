"""
APEX Agent Payroll System - Main Entry Point
Module ID: APEX-MAIN-001
Version: 0.1.0

This is the main entry point for the APEX Agent Payroll System.
It initializes all subsystems and provides the primary interface.

VERSION CONTROL FOOTER
File: main.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core import ensure_directories_exist, SYSTEM_CONFIG
from src.economics import get_mce
from src.agents import get_soul_parser
from src.mcp import mcp_server


# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


# ============================================================================
# INITIALIZATION
# ============================================================================


def initialize_system() -> None:
    """Initialize all APEX subsystems."""
    logger.info("Initializing APEX Agent Payroll System...")

    # Ensure all directories exist
    ensure_directories_exist()
    logger.info("✓ Project directories initialized")

    # Initialize MCE
    mce = get_mce()
    logger.info("✓ Master Compensation Engine ready")

    # Initialize Soul Parser
    soul_parser = get_soul_parser()
    available_agents = soul_parser.list_available_agents()
    logger.info(f"✓ Soul Parser ready ({len(available_agents)} agents found)")

    # Initialize MCP Server
    # Use the global MCP server instance
    pass
    logger.info("✓ MCP Server ready")

    logger.info("APEX System initialized successfully!")
    logger.info(f"Configuration: {SYSTEM_CONFIG['environment']}")


# ============================================================================
# CORE OPERATIONS
# ============================================================================


async def main():
    """Main async entry point."""
    try:
        initialize_system()

        # TODO: Start main event loop
        logger.info("System ready for operation")

        # For now, just print system status
        mce = get_mce()
        soul_parser = get_soul_parser()

        print("\n" + "=" * 60)
        print("APEX AGENT PAYROLL SYSTEM - STATUS REPORT")
        print("=" * 60)

        ledger = mce.get_ledger_snapshot()
        print(f"\nSystem Bank Balance: {ledger['system_bank']['balance']} APX")
        print(f"Active Agents: {len(ledger['agents'])}")
        print(f"Transactions: {len(ledger['transaction_log'])}")

        available_agents = soul_parser.list_available_agents()
        print(f"\nAvailable Agent Personas: {len(available_agents)}")
        for agent_id in available_agents:
            print(f"  - {agent_id}")

        print("\n" + "=" * 60)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
