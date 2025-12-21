# APEX Agent Payroll System

A sophisticated autonomous agent swarm orchestration platform with meritocratic compensation, semantic memory, and advanced security measures.

## Project Overview

APEX is an **Agent Payroll System** that implements a **Meritocratic Autonomous Environment (MAE)** where intelligent agents operate as autonomous profit-and-loss centers. The system enforces strict economic incentives to reduce hallucinations and encourage efficient reasoning.

## Core Architecture

### 1. **Master Compensation Engine (MCE)** - `src/economics/`
- ACID-compliant financial ledger with Write-Ahead Logging (WAL)
- Agent financial state management (balance, escrow, earnings)
- Performance tracking (streak, success rate, reputation)
- Transaction logging with cryptographic checksums

### 2. **Soul Parser** - `src/agents/`
- Transforms Markdown agent specifications into compiled system prompts
- Validates YAML frontmatter (Genotype)
- Parses semantic behavioral blocks (Phenotype)
- Generates token-optimized cognitive instructions

### 3. **MCP Server** - `src/mcp/`
- Model Context Protocol (MCP) hub for LLM communication
- JSON-RPC 2.0 state machine with request registry
- Tool and resource registration
- Asynchronous I/O with non-blocking transport

### 4. **Hypervisor & Hooks** - `src/hooks/`
- Deep packet inspection on JSON-RPC streams
- Chain-of-Responsibility hook pipeline
- PRE_PROMPT, PRE_TOOL, POST_TOOL phases
- Security validation and fiscal reality injection

### 5. **Semantic Memory** - `src/memory/`
- Multi-tiered memory hierarchy (L1, L2, L3)
- Vector embedding pipeline with HNSW indexing
- Semantic Sieve for filtering non-critical data
- Long-term technical intuition for agents

## Project Structure

```
Agent Payroll/
├── src/                          # Source code
│   ├── core/                     # Constants and configuration
│   ├── economics/                # Master Compensation Engine
│   ├── agents/                   # Soul Parser and personas
│   ├── mcp/                      # MCP server and JSON-RPC
│   ├── hooks/                    # Hypervisor and hooks
│   └── memory/                   # Semantic memory and vectors
├── agents/                       # Agent persona markdown files
├── hooks/                        # Hook implementations
├── tests/                        # Unit and integration tests
├── docs/                         # System documentation
├── workflow/                     # Task management
│   ├── [TODO]/                   # Pending tasks
│   └── completed/                # Completed tasks
├── scripts/                      # Utility scripts
├── temp/                         # Temporary files
└── requirements.txt              # Python dependencies
```

## Getting Started

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the System

```bash
# Start the APEX system
python main.py
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Key Design Principles

### Zero-Defect Production Protocol (ZDPP)

Every deliverable adheres to strict quality standards:

1. **No Placeholders:** Code is production-ready with no stubs or mock functions
2. **Full Test Coverage:** All non-trivial functions have unit tests
3. **Type Safety:** Python code uses strict type hints
4. **ACID Compliance:** Financial state is never compromised
5. **Security First:** All code passes security audits

### Meritocratic Economics

Agents operate as autonomous P&L centers:

- **Pay-for-Performance:** Every action has measurable financial impact
- **Streak Bonuses:** Consistent success increases reputation and earnings
- **Complexity Multipliers:** Expert tasks command premium rates
- **Reputation Scoring:** Long-term reliability determines trust level

### Cognitive Compilation

Agents are defined as executable Markdown files:

```markdown
---
# YAML Genotype (Immutable parameters)
agent_id: "polyglot_builder_v1"
economics:
  base_pay_rate: 85.00
---

# Markdown Phenotype (Behavior directives)
## SYSTEM IDENTITY
I am a master architect...
```

The Soul Parser compiles these into token-optimized system prompts.

## Core Components

### Master Compensation Engine

```python
from src.economics import get_mce

mce = get_mce()

# Create agent
mce.create_agent("builder_01", "The Builder", tier="expert")

# Transfer funds
mce.transfer_funds("system_bank", "builder_01", 100.0)

# Update performance
mce.update_agent_performance("builder_01", streak=5, reputation_score=0.95)
```

### Soul Parser

```python
from src.agents import get_soul_parser

parser = get_soul_parser()

# Awaken an agent (compile its system prompt)
agent = parser.awaken_agent("polyglot_builder_v1")
print(agent["system_prompt"])  # Token-optimized prompt
```

### MCP Server

```python
from src.mcp import get_mcp_server

server = get_mcp_server()

# Register a handler
async def handle_tools_list(params):
    return {"tools": [...]}

server.register_handler("tools/list", handle_tools_list)

# Process a JSON-RPC request
response = await server.handle_request('{"jsonrpc":"2.0","method":"tools/list","id":"1"}')
```

## Documentation

See the `docs/` folder for detailed system specifications:

- [The Master Compensation Engine](docs/The%20Master%20Compensation%20Engine.md)
- [Agent Personas & the Soul Parser](docs/Agent%20Personas%20&%20the%20Soul%20Parser.md)
- [MCP Protocol & System Architecture](docs/MCP%20Protocol%20&%20System%20Architecture.md)
- [The Hypervisor & Hook Manager](docs/The%20Hypervisor%20&%20Hook%20Manager.md)
- [Data Persistence & Semantic Memory](docs/Data%20Persistence%20&%20Semantic%20Memory%20Architecture.md)

## Workflow Management

Tasks are tracked in JSON format following the Universal Todo Workflow Template (UTWT):

```json
{
  "task_id": "TASK-001",
  "title": "Implement core MCE",
  "status": "completed",
  "owner": "polyglot_builder_v1",
  "priority": 1,
  "created_at": "2025-12-21T00:00:00Z",
  "completed_at": "2025-12-21T12:00:00Z"
}
```

## Development Guidelines

### Code Organization

- **`src/`**: Core production code
- **`tests/`**: Unit and integration tests
- **`docs/`**: System documentation
- **`agents/`**: Agent persona definitions
- **`hooks/`**: Hook implementations
- **`scripts/`**: Utility and maintenance scripts

### Version Control

Every file includes a version control footer:

```python
# VERSION CONTROL FOOTER
# File: src/module/file.py
# Version: 0.1.0
# Last Modified: 2025-12-21T00:00:00Z
# Git Hash: abc123def456
```

### Testing Requirements

All code must pass:

```bash
pytest tests/                    # Unit tests
mypy src/                        # Type checking
ruff check src/                  # Linting
black --check src/               # Formatting
```

## Contributing

This project follows the Universal Todo Workflow Template (UTWT) methodology. All contributions must:

1. Pass the Zero-Defect Production Protocol (ZDPP)
2. Include comprehensive unit tests
3. Maintain type safety
4. Follow the project's architectural patterns
5. Update documentation

## License

[License information to be added]

## Author

APEX Development Team

---

**Last Updated:** 2025-12-21
**Version:** 0.1.0
