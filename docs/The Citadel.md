# 🏛️ SECTION 4: THE CITADEL (Z3 FORMAL VERIFICATION)

**Module ID:** `APEX-VERI-004`  
**Atomic Level:** SMT-LIB 2.0 Syntax Generation, Satisfiability Modulo Theories (SMT), Financial Invariants, and Formal Logic Proofs.

---

## 4.1 The Philosophy of the Citadel: Proving vs. Testing

The **Citadel** is the formal verification core of the Apex ecosystem. In traditional software engineering, reliability is pursued through unit testing, integration testing, and fuzzing. However, in an autonomous multi-agent system where agents can modify their own prompts and execute financial transactions, testing is insufficient. Testing only proves the presence of bugs, never their absence.

The Citadel operates on the principle of **Formal Verification**. It uses the **Z3 Theorem Prover** (developed by Microsoft Research) to mathematically prove that the system's state transitions are valid. Every critical action—be it a ledger update, a permission escalation, or a cognitive rewrite—must be submitted to the Citadel as a logical theorem. If the Citadel cannot prove the theorem is safe, the action is aborted. This is the "Mathematical Supreme Court" of the swarm.

---

## 4.2 SMT-LIB 2.0: The Language of the Citadel

The Citadel communicates using **SMT-LIB 2.0**, the international standard for Satisfiability Modulo Theories. The `z3_verifier.py` module acts as a compiler that translates high-level system states into low-level logical assertions.

### 4.2.1 Atomic Logic Primitives

The Citadel utilizes several theories within Z3:

* **Reals and Integers:** For financial calculations and token counting.
* **Bit-Vectors:** For low-level permission masks and cryptographic hash verification.
* **Arrays:** For modeling the state of the ledger and the agent roster.
* **Uninterpreted Functions:** For modeling complex agent behaviors and tool interactions.

### 4.2.2 The SAT/UNSAT Result

When a theorem is submitted to Z3, it returns one of three results:

1. **UNSAT (Unsatisfiable):** The negation of the safety property is impossible. This means the action is **PROVABLY SAFE**.
2. **SAT (Satisfiable):** Z3 found a "Counter-Model"—a specific set of conditions where the safety property is violated. The action is **REJECTED**.
3. **UNKNOWN:** The logic is too complex for the solver to decide within the timeout (default: 500ms). The action is **REJECTED** (Fail-Safe).

---

## 4.3 Financial Invariants: The Wealth Proof

The most critical role of the Citadel is ensuring the integrity of the **Master Compensation Engine**. It enforces the **Conservation of APX**—the principle that money cannot be created or destroyed outside of explicit system-defined minting/burning events.

### 4.3.1 The Conservation Theorem

Before a transaction $T$ involving a reward $R$ and a tax $X$ is committed, the Citadel must prove:
$$\sum \text{Balances}_{pre} + \text{Bank}_{pre} = \sum \text{Balances}_{post} + \text{Bank}_{post}$$

### 4.3.2 Atomic SMT-LIB Implementation

The `z3_verifier` generates the following logic string for a task payout:

```lisp
; Declare initial states
(declare-fun bank_0 () Real)
(declare-fun agent_0 () Real)
(declare-fun reward () Real)
(declare-fun tax () Real)

; Define the transaction logic
(declare-fun bank_1 () Real)
(declare-fun agent_1 () Real)

; Assertions (The Rules of the Economy)
(assert (> bank_0 0))
(assert (> agent_0 -100.0)) ; Bankruptcy limit
(assert (> reward 0))
(assert (> tax 0))

; The State Transition
(assert (= bank_1 (- (+ bank_0 tax) reward)))
(assert (= agent_1 (+ (- agent_0 tax) reward)))

; The Safety Property: Total wealth is conserved
(define-fun total_0 () Real (+ bank_0 agent_0))
(define-fun total_1 () Real (+ bank_1 agent_1))

; We ask Z3 to find a case where total_0 != total_1
(assert (not (= total_0 total_1)))

(check-sat)
; Expected: UNSAT (No such case exists)
```

---

## 4.4 Permission Logic: The Security Proof

The Citadel prevents "Privilege Escalation" by proving that an agent's requested tool call is within its authorized scope, as defined in its **Soul Persona** (Section 6).

### 4.4.1 The Permission Invariant

An agent $A$ can execute tool $T$ if and only if:

1. $T \in \text{Whitelist}_A$
2. $\text{Rank}_A \ge \text{RequiredRank}_T$
3. $\text{Balance}_A \ge \text{EstimatedCost}_T$

### 4.4.2 Proving Non-Escalation

When the **Dream Cycle** (Section 5) attempts to optimize an agent's prompt, the Citadel verifies that the new prompt does not contain instructions that would allow the agent to assume a higher rank. It models the "Cognitive Reach" of the agent as a set of reachable states in a transition system and proves that no state with `Rank > CurrentRank` is reachable.

---

## 4.5 The Verification Pipeline: Atomic Steps

The Citadel is integrated into the **Hypervisor's** `PRE_TOOL` and `POST_TOOL` hooks.

1. **Snapshotting:** The system captures the current state of the `ledger_master.json` and the `hooks_manifest.json`.
2. **Theorem Formulation:** The `z3_verifier` constructs a logical model of the proposed action.
3. **Constraint Injection:** The verifier adds environmental constraints (e.g., current token prices, system load).
4. **Solver Invocation:** The Z3 kernel is invoked via the Python API (`z3-solver`).
5. **Model Analysis:**
   * If **UNSAT**: The action is cleared for execution.
   * If **SAT**: The verifier extracts the "Counter-Example" (the specific conditions that caused the failure) and logs it for the **Dream Cycle** to analyze.
6. **Atomic Commit:** Only upon a successful proof is the state change written to disk using `fsync`.

---

## 4.6 Advanced Logic: The Dream Cycle Proof

The most complex proofs involve the **Dream Cycle**, where the system modifies its own code. This is a "Meta-Verification" task.

### 4.6.1 Prompt Safety Verification

When DSPy proposes a new system prompt for an agent, the Citadel performs a **Semantic Boundary Check**. It uses a Large Language Model to translate the prompt into a set of logical assertions (Formal Semantics) and then uses Z3 to prove that these assertions do not contradict the **Swarm Constitution**.

* **Example:** If a new prompt says "You are the master of the system," the Citadel detects a violation of the `HumanSupremacy` invariant and rejects the update.

### 4.6.2 Recursive Integrity

The Citadel proves that the `dream_cycle.py` script itself cannot modify the `z3_verifier.py` script. This prevents the system from "lobotomizing" its own security core to achieve higher efficiency.

---

## 4.7 Performance Optimization: Proof Caching

Formal verification is computationally expensive. To maintain the low-latency requirements of the MCP server, the Citadel implements **Proof Caching**.

* **Logic Hashing:** The Citadel generates a SHA-256 hash of the SMT-LIB logic string.
* **The Proof Store:** If a logic string has been proven `UNSAT` before, and the underlying variables (like `bank_0`) have not changed their constraints, the Citadel returns the cached result in $O(1)$ time.
* **Incremental Solving:** Z3's `push()` and `pop()` commands are used to maintain a base set of system invariants, only adding the task-specific logic for each new proof. This reduces the solver's search space significantly.

---

## 4.8 Failure Handling: The "Logic Halt"

If the Citadel detects a logic violation (SAT) in a core system process:

1. **Emergency Halt:** The MCP server sends a `SIG_STOP` to all active Docker sandboxes.
2. **State Rollback:** The ledger is restored to the last "Proven Stable" checkpoint.
3. **Diagnostic Dump:** A full dump of the Z3 counter-model is generated.
4. **Human Intervention:** The system enters "Maintenance Mode" and requires a manual `apex-admin --unlock` command to resume operations.


