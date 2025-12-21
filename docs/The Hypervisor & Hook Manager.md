# 🛡️ SECTION 3: THE HYPERVISOR & HOOK MANAGER

**Module ID:** `APEX-HYP-003`  
**Atomic Level:** Middleware Priority Queues, AST-Based Security, Docker Runtime Interception, and Self-Healing Logic.

---

## 3.1 The Philosophy of the Citadel Gate

The **Hypervisor** is the non-bypassable security and orchestration layer of the Apex ecosystem. In a system where autonomous agents possess the capability to execute code and manage capital, the Hypervisor serves as the "Citadel Gate"—the thin, impenetrable line between an agent's cognitive "thought" (the prompt) and its physical "action" (the tool call).

Unlike traditional middleware, the Apex Hypervisor does not merely log events; it performs **Deep Packet Inspection (DPI)** on the JSON-RPC stream. It operates on a "Zero Trust" architecture: no command is executed, no prompt is delivered, and no result is returned without passing through a multi-stage validation pipeline.

---

## 3.2 The Hook Pipeline: Chain of Responsibility

The Hypervisor utilizes a **Chain of Responsibility** pattern to manage system behavior. Every interaction is treated as a "Payload" that must traverse a sequence of **Hooks**.

### 3.2.1 Hook Priority and Execution Order

Hooks are registered with a numeric priority (1–100). The Hypervisor executes them in ascending order. If any hook in the chain returns a `HALT` signal, the entire execution pipeline is terminated, and an error is returned to the caller.

* **Priority 1–20 (System Integrity):** Hooks that inject critical state (Fiscal status, Memory context).
* **Priority 21–50 (Security & Safety):** Hooks that perform AST scanning, regex filtering, and permission checks.
* **Priority 51–80 (Optimization):** Hooks that prune context windows or compress tool outputs.
* **Priority 81–100 (Recovery & Logging):** Hooks that handle self-healing retries and telemetry.

### 3.2.2 The Hook Manifest (`hooks_manifest.json`)

The behavior of the Hypervisor is governed by a version-controlled manifest. This allows the system to evolve its security posture without modifying the core engine code.

```json
{
  "version": "2.4.0",
  "policy": "strict-isolation",
  "hooks": [
    {
      "id": "fiscal_injector",
      "type": "PRE_PROMPT",
      "priority": 5,
      "module": "src.hooks.economics.FiscalStatusHook",
      "config": { "warn_at": 10.0, "halt_at": -100.0 }
    },
    {
      "id": "python_ast_guard",
      "type": "PRE_TOOL",
      "priority": 25,
      "target_tool": "execute_python",
      "module": "src.hooks.security.ASTScannerHook",
      "config": {
        "blocked_imports": ["os", "subprocess", "socket", "requests"],
        "blocked_calls": ["eval", "exec", "getattr", "setattr"]
      }
    }
  ]
}
```

---

## 3.3 Phase 1: PRE_PROMPT Injection (Cognitive Shaping)

Before a prompt is sent to the LLM, the Hypervisor "shapes" the agent's cognition by injecting mandatory environmental context.

### 3.3.1 Fiscal Reality Injection

The `FiscalStatusHook` queries the **Master Compensation Engine** to retrieve the agent's current balance, streak, and debt status. It appends a high-priority block to the system prompt.

* **Atomic Logic:** If `balance < 0`, the hook injects a "Debt Stressor" prompt: *"WARNING: You are in debt. Your earnings are currently garnished. Failure on this task will lead to immediate Bankruptcy."*
* **Impact:** This forces the LLM to prioritize low-token, high-certainty solutions over experimental or verbose ones.

### 3.3.2 Semantic Memory Injection

The `MemoryContextHook` uses the user's input to perform a vector search in the **Vector Store**. It injects the top-K most relevant historical code snippets or documentation into the prompt, ensuring the agent has "Long-Term Memory" of the project.

---

## 3.4 Phase 2: PRE_TOOL Validation (The Security Sieve)

When an agent attempts to call a tool (e.g., `execute_bash` or `execute_python`), the Hypervisor performs a multi-layered security audit.

### 3.4.1 AST-Based Static Analysis

For Python code, regex is insufficient because of obfuscation techniques (e.g., `getattr(__builtins__, 'ev' + 'al')`). The Hypervisor uses the `ast` (Abstract Syntax Tree) module to perform a recursive descent audit of the code.

1. **Parsing:** The code is converted into a tree of nodes.
2. **Import Blocking:** The scanner identifies `Import` and `ImportFrom` nodes. If an agent attempts to import `os` or `subprocess` to escape the sandbox, the hook returns a `SecurityViolation`.
3. **Dunder Method Protection:** The scanner blocks access to `__subclasses__`, `__globals__`, and `__builtins__`, which are common vectors for sandbox escapes in Python.
4. **Attribute Access Control:** It prevents the use of `getattr` and `setattr` with dynamic strings, forcing the agent to use explicit, auditable code.

### 3.4.2 Regex-Based Shell Guard

For Bash commands, the Hypervisor uses a high-performance Rust-based regex engine to block dangerous patterns:

* **Path Traversal:** Blocks `..`, `/etc/`, `/root/`, and `/dev/`.
* **Permission Manipulation:** Blocks `chmod`, `chown`, `sudo`.
* **Network Exfiltration:** Blocks `curl`, `wget`, `nc`, and `ping` unless a `NetworkGrant` is present in the agent's metadata.

---

## 3.5 Phase 3: Runtime Interception (Docker Orchestration)

If the security audit passes, the Hypervisor manages the execution within the Docker Sandbox.

### 3.5.1 Transient Container Lifecycle

The Hypervisor does not use persistent containers. For every tool call:

1. **Provision:** It selects a "Warm" container from the pool.
2. **Mount:** It performs a read-only bind mount of the project directory into `/workspace`.
3. **Execute:** It uses `docker exec` to run the command under a non-privileged user (`uid: 1000`).
4. **Cleanup:** After execution, the `/tmp` and `/workspace/scratch` directories are wiped.

### 3.5.2 Resource Metering

The Hypervisor monitors the container's resource usage in real-time via the `/sys/fs/cgroup` interface.

* **CPU Throttling:** If the agent exceeds its `cpu_quota`, the Hypervisor pauses the execution and returns a `ResourceExhausted` error.
* **Memory OOM:** If the agent hits the 512MB limit, the container is killed, and the agent is penalized for "Inefficient Memory Management."

---

## 3.6 Phase 4: POST_TOOL Recovery (Self-Healing)

The Hypervisor is responsible for system resilience. If a tool call fails due to a non-security error (e.g., a `SyntaxError` or a missing package), the Hypervisor triggers the **Self-Healing Protocol**.

### 3.6.1 The "Cognitive Retry" Logic

Instead of returning the error to the user, the Hypervisor intercepts the failure and performs the following:

1. **Error Analysis:** It categorizes the error (e.g., `ImportError`, `LogicError`, `Timeout`).
2. **Retry Prompting:** It sends a hidden message to the agent: *"Your last action failed with: [ERROR]. You have 1 attempt to fix this. Analyze the traceback and provide a corrected version. Note: This retry costs 5 APX."*
3. **State Tracking:** If the second attempt fails, the Hypervisor halts the task, marks it as `FAILED`, and triggers the **Master Compensation Engine** to deduct the full penalty.

### 3.6.2 Output Sanitization

Before returning the result to the LLM client, the Hypervisor prunes the output. If a command generates 10,000 lines of logs, the Hypervisor truncates it to the first 50 and last 50 lines, adding a summary: `[... 9,900 lines truncated to save context ...]`. This prevents "Context Window Flooding."

---

## 3.7 Telemetry and Audit Logging

Every action taken by the Hypervisor is logged to `data/audit_log.jsonl`. This log is immutable and serves as the primary dataset for the **Dream Cycle** (Section 5).

* **Trace ID:** Every request has a unique Trace ID that links the Prompt -> Tool Call -> AST Scan -> Docker Output -> Financial Transaction.
* **Security Alerts:** Any `HALT` signal triggered by a security hook is flagged for immediate human review.


