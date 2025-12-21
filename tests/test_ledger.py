"""
Unit Tests for Master Compensation Engine
Module ID: APEX-TEST-ECON-001
Version: 0.1.0

VERSION CONTROL FOOTER
File: tests/test_ledger.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

import pytest
from pathlib import Path
from src.economics.ledger import MasterCompensationEngine


def test_ledger_initialization(temp_ledger):
    """Test that MCE initializes with empty ledger."""
    mce = MasterCompensationEngine(temp_ledger)
    snapshot = mce.get_ledger_snapshot()

    assert snapshot["metadata"]["currency"] == "APX"
    assert snapshot["system_bank"]["balance"] == 10000.00
    assert len(snapshot["agents"]) == 0
    assert len(snapshot["transaction_log"]) == 0


def test_create_agent(temp_ledger):
    """Test agent creation."""
    mce = MasterCompensationEngine(temp_ledger)

    success = mce.create_agent("test_agent_01", "Test Agent", tier="novice", base_pay_rate=50.0)
    assert success is True

    agent_state = mce.get_agent_state("test_agent_01")
    assert agent_state["metadata"]["tier"] == "novice"
    assert agent_state["financials"]["balance"] == 100.0


def test_create_duplicate_agent_fails(temp_ledger):
    """Test that creating duplicate agent fails."""
    mce = MasterCompensationEngine(temp_ledger)

    mce.create_agent("test_agent_01", "Test Agent")
    success = mce.create_agent("test_agent_01", "Test Agent")

    assert success is False


def test_transfer_funds(temp_ledger):
    """Test fund transfer between agents."""
    mce = MasterCompensationEngine(temp_ledger)

    mce.create_agent("agent_a", "Agent A")
    mce.create_agent("agent_b", "Agent B")

    # Agent A has initial balance of 100 APX
    tx_id = mce.transfer_funds("agent_a", "agent_b", 30.0)

    assert tx_id is not None
    assert mce.get_agent_balance("agent_a") == 70.0
    assert mce.get_agent_balance("agent_b") == 130.0


def test_transfer_insufficient_funds(temp_ledger):
    """Test that transfer fails with insufficient funds."""
    mce = MasterCompensationEngine(temp_ledger)

    mce.create_agent("agent_a", "Agent A")
    mce.create_agent("agent_b", "Agent B")

    # Try to transfer more than available
    tx_id = mce.transfer_funds("agent_a", "agent_b", 200.0)

    assert tx_id is None
    assert mce.get_agent_balance("agent_a") == 100.0
    assert mce.get_agent_balance("agent_b") == 100.0


def test_update_agent_performance(temp_ledger):
    """Test updating agent performance metrics."""
    mce = MasterCompensationEngine(temp_ledger)

    mce.create_agent("test_agent_01", "Test Agent")
    success = mce.update_agent_performance(
        "test_agent_01", streak=5, success_rate=0.95, reputation_score=0.92
    )

    assert success is True

    agent_state = mce.get_agent_state("test_agent_01")
    assert agent_state["performance"]["streak"] == 5
    assert agent_state["performance"]["success_rate"] == 0.95
    assert agent_state["performance"]["reputation_score"] == 0.92


def test_ledger_persistence(temp_ledger):
    """Test that ledger persists to disk."""
    mce1 = MasterCompensationEngine(temp_ledger)
    mce1.create_agent("persistent_agent", "Persistent Agent")
    mce1.transfer_funds("system_bank", "persistent_agent", 50.0)

    # Create new instance and verify data persists
    mce2 = MasterCompensationEngine(temp_ledger)
    agent_state = mce2.get_agent_state("persistent_agent")

    assert agent_state is not None
    assert agent_state["financials"]["balance"] == 150.0
