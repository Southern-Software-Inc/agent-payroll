"""
Test Configuration and Fixtures
Module ID: APEX-TEST-000
Version: 0.1.0

VERSION CONTROL FOOTER
File: tests/conftest.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

import pytest
import tempfile
from pathlib import Path
from src.core.constants import ensure_directories_exist


@pytest.fixture(scope="session", autouse=True)
def initialize_project():
    """Initialize project directories before tests run."""
    ensure_directories_exist()


@pytest.fixture
def temp_ledger(tmp_path):
    """Provide a temporary ledger file path for testing."""
    return tmp_path / "test_ledger.json"


@pytest.fixture
def temp_agent_persona(tmp_path):
    """Provide a temporary agent persona file for testing."""
    return tmp_path / "test_agent.md"
