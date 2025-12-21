

# Universal Todo Workflow Template

**Document Type:** Master Standard Operating Procedure (MSOP) & Project Bible  
**Enforcement Level:** Strict / Mandatory  
**Applicability:** All Agentic Swarm Operations  
**Version:** 2.7 (Unified Rust/Python Architecture & UAWP Standards)

-----

## 1.) Core Philosophy & Operational Mandates

The fundamental axiom of this protocol is **Zero-Defect**. The "Good Enough" standard is explicitly abolished. This document serves as the absolute authority for project structure, execution, and delivery.

### 1.1 The Perfection Mandate

The workflow refuses to progress until the current artifact is mathematically and functionally perfect.

* **Production-Ready State:** Code must contain **NO** placeholders, **NO** stubs, **NO** simulated functions, **NO** mock features, and **NO** dead code. Code must be robust, effective, and efficient.
* **Atomic Granularity:** Tasks must be broken down to their lowest level. If a task can be split into multiple sub-tasks, it **must** be split.
* **Version Control Enforcement:** Every single file created or modified must end with a specific version control footer. This occurs in every single file.

### 1.2 The "Do Not Invent" Rule

Agents must not hallucinate libraries or APIs. Code must be written based on verified documentation and the existing `focus_paths` context provided in the Task JSON.

### 1.3 The "Golden Bridge" (Rust-Python Binding Mandate)

**CRITICAL:** Manual duplication of logic between Rust and Python is **STRICTLY PROHIBITED**.

* **Mechanism:** We prioritize **PyO3** to expose Rust structs and functions directly to Python as a native extension module.
* **Type Safety:** Python code interacting with Rust must use **Type Hints** (`.pyi` stubs) and **Pydantic Models** that mirror the Rust structs.
* **Validation:** Implementation is considered incomplete if the Python Frontend cannot import the Rust Backend as a typed module.

-----

## 2.) The Agentic Swarm Architecture

The Swarm operates as a cohesive unit. Agents are specific execution contexts with distinct permissions.

| **ID** | **Agent Name**                                | **Contextual Role** | **Specific Responsibilities & Mandates**                                                       |
|:------ |:--------------------------------------------- |:------------------- |:---------------------------------------------------------------------------------------------- |
| **1**  | **Orchestrator Agent (The Executive)**        | Project Manager     | Generates `TODO_LIST.json`, manages high-level architecture, enforces 10-task limits.          |
| **2**  | **Context Management Agent (The Optimizer)**  | Context Manager     | Ensures `focus_paths` are accurate and context tokens are optimized.                           |
| **7**  | **UI/UX Design Agent (The Visionary)**        | **Python UI Lead**  | Manages Python GUI logic (PySide6/Flet/Tkinter). Enforces **Event-Loop non-blocking** rules.   |
| **8**  | **QA & Testing Agent (The Critic)**           | Final Gatekeeper    | Validates **PyO3 bindings**. Ensures no "GIL Locking" issues. Runs `pytest`.                   |
| **9**  | **Polyglot Architect (The Builder)**          | **FFI Specialist**  | Owner of the **PyO3 Bridge**. Responsible for `Cargo.toml` (crate-type "cdylib") and `lib.rs`. |
| **11** | **Refactoring Agent (The Architect)**         | Code Optimizer      | Structural improvements, design pattern implementation, and non-functional enhancements.       |
| **12** | **Comprehensive Debugging Agent (The Fixer)** | Error Specialist    | Reviews code for *every possible conceivable error*. Manages the "Remediation Loop".           |
| **13** | **Code Quality Agent (The Linter)**           | **The Linter**      | Enforces `cargo clippy` (Rust) and **`ruff` / `mypy`** (Python).                               |
| **14** | **Security Agent (The Guardian)**             | Security Auditor    | Scans for vulnerabilities (`cargo audit`, `npm audit`, `pip-audit`) and secrets.               |
| **15** | **DevOps Agent (The Engineer)**               | Infrastructure      | Manages `maturin` builds (for compiling Rust to Python) and CI/CD.                             |
| **16** | **Technical Documents Agent (The Scribe)**    | Documentation       | Generates `README.md`, `CONTRIBUTING.md`, and technical comments.                              |
| **18** | **Version Control Agent (The Auditor)**       | Git Manager         | Ensures clean git status, manages `.gitignore`, handles commits/pushes.                        |

### 2.1 Hierarchy of Mandates (Conflict Resolution)

In the event of conflicting instructions between agents, the following hierarchy applies strictly:

1. **Security Agent (Highest):** Security concerns, vulnerability patches, and secret management override ALL other functionality or design requests.
2. **Orchestrator Agent:** Architectural constraints and project-level goals override local optimizations.
3. **Refactoring Agent:** Code structure, maintainability, and pattern adherence override raw coding speed.
4. **Polyglot Architect:** Implementation details and logic choices.

-----

## 3.) The Zero-Defect Production Protocol (ZDPP)

This is the rigid, iterative loop that governs **all** code generation. The process cannot skip steps.

### Phase 1: Implementation & Research

**Owner:** Polyglot Architect (The Builder)

1. **Documentation Review:** Review feature implementation docs and project docs to understand integration.
2. **Manifest Verification:** Confirm `file_manifest` distinguishes between `read_only` reference files and `write_access` target files.
3. **File Generation:** Create all required files. **No Stubs.**
4. **Multi-Stage TDD Execution:** Execute `implementation_approach` steps sequentially:
   * **Step A (TDD Scaffolding):** Create `pytest` scripts that fail because the Rust module isn't compiled yet.
   * **Step B (The Golden Bridge):** Define Rust structs with `#[pyclass]` and functions with `#[pyfunction]`.
   * **Step C (Backend Logic):** Implement the Rust Core logic.
   * **Step D (Python Integration):** Compile via `maturin develop`. Import the new module in Python. Ensure tests pass.
   * *Constraint:* Code must be Robust, Fully Functional, Effective, and Efficient.
   * *Footer Insertion:* Insert Version Control footer immediately upon creation.

### Phase 2: Normalization (The Formatting Loop)

**Owner:** Code Quality Agent (The Linter)
*This phase repeats until zero changes are detected by the scripts.*

1. **Formatting:** Run `rustfmt` (Rust), `ruff format` / `black` (Python).
2. **Stylization:** Run `clippy` (Rust), `ruff check` (Python). Correct idiomatic issues.
3. **Type Check:** Run `mypy --strict` (Python). **Crucial step to verify FFI safety.**
4. **Sorting:** Sort imports via `ruff`.
5. **Verification:** Rerun all scripts. **Success = 0 errors/warnings/issues**.

### Phase 3: Security Hardening

**Owner:** Security Agent (The Guardian)

1. **Vulnerability Scan:** Run `cargo audit` (Rust), `pip-audit` (Python).
2. **Memory Safety:** Ensure PyO3 implementations handle lifetimes correctly to prevent leaks.
3. **Remediation:** Correct every single issue detected.
4. **Verification:** Rerun scans until **0 vulnerabilities** remain.

### Phase 4: Functional Verification Matrix (Complex Testing)

**Owner:** Polyglot Architect (The Builder) & QA Agent
*This phase ensures logic soundness BEFORE deep debugging begins.*

1. **FFI Round-Trip:** Send data from Python -\> Rust -\> Python. Verify object integrity.
2. **Granular Functionality Test:**
   * **Action:** Cycle through **every** single new function, option, switch, and setting associated with the feature.
   * **Verification:** Confirm that input data results in the exact expected output data defined in the documentation.
3. **Edge Case Simulation:**
   * **Action:** Test maximum/minimum values, null inputs, and rapid-fire toggling of options.
   * **Verification:** Confirm stability is maintained under stress.
4. **GIL Stress Test:** Ensure heavy Rust computations release the Global Interpreter Lock (GIL) to keep the Python UI responsive.
5. **Compromise Remediation:**
   * **Condition:** If *any* functionality is compromised, behaves unexpectedly, or fails to trigger.
   * **Correction:** The **Polyglot Architect** immediately refactors the logic.
   * **Loop:** Restart Phase 4 Step 1 until 100% functionality is verified.

### Phase 5: The Debugging Loop

**Owner:** Comprehensive Debugging Agent (The Fixer)

1. **Deep Review:** Review every line for every conceivable type of error (logic, syntax, runtime).
2. **Detection:** Note *every single* error found.
3. **Correction:** The 'Coding Expert' (Polyglot Architect) makes corrections.
4. **Re-Review:** The Debugging Agent reviews the corrected code.
5. **Loop:** Repeat until **no errors** are discovered.

### Phase 6: Final Quality Assurance & Runtime Validation

**Owner:** QA & Testing Agent (The Critic)

1. **Final Code Review:** QA Agent reviews code one last time. Issues handed to 'Coding Expert'.
2. **Compilation/Build:** Attempt to compile (`maturin build --release`).
   * *Failure:* Tracebacks sent to 'Coding Expert' -\> Fix -\> Retry.
3. **Runtime Execution:** Launch Python entry point.
   * *Failure (Load Error):* Coding Expert corrects tracebacks -\> Recompile -\> Rerun.
4. **Functional Cycle:** Cycle through each feature, function, setting, option, or configuration in the live environment.
5. **Final Sign-off:** Task marked "Completed" only when all criteria are met.

-----

## 4.) Data Structures & Schema Standards

Deviating from these JSON formats is **Strictly Prohibited**.

### 4.1 Rust-Python Response Format (Standardized Result)

To ensure the Frontend can robustly handle any Backend result, Rust functions exposed to Python must return a standardized Result type (often converting Rust `Result<T, E>` to Python exceptions or a custom Python class).

```rust
// Rust (PyO3)
#[pyclass]
pub struct PyResponse {
    #[pyo3(get)]
    pub success: bool,
    #[pyo3(get)]
    pub data: Option<String>, // Or specific PyObject
    #[pyo3(get)]
    pub error: Option<String>,
}
```

### 4.2 Macro-Level: The Project Roadmap (`TODO_LIST.json`)

Located in: `./workflow/TODO/TODO_LIST.json`

*(Standard project-level JSON structure, managed by Orchestrator Agent)*

### 4.3 Micro-Level: Task Execution (`IMPL-*.json`)

Located in: `./workflow/TODO/IMPL-N.M.json`

**Rules:**

* **File Manifest:** Must be an object distinguishing `read_only` (context) from `write_access` (modification).
* **Target Files:** Must be specific for each *step* of the implementation.
* **Golden Bridge:** `target_files` must include `src/lib.rs` (Rust export) and the Python calling code.
* **Flow Control:** Must include `rollback_strategy`, `pre_analysis`, and `implementation_approach`.
* **Hierarchy:** IMPL-N (Main) -\> IMPL-N.M (Subtask). Max 2 levels depth.
* **Context Pruning:** Use `pre_execution_trigger` to force context clearing between heavy steps.

<!-- end list -->

```json
{
  "id": "IMPL-1.2",
  "title": "Implement Data Processing & Python Bindings",
  "status": "pending",
  "meta": {
    "type": "feature_implementation",
    "agent": "Polyglot Architect (The Builder)",
    "category": "Core Logic",
    "created": "2025-12-08T07:05:05",
    "documented_in": "docs/tech/FFI_SPEC.md"
  },
  "context": {
    "requirements": [
      "Implement `process_data` in Rust",
      "Expose via PyO3 as `backend.process_data`",
      "Implement Python UI thread to call this non-blocking",
      "Release GIL during processing"
    ],
    "file_manifest": {
      "read_only": ["frontend/config.py"],
      "write_access": [
        "backend/src/lib.rs",
        "backend/src/processor.rs",
        "frontend/main_window.py",
        "tests/test_processor.py"
      ]
    },
    "acceptance": [
      "Rust compiles via Maturin",
      "Python can import and call function",
      "UI does not freeze during execution"
    ]
  },
  "flow_control": {
    "rollback_strategy": {
      "on_failure": "revert_git_clean",
      "notify_agent": "Orchestrator Agent",
      "fallback_action": "Create ticket for dependency research and mark IMPL-1.2 as BLOCKED"
    },
    "pre_analysis": [
      {
        "step": "review_documentation",
        "action": "Read docs/tech/FFI_SPEC.md",
        "output_to": "feature_requirements"
      }
    ],
    "implementation_approach": [
      {
        "step": 1,
        "title": "Phase 1: Rust Core & PyO3 Definition",
        "description": "Create Rust structs and PyModule definition.",
        "pre_execution_trigger": "Context Management Agent: Prune context.",
        "target_files": [
          "backend/src/lib.rs",
          "backend/src/processor.rs"
        ],
        "modification_points": [
          "Define `DataProcessor` struct",
          "Add `#[pyclass]` and `#[pymethods]`",
          "Implement `#[pyfunction] fn process_data`"
        ],
        "logic_flow": [
          "Define Logic",
          "Wrap in PyO3",
          "Ensure GIL release via `Python::allow_threads`"
        ]
      },
      {
        "step": 2,
        "title": "Phase 2: Build & Python Tests",
        "description": "Compile extension and write Python tests.",
        "pre_execution_trigger": "Context Management Agent: Clear memory of Step 1 'thinking'.",
        "target_files": ["tests/test_processor.py"],
        "modification_points": [
          "Run `maturin develop`",
          "Write `pytest` cases to assert Rust behavior"
        ],
        "logic_flow": ["Compile -> Import -> Test Assertions"]
      },
      {
        "step": 3,
        "title": "Phase 3: Python UI Integration",
        "description": "Connect the Rust function to the GUI.",
        "pre_execution_trigger": "Context Management Agent: Prune context.",
        "target_files": ["frontend/main_window.py"],
        "modification_points": [
          "Import `backend` module",
          "Spawn worker thread/async task for Rust call",
          "Handle result signal"
        ],
        "logic_flow": ["UI Event -> Thread/Task -> Rust Call -> Signal UI"]
      }
    ]
  },
  "quality_gate_verification": {
    "type_safety": {
      "status": "Required",
      "criteria": "Python code passes `mypy --strict`. Rust passes `clippy`."
    },
    "linted": {
      "status": "Required",
      "criteria": "Zero warnings (Ruff/Rustfmt)"
    },
    "security": {
      "status": "Required",
      "criteria": "No vulnerabilities"
    },
    "testing": {
      "status": "Required",
      "criteria": "100% pytest pass"
    },
    "no_placeholders": {
      "status": "Required",
      "criteria": "No TODO/FIXME/placeholder code"
    }
  }
}
```

-----

## 5.) File System & Environment Standards

### 5.1 Directory Structure

The system relies on this specific structure for session detection.

```
Project Root
├── workflow
│   ├── active
│   │   └── WFS-[topic]         <-- Active Session
│   │       ├── task
│   │       │   └── IMPL-1.json  <-- Micro Task Files
│   │       ├── IMPL_PLAN.md     <-- Planning Doc
│   │       ├── TODO_LIST.json   <-- Macro Roadmap
│   │       └── workflow-session.json
│   └── archive
├── backend             <-- RUST PROJECT
│   ├── Cargo.toml      <-- Crate-type = ["cdylib"]
│   ├── src
│   │   ├── lib.rs      <-- PyModule Entry Point
│   │   └── ...
├── frontend            <-- PYTHON FRONTEND
│   ├── main.py
│   ├── ui/
│   └── ...
├── tests               <-- PYTHON TESTS (pytest)
├── docs
└── gfx
    ├── icons
    └── fonts
```

### 5.2 Version Control Footer

**Mandatory:** The last lines of *every* file must contain this block.

```
# Version Control Information 
# --------------------------- 
# File Created: [Date] 
# Last Modified: [Date] 
# Modified By: [Agent Name] 
# Version: [Version Number]
```

-----

## 6.) Success Criteria Checklist

A project/task is only successful when **ALL** items below are checked.

1. [ ] **Zero Defects:** Code throws no Errors or Warnings (Rust or Python).
2. [ ] **Binding Integrity:** Rust functions are callable from Python with correct types.
3. [ ] **Fidelity:** All features function exactly as described in documentation.
4. [ ] **Purity:** No placeholders, stubs, mocks, or dead code.
5. [ ] **Concurrency Safety:** Heavy Rust tasks release the Python GIL.
6. [ ] **Verification:** The `quality_gate_verification` block in the Todo JSON is fully satisfied.
7. [ ] **Security:** No secrets or vulnerabilities exist.
8. [ ] **Packaging:** `maturin build` succeeds without warnings.
