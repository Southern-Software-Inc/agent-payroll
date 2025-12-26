🏛️ Apex Agent Payroll System v7.0: The Definitive Technical Specification
==========================================================================

**Classification:** Autonomous Meritocratic Swarm (AMS) **Version:** 7.0.0 (Singularity Release) **License:** MIT / Apache 2.0 Hybrid **Architecture:** Distributed Model Context Protocol (MCP) Server **Governance:** Neuro-Symbolic Logic & Deflationary DeFi
📑 Master Index
---------------

1. [**System Architecture & Topology**](https://www.google.com/search?q=%231-system-architecture--topology "null") - _The Physical Layout._

2. [**The Constitution (Kernel Logic)**](https://www.google.com/search?q=%232-the-constitution-kernel-logic "null") - _Hardcoded Invariants._

3. [**The 32-Agent Swarm (Persona Specs)**](https://www.google.com/search?q=%233-the-32-agent-swarm-persona-specs "null") - _Prompts & Tools._

4. [**Cognitive Architecture (The Mind)**](https://www.google.com/search?q=%234-cognitive-architecture-the-mind "null") - _HTN, Neuro-Symbolic, Holographic._

5. [**Economic Engine (The Heart)**](https://www.google.com/search?q=%235-economic-engine-the-heart "null") - _Stablecoins, Staking, Math._

6. [**Infrastructure & Security (The Body)**](https://www.google.com/search?q=%236-infrastructure--security-the-body "null") - _WASM, Docker, IPFS, Kyber._

7. [**Governance & Hooks (The Nervous System)**](https://www.google.com/search?q=%237-governance--hooks-the-nervous-system "null") - _The 8-Stage Pipeline._

8. [**Interoperability Protocols (The Senses)**](https://www.google.com/search?q=%238-interoperability-protocols-the-senses "null") - _LSP, SSP, TUI._

1. System Architecture & Topology

---------------------------------

### 1.1 The "Where": Directory Structure & Component Map

The system lives in a strict hierarchical file system to separate concerns (Logic vs. Data vs. Identity).
    /ApexAgentPayroll
    ├── /agents (The Soul)          # Markdown definitions of Agent Personas (WHO)
    ├── /src (The Body)             # Python Source Code (HOW)
    │   ├── /config                 # JSON Manifests (hooks, plugins)
    │   ├── /modules                # Core Logic Engines (Economy, Z3, RAG)
    │   └── /ui                     # Presentation Layer (TUI, Web)
    ├── /data (The Memory)          # Mutable State (SQLite, Vector Store)
    └── /docs (The Wisdom)          # Auto-generated Knowledge Base

### 1.2 The "What": Technology Stack

* **Runtime:** Python 3.11+ (AsyncIO).

* **Interface:** Model Context Protocol (MCP) over Stdio/SSE.

* **Database:** SQLite (WAL Mode) for Ledger; ChromaDB for Semantic Memory.

* **Graph:** NetworkX (in-memory) / Neo4j (persistent) for Knowledge Graph.

* **Logic:** Microsoft Z3 (SMT Solver) for mathematical verification.

* **Networking:** Libp2p (via Python bindings) for Swarm-to-Swarm.

* **UI:** Rich/Textual (TUI), React/Vite (Web).
2. The Constitution (Kernel Logic)

----------------------------------

### 2.1 The "Why": Immutable Governance

To prevent "rogue agent" scenarios and ensure fiscal solvency, specific rules are hardcoded into the execution path. These are not suggestions; they are **constraints**.

### 2.2 The "How": Implementation

**File:** `src/modules/z3_verifier.py`

#### Law 1: Fiscal Responsibility (Bankruptcy Prevention)

* **Rule:** System halts if `Balance < -100`.

* **Z3 Constraint:** `s.add(Global_Balance + Transaction_Value >= -100)`

* **Enforcement:** Before `master_compensation.py` commits a transaction, it calls `z3_verifier`. If `s.check() == unsat`, the transaction raises `BankruptcyError` and the task is aborted.

#### Law 2: Non-Exfiltration (DLP)

* **Rule:** No data leaves localhost without explicit user confirmation.

* **Mechanism:**
  
  1. **Docker:** Containers run with `--network none`.
  
  2. **Regex Hook:** `hook_dlp_scan` scans all outbound text for IP addresses, URLs, and AWS Keys (`AKIA...`).
  
  3. **Action:** Regex match triggers immediate `SystemHalt`.

#### Law 3: Zero-Stub Policy

* **Rule:** Code must be functional. No placeholders.

* **Mechanism:** The `polyglot_architect` output is parsed via Python's `ast` module.
  
  * **Check:** `if isinstance(node, ast.Pass) or "TODO" in node.body:`
  
  * **Result:** Automatic rejection of the code block.
3. The 32-Agent Swarm (Persona Specs)

-------------------------------------

### 3.1 The "Who": Anatomy of an Agent

An Agent is not just a prompt; it is a **Tuple**: `(System_Prompt, Tool_Set, Memory_Scope, Economic_Wallet)`.

**Location:** `agents/{agent_name}.md`

### 3.2 Key Agent Specifications

#### **A. Orchestrator Agent (The Executive)**

* **Input:** Raw User Request ("Build a Todo App").

* **Algorithm:** **HTN (Hierarchical Task Network)**.
  
  * _Decompose:_ Goal -> Strategy -> Tactics -> Atomic Actions.
  
  * _Constraint:_ Must define dependencies (Task B requires Task A).

* **Output:** A JSON DAG (Directed Acyclic Graph) of tasks passed to the `EventBus`.

#### **B. Polyglot Architect (The Builder)**

* **Prompt Strategy:** "Chain-of-Thought" + "Reflexion".
  
  * _Step 1:_ Draft Code.
  
  * _Step 2:_ Inner Monologue ("Did I handle the null case?").
  
  * _Step 3:_ Revise Code.
  
  * _Step 4:_ Final Output.

* **Tools:** `read_file`, `write_file`, `list_dir`.

* **Specialty:** Rust, Python, TypeScript. Zero-Stub enforcement.

#### **C. QA & Testing Agent (The Adversary)**

* **Philosophy:** Test Driven Development (TDD).

* **Action:** Receives the _Plan_ from the Orchestrator. Writes unit tests that **FAIL**.

* **Tools:** `run_pytest`, `run_cargo_test`, `run_jest`.

* **Economic Incentive:** Earns a bounty ($5.00) for every bug found in the Architect's code.

#### **D. Prompt Engineering Agent (The Refiner)**

* **Function:** Dynamic Temperature Control.

* **Logic:**
  
  * If Hook Stage == `Ideation`: Set `temperature=0.7`.
  
  * If Hook Stage == `Coding`: Set `temperature=0.1`.

* **Meta-Prompting:** Wraps the user's request in a "Persona Wrapper" (e.g., "You are a Senior Principal Engineer at Google...").

#### **E. Evolution Agent (The Improver)**

* **Trigger:** Nightly Cron Job (`dream_cycle.py`).

* **Input:** `data/error_logs.json`.

* **Algorithm:** Semantic Clustering. Groups errors by type (e.g., "ImportError").

* **Action:** Edits `agents/polyglot_architect.md` to add a negative constraint: "Do not use circular imports in Python."
4. Cognitive Architecture (The Mind)

------------------------------------

### 4.1 The "How": HTN Planning

Instead of a linear list, the system builds a Tree.
    # Pseudocode logic for HTN
    def plan(task):
        if is_atomic(task): return [task]
        methods = get_methods(task)
        for method in methods:
            subtasks = decompose(method)
            try:
                return [plan(t) for t in subtasks]
            except PlanningFailure:
                continue # Backtrack

### 4.2 The "What": Neuro-Symbolic Core

Combines LLM Intuition with Logic Rigor.

1. **LLM:** Generates a _hypothesis_ code block.

2. **Prolog/Z3:** Verifies the _invariants_.
   
   * _Example:_ LLM writes a Bank Transfer function. Z3 verifies `Post_Balance == Pre_Balance - Amount`.
   
   * _Result:_ If verification fails, the code is rejected _before_ running tests.

### 4.3 The "Where": Holographic Memory

* **Problem:** Context Window limits.

* **Solution:** **Holographic Reduced Representations (HRR)**.

* **Math:** `Memory_Vector = (Context * New_Info) + Noise`.

* **Storage:** Stored in `data/vector_store/` as dense binary vectors. Allows recalling the _gist_ of a conversation from 10,000 turns ago without storing the text.
5. Economic Engine (The Heart)

------------------------------

### 5.1 The "Why": Economic Alignment

Standard RLHF aligns models to "helpfulness." Apex aligns them to "Profitability" (Correctness/Efficiency).

### 5.2 The "What": Apex Credit (APX)

* **Definition:** An Algorithmic Stablecoin.

* **Peg:** 1 APX = 1 Second of A100 GPU Inference Time.

* **Minting:** Credits are minted by the User (injecting capital) or by the System (UBI).

* **Burning:** Credits are burned via "Slashing" (failed tasks) or "Taxation".

### 5.3 The "How": Ledger Database Schema (`ledger.db`)

    CREATE TABLE ledger (
        transaction_id UUID PRIMARY KEY,
        agent_id TEXT NOT NULL,
        amount DECIMAL(10, 4) NOT NULL,
        transaction_type TEXT CHECK(transaction_type IN ('REWARD', 'FINE', 'STAKE', 'TAX')),
        task_ref_id UUID,
        prev_hash TEXT NOT NULL -- Merkle Chain Link
    );

### 5.4 Advanced Mechanisms

* **Staking:** Agent X wants a High-Risk task. It locks 50 APX. If it fails, 50 APX is sent to `0x0` (Burned).

* **Prediction Markets:** Agent Y bets 10 APX that Agent X will fail. If X fails, Y wins 20 APX. Crowdsources risk assessment.
6. Infrastructure & Security (The Body)

---------------------------------------

### 6.1 WASM/Docker Sandboxing

**File:** `src/modules/sandbox_executor.py`

* **Tier 1 (WASM):** Uses `wasmtime` for pure logic/linting. Startup: 5ms.

* **Tier 2 (Docker):** Uses `python:3.9-slim`. Startup: 500ms.
  
  * _Config:_ `network_mode="none"`, `mem_limit="512m"`, `read_only=True`.

### 6.2 Decentralized Persistence (IPFS)

* **Logic:** Every hour, the system takes a snapshot of `ledger.db` and `vector_store`.

* **Action:** Hashes the snapshot (SHA-256) and pins it to a local IPFS node.

* **Benefit:** Complete disaster recovery even if the local disk is wiped.

### 6.3 Cryptography

* **Internal Comms:** Simulated Kyber-512 (Post-Quantum) key exchange between agents.

* **Audit Log:** Structured as a **Merkle Tree**. The User only needs the Root Hash to verify the entire history of the project is unaltered.
7. Governance & Hooks (The Nervous System)

------------------------------------------

### 7.1 The "When": 8-Stage Lifecycle

**File:** `src/config/hooks_manifest.json`

Every prompt passes through these gates strictly in order:

1. **Input Processing:** Sanitization (Bleach), Sentiment Analysis (VADER).

2. **Prompt Engineering:** Expansion, Persona Injection.

3. **Context Optimization:** Token Pruning, Holographic Compression.

4. **Cognitive Planning:** Z3 Logic Verification, Counterfactual Simulation.

5. **Specialized Checks:** Zero-Stub Audit, Compliance Scan (Ethicist).

6. **Execution Gating:** Safety Block (`rm -rf`), Biometric Gate.

7. **Synthesis:** Hallucination Check, Watermarking.

8. **Economics:** Ledger Update, Merkle Hashing.

8. Interoperability Protocols (The Senses)

------------------------------------------

### 8.1 Language Server Protocol (LSP)

* **What:** Exposes the Swarm to VS Code / Neovim.

* **How:** Implements `textDocument/completion` and `textDocument/publishDiagnostics`.

* **Result:** The User sees squiggly lines in their editor generated by the Swarm's logic.

### 8.2 Swarm-to-Swarm Protocol (SSP)

* **What:** P2P Networking.

* **Tech:** Libp2p over WebSockets.

* **Packet Structure:**
  
      {
        "protocol": "apex/ssp/1.0",
        "type": "RFP_BROADCAST",
        "payload": { "task_id": "...", "bounty": 100, "currency": "APX" },
        "signature": "gpg_signed_hash"
      }
