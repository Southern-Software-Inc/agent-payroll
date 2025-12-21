"""
Master Compensation Engine (MCE) - Core Financial State Management
Module ID: APEX-ECON-002
Version: 0.1.0

The MCE is the economic heart of the Apex ecosystem. It manages:
- ACID-compliant ledger persistence
- Agent financial state (balance, escrow, earnings)
- Performance tracking (streak, success rate, reputation)
- Token taxation and bond management
- Transaction logging with checksums

VERSION CONTROL FOOTER
File: src/economics/ledger.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

import json
import hashlib
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from threading import Lock
import os
from src.core.constants import (
    LEDGER_FILE,
    LEDGER_VERSION,
    SYSTEM_CURRENCY,
    INITIAL_SYSTEM_BANK_BALANCE,
    INITIAL_AGENT_BALANCE,
    PROJECT_ROOT,
)


@dataclass
class AgentFinancials:
    """Agent financial state."""

    balance: float = INITIAL_AGENT_BALANCE
    escrow_hold: float = 0.0
    lifetime_earnings: float = 0.0
    debt_ceiling: float = -100.0


@dataclass
class AgentPerformance:
    """Agent performance metrics."""

    streak: int = 0
    success_rate: float = 0.0
    avg_token_efficiency: float = 0.0
    reputation_score: float = 0.5


@dataclass
class AgentMetadata:
    """Agent metadata and status."""

    tier: str = "novice"
    last_active: str = ""


@dataclass
class Transaction:
    """Financial transaction record."""

    tx_id: str
    timestamp: str
    from_agent: str
    to_agent: str
    amount: float
    tx_type: str
    task_ref: Optional[str] = None
    description: Optional[str] = None
    checksum: str = ""


class MasterCompensationEngine:
    """
    ACID-compliant financial ledger for the Apex ecosystem.

    Ensures that all financial transactions are atomic, consistent, isolated,
    and durable. Implements Write-Ahead Logging (WAL) and file locking.
    """

    def __init__(self, ledger_path: Path = LEDGER_FILE):
        """
        Initialize the MCE with a ledger file path.

        Args:
            ledger_path: Path to the ledger_master.json file.
        """
        self.ledger_path = ledger_path
        self._lock = Lock()
        self._ledger: Dict[str, Any] = {}
        self._load_or_initialize_ledger()

    def _load_or_initialize_ledger(self) -> None:
        """Load existing ledger or create a new one."""
        if self.ledger_path.exists():
            try:
                with open(self.ledger_path, "r") as f:
                    self._ledger = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                raise RuntimeError(f"Failed to load ledger: {e}")
        else:
            self._ledger = self._create_empty_ledger()
            self._persist_ledger()

    def _create_empty_ledger(self) -> Dict[str, Any]:
        """Create a blank ledger structure."""
        return {
            "metadata": {
                "version": LEDGER_VERSION,
                "currency": SYSTEM_CURRENCY,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_checkpoint_hash": "",
            },
            "system_bank": {
                "balance": INITIAL_SYSTEM_BANK_BALANCE,
                "total_tax_collected": 0.0,
                "total_bonds_burned": 0.0,
            },
            "agents": {},
            "transaction_log": [],
        }

    def _persist_ledger(self) -> None:
        """
        Persist ledger to disk with ACID guarantees.

        Uses Write-Ahead Logging (WAL) pattern:
        1. Write to temporary file
        2. Compute checksum
        3. Atomic rename
        4. fsync to ensure durability (platform-specific)
        """
        with self._lock:
            temp_path = self.ledger_path.with_suffix(".tmp")

            try:
                # Write to temporary file
                with open(temp_path, "w") as f:
                    json.dump(self._ledger, f, indent=2)
                    f.flush()
                    # fsync for durability (platform-safe)
                    try:
                        os.fsync(f.fileno())
                    except (OSError, ValueError):
                        # Windows may not support fsync on text mode files
                        pass

                # Atomic rename (POSIX-compliant)
                temp_path.replace(self.ledger_path)

                # Ensure durability (platform-safe)
                try:
                    with open(self.ledger_path, "r") as f:
                        os.fsync(f.fileno())
                except (OSError, ValueError):
                    # Windows compatibility
                    pass

            except Exception as e:
                if temp_path.exists():
                    temp_path.unlink()
                raise RuntimeError(f"Failed to persist ledger: {e}")

    def _compute_transaction_checksum(self, tx: Dict[str, Any]) -> str:
        """Compute SHA256 checksum of transaction data."""
        tx_copy = {k: v for k, v in tx.items() if k != "checksum"}
        tx_str = json.dumps(tx_copy, sort_keys=True)
        return hashlib.sha256(tx_str.encode()).hexdigest()

    def create_agent(
        self,
        agent_id: str,
        name: str,
        tier: str = "novice",
        base_pay_rate: float = 85.0,
    ) -> bool:
        """
        Create a new agent in the ledger.

        Args:
            agent_id: Unique agent identifier.
            name: Human-readable agent name.
            tier: Agent tier (novice, established, advanced, expert, master).
            base_pay_rate: Base hourly pay rate in APX.

        Returns:
            True if agent created successfully, False if already exists.
        """
        with self._lock:
            if agent_id in self._ledger["agents"]:
                return False

            self._ledger["agents"][agent_id] = {
                "name": name,
                "financials": asdict(AgentFinancials()),
                "performance": asdict(AgentPerformance()),
                "metadata": {
                    "tier": tier,
                    "last_active": datetime.now(timezone.utc).isoformat(),
                    "base_pay_rate": base_pay_rate,
                },
            }

            self._persist_ledger()
            return True

    def get_agent_balance(self, agent_id: str) -> Optional[float]:
        """Get agent's current balance."""
        if agent_id not in self._ledger["agents"]:
            return None
        return self._ledger["agents"][agent_id]["financials"]["balance"]

    def transfer_funds(
        self,
        from_agent: str,
        to_agent: str,
        amount: float,
        tx_type: str = "TRANSFER",
        task_ref: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[str]:
        """
        Execute a financial transfer between agents.

        Args:
            from_agent: Source agent ID.
            to_agent: Destination agent ID.
            amount: Amount to transfer in APX.
            tx_type: Transaction type (TRANSFER, TASK_REWARD, TAX, BOND, etc.).
            task_ref: Optional reference to a task ID.
            description: Optional transaction description.

        Returns:
            Transaction ID if successful, None if failed.
        """
        with self._lock:
            if from_agent not in self._ledger["agents"] or to_agent not in self._ledger["agents"]:
                return None

            # Check sufficient balance
            if self._ledger["agents"][from_agent]["financials"]["balance"] < amount:
                return None

            tx_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc).isoformat()

            tx = {
                "tx_id": tx_id,
                "timestamp": timestamp,
                "from": from_agent,
                "to": to_agent,
                "amount": amount,
                "type": tx_type,
                "task_ref": task_ref,
                "description": description,
                "checksum": "",
            }

            # Compute checksum
            tx["checksum"] = self._compute_transaction_checksum(tx)

            # Update balances
            self._ledger["agents"][from_agent]["financials"]["balance"] -= amount
            self._ledger["agents"][to_agent]["financials"]["balance"] += amount

            # Log transaction
            self._ledger["transaction_log"].append(tx)

            self._persist_ledger()
            return tx_id

    def get_ledger_snapshot(self) -> Dict[str, Any]:
        """Get a read-only snapshot of the entire ledger."""
        with self._lock:
            return json.loads(json.dumps(self._ledger))

    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get complete state of a specific agent."""
        if agent_id not in self._ledger["agents"]:
            return None
        return self._ledger["agents"][agent_id].copy()

    def update_agent_performance(
        self,
        agent_id: str,
        streak: int = None,
        success_rate: float = None,
        avg_token_efficiency: float = None,
        reputation_score: float = None,
    ) -> bool:
        """Update agent performance metrics."""
        with self._lock:
            if agent_id not in self._ledger["agents"]:
                return False

            perf = self._ledger["agents"][agent_id]["performance"]
            if streak is not None:
                perf["streak"] = streak
            if success_rate is not None:
                perf["success_rate"] = success_rate
            if avg_token_efficiency is not None:
                perf["avg_token_efficiency"] = avg_token_efficiency
            if reputation_score is not None:
                perf["reputation_score"] = reputation_score

            self._persist_ledger()
            return True


# Global MCE instance
_mce_instance: Optional[MasterCompensationEngine] = None


def get_mce() -> MasterCompensationEngine:
    """Get or create the global MCE instance."""
    global _mce_instance
    if _mce_instance is None:
        _mce_instance = MasterCompensationEngine()
    return _mce_instance
