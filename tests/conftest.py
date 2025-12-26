"""
Pytest Configuration and Fixtures
Module ID: APEX-TEST-001
Version: 0.1.0

Centralized test configuration with fixtures for all modules.
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import logging

# Disable logging during tests
logging.getLogger().setLevel(logging.CRITICAL)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def initialize_test_environment():
    """Initialize test environment."""
    from src.core import ensure_directories_exist
    ensure_directories_exist()


@pytest.fixture
def temp_dir(tmp_path):
    """Provide temporary directory."""
    return tmp_path


@pytest.fixture
def temp_ledger(temp_dir):
    """Provide temporary ledger file."""
    return temp_dir / "test_ledger.json"


@pytest.fixture
def temp_agent_persona(temp_dir):
    """Provide temporary agent persona file."""
    return temp_dir / "test_agent.md"


@pytest.fixture
def mock_mce():
    """Mock Master Compensation Engine."""
    mce = Mock()
    mce.create_agent = Mock(return_value=True)
    mce.transfer_funds = Mock(return_value="test_tx_id")
    mce.get_agent_balance = Mock(return_value=100.0)
    mce.get_ledger_snapshot = Mock(return_value={
        "system_bank": {"balance": 10000.0},
        "agents": {},
        "transaction_log": []
    })
    return mce


@pytest.fixture
def mock_citadel():
    """Mock Citadel verifier."""
    citadel = Mock()
    citadel.verify_conservation_of_wealth = Mock(return_value=Mock(is_valid=True))
    citadel.verify_solvency = Mock(return_value=Mock(is_valid=True))
    citadel.verify_checksum_integrity = Mock(return_value=Mock(is_valid=True))
    citadel.verify_debt_ceiling = Mock(return_value=Mock(is_valid=True))
    return citadel


@pytest.fixture
def mock_vector_store():
    """Mock vector store."""
    store = Mock()
    store.add_memory = AsyncMock(return_value="test_id")
    store.search = AsyncMock(return_value=[])
    store.deprecate_memory = AsyncMock()
    return store


@pytest.fixture
def mock_z3_verifier():
    """Mock Z3 verifier."""
    verifier = Mock()
    verifier.verify_theorem = Mock(return_value=Mock(
        is_valid=True,
        theorem="test_theorem",
        reasoning="Test reasoning",
        error_details=""
    ))
    verifier.get_verification_summary = Mock(return_value={
        "total": 0,
        "passed": 0,
        "failed": 0,
        "pass_rate": 0.0
    })
    return verifier


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "agent_id": "test_agent",
        "name": "Test Agent",
        "role": "Tester",
        "tier": "novice",
        "economics": {
            "base_pay_rate": 50.0,
            "complexity_access": 2,
            "bond_rate": 0.30,
            "royalty_share": 0.03,
            "penalty_multiplier": 2.0,
        },
        "cognition": {
            "model": "claude-3-sonnet",
            "temperature": 0.7,
            "max_tokens": 4096
        },
        "permissions": {
            "tools": ["test_tool"],
            "files": ["/tmp/test"],
            "network": False
        },
        "evolution": {
            "learning_rate": 0.01,
            "adaptation_threshold": 0.8
        }
    }


@pytest.fixture
def sample_transaction():
    """Sample transaction for testing."""
    return {
        "tx_id": "test_tx_001",
        "from": "system_bank",
        "to": "test_agent",
        "amount": 100.0,
        "type": "TRANSFER",
        "timestamp": "2024-01-01T00:00:00Z",
        "checksum": "test_checksum"
    }


@pytest.fixture
def sample_memory_chunk():
    """Sample memory chunk for testing."""
    from src.memory import MemoryChunk
    from datetime import datetime, timezone
    
    return MemoryChunk(
        id="test_memory_001",
        content="Test memory content",
        agent_id="test_agent",
        task_id="test_task",
        file_path="/tmp/test.py",
        timestamp=datetime.now(timezone.utc),
        utility_score=0.85,
        vector=[0.1] * 1536,
        status="active"
    )


@pytest.fixture
def test_config():
    """Test configuration dictionary."""
    return {
        "environment": "testing",
        "debug": True,
        "database": {
            "url": "sqlite:///:memory:",
            "host": "localhost",
            "port": 5432,
            "database": "test_apex",
            "username": "test",
            "password": "test"
        },
        "redis": {
            "url": "redis://localhost:6379/1",
            "host": "localhost",
            "port": 6379,
            "db": 1
        },
        "vector_store": {
            "backend": "chromadb",
            "dimension": 1536,
            "chroma_host": "localhost",
            "chroma_port": 8000
        },
        "llm": {
            "anthropic_api_key": "test_key",
            "openai_api_key": "test_key",
            "default_provider": "anthropic",
            "default_model": "claude-3-sonnet-20240229"
        },
        "security": {
            "jwt_secret": "test_secret_key_32_characters_long",
            "encryption_key": "test_encryption_key_32_chars",
            "enable_rbac": True
        },
        "monitoring": {
            "metrics_enabled": False,
            "tracing_enabled": False,
            "log_level": "DEBUG"
        },
        "performance": {
            "max_workers": 2,
            "request_timeout_seconds": 30
        }
    }


@pytest.fixture
def mock_pinecone_config():
    """Mock Pinecone configuration."""
    return {
        "api_key": "test_pinecone_key",
        "environment": "test-env",
        "index_name": "test-index",
        "dimension": 1536,
        "metric": "cosine",
        "batch_size": 10
    }


@pytest.fixture
def mock_weaviate_config():
    """Mock Weaviate configuration."""
    return {
        "url": "http://localhost:8080",
        "api_key": "test_weaviate_key",
        "batch_size": 10,
        "class_name": "MemoryChunk"
    }


@pytest.fixture
def security_hook_config():
    """Security hook configuration."""
    return {
        "blocked_imports": ["os", "sys", "subprocess"],
        "blocked_calls": ["exec", "eval", "open"],
        "blocked_dunder_methods": ["__import__", "__builtins__"],
        "suspicious_patterns": ["base64", "obfuscate"],
        "max_line_length": 1000,
        "max_ast_nodes": 10000
    }


@pytest.fixture
def bash_guard_config():
    """Bash guard configuration."""
    return {
        "blocked_commands": ["rm", "sudo", "chmod"],
        "allowed_commands": ["ls", "pwd", "echo"],
        "allowed_paths": ["/tmp", "/app"],
        "max_command_length": 1000
    }


# Test markers
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


# Helper functions
def create_test_ledger(path: Path, initial_balance: float = 10000.0):
    """Create a test ledger file."""
    ledger_data = {
        "metadata": {
            "version": "3.0.1",
            "currency": "APX",
            "created_at": "2024-01-01T00:00:00Z"
        },
        "system_bank": {
            "balance": initial_balance,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "agents": {},
        "transaction_log": []
    }
    
    with open(path, 'w') as f:
        json.dump(ledger_data, f, indent=2)
    
    return path


def create_test_persona(path: Path, agent_data: dict):
    """Create a test agent persona file."""
    persona_content = f"""---
agent_id: {agent_data['agent_id']}
name: {agent_data['name']}
role: {agent_data['role']}
tier: {agent_data['tier']}
economics:
  base_pay_rate: {agent_data['economics']['base_pay_rate']}
  complexity_access: {agent_data['economics']['complexity_access']}
  bond_rate: {agent_data['economics']['bond_rate']}
  royalty_share: {agent_data['economics']['royalty_share']}
  penalty_multiplier: {agent_data['economics']['penalty_multiplier']}
cognition:
  model: {agent_data['cognition']['model']}
  temperature: {agent_data['cognition']['temperature']}
  max_tokens: {agent_data['cognition']['max_tokens']}
permissions:
  tools: {agent_data['permissions']['tools']}
  files: {agent_data['permissions']['files']}
  network: {agent_data['permissions']['network']}
evolution:
  learning_rate: {agent_data['evolution']['learning_rate']}
  adaptation_threshold: {agent_data['evolution']['adaptation_threshold']}
---

## 🧠 SYSTEM IDENTITY
You are a test agent for unit testing.
"""
    
    with open(path, 'w') as f:
        f.write(persona_content)
    
    return path


__all__ = [
    "event_loop",
    "initialize_test_environment",
    "temp_dir",
    "temp_ledger",
    "temp_agent_persona",
    "mock_mce",
    "mock_citadel",
    "mock_vector_store",
    "mock_z3_verifier",
    "sample_agent_data",
    "sample_transaction",
    "sample_memory_chunk",
    "test_config",
    "mock_pinecone_config",
    "mock_weaviate_config",
    "security_hook_config",
    "bash_guard_config",
    "create_test_ledger",
    "create_test_persona",
]
