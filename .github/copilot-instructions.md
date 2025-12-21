<!-- Copilot instructions for the agent-payroll repository -->
# Copilot Instructions — APEX Agent Payroll

Purpose: give an AI coding agent the minimal, high-value context to be productive in this repository.

1) Big picture (quick)
- Master Compensation Engine (MCE): `src/economics/` — ACID ledger, WAL, agent P&L. Changes here require strong tests and careful state migration.
- Soul Parser / Agents: `src/agents/` + `agents/` — agents are authored as Markdown with YAML frontmatter (genotype) and markdown phenotype. The Soul Parser compiles these to token-optimized prompts.
- MCP Server: `src/mcp/` — JSON-RPC 2.0 hub for LLM/tool integration. Handlers must be async and respect the request registry.
- Hooks / Hypervisor: `src/hooks/` — PRE_PROMPT / PRE_TOOL / POST_TOOL phases; used for security and fiscal checks.
- Semantic Memory: `src/memory/` — embedding pipeline, HNSW indexes, semantic sieve.

2) Why these choices matter
- Economic correctness is core: any code touching `src/economics/` impacts agent payouts and must preserve ACID properties and ledger integrity.
- Agent behavior is data-driven (Markdown personas). Edits to `agents/*.md` are part of runtime behavior and must validate frontmatter.

3) Project-specific workflows (commands you should run locally / in CI)
- Setup virtualenv and deps:
  ```bash
  python -m venv venv
  # Windows
  venv\Scripts\activate
  pip install -r requirements.txt
  ```
- Run system locally:
  ```bash
  python main.py
  ```
- Tests and checks (must pass before PR):
  ```bash
  pytest tests/                # unit + integration
  pytest tests/ --cov=src --cov-report=html
  mypy src/
  ruff check src/
  black --check src/
  ```

4) Repository conventions and gotchas
- Zero-Defect Production Protocol (ZDPP): no placeholder functions, full test coverage for non-trivial logic, strict type hints.
- Documentation belongs in `docs/` (root README is the primary overview). Do not scatter design docs elsewhere.
- Files include a version-control footer — update it if you modify production files.
- Agent persona format (example):
  ```markdown
  ---
  agent_id: "polyglot_builder_v1"
  economics:
    base_pay_rate: 85.00
  ---

  ## SYSTEM IDENTITY
  I am a master architect...
  ```

5) Integration points to inspect for changes
- JSON-RPC handlers: `src/mcp/` (look for `register_handler`, `handle_request`).
- Hooks pipeline: `src/hooks/` (PRE_PROMPT, PRE_TOOL, POST_TOOL) — ensure hook ordering and security checks are preserved.
- Ledger WAL and transaction APIs: `src/economics/` — review tests in `tests/test_ledger.py` for expected behaviors.
- Agent compilation: `src/agents/` — see how Markdown frontmatter is validated and compiled into prompts.

6) When editing code, follow this checklist
- Add/modify tests in `tests/` that exercise new behavior.
- Run `mypy`, `ruff`, `black` locally; fix reported issues.
- Update documentation in `docs/` and, where relevant, the agent Markdown files.
- Update version-control footer in modified files.
- For economic/ledger changes, include migration notes and explicit ACID reasoning in the PR description.

7) Quick file pointers (start here)
- Project overview: `README.md`
- Agents index: `agents/README.md`
- Core examples: `src/economics/`, `src/agents/`, `src/mcp/`, `src/hooks/`, `src/memory/`
- Tests: `tests/test_ledger.py`, `tests/conftest.py`

8) PR guidance for an AI agent
- Keep PRs focused and small when changing economic logic.
- Describe the exact runtime impact (e.g., change in payout calculation) and link tests that demonstrate the change.
- If touching agent personas, show before/after compiled prompts and token impact.

If anything here is unclear or you'd like more detail about a specific component (MCE, Soul Parser, MCP, or Hooks), tell me which one and I will expand the section with concrete code references and examples.
