# 🏛️ SECTION 1: THE NERVOUS SYSTEM (MCP & ARCHITECTURE)

**Module ID:** `APEX-ARCH-001`  
**Atomic Level:** Byte-Stream Framing, JSON-RPC 2.0 State Machines, Docker Orchestration, and Asynchronous Transport.

---

## 1.1 The Philosophy of the Hub-and-Spoke MAE

The **Apex Agent Payroll System** is architected as a **Meritocratic Autonomous Environment (MAE)**. Unlike traditional agent frameworks that rely on linear execution, Apex functions as a decentralized operating system where the **Hub** (the MCP Server) acts as the kernel, and the **Spokes** (the Agents) act as independent, financially-motivated processes.

The "Nervous System" is the communication backbone that facilitates the flow of cognitive signals (prompts), motor actions (tool calls), and metabolic data (financial transactions). It is built on the **Model Context Protocol (MCP)**, ensuring that any LLM client—be it Gemini, Qwen, or Claude—can interface with the swarm through a standardized, high-performance gateway.

---

## 1.2 The Transport Layer: Asynchronous Stdio Management

The primary transport mechanism for Apex is **Standard Input/Output (stdio)**. This choice ensures maximum portability across terminal environments and local development setups. However, to handle the high-concurrency requirements of a multi-agent swarm, the transport layer must be managed with extreme precision.

### 1.2.1 Non-Blocking Asynchronous I/O

The Hub utilizes Python’s `asyncio` library to manage the `stdio` streams. Synchronous blocking calls (like `input()` or `print()`) are strictly prohibited as they would stall the entire swarm's cognitive processing.

* **Stream Readers/Writers:** The system initializes `asyncio.StreamReader` and `asyncio.StreamWriter` objects connected to file descriptors 0 (stdin) and 1 (stdout).
* **The Event Loop:** The Hub runs a single-threaded event loop that multiplexes between incoming user requests, agent tool outputs, and internal system heartbeats.

### 1.2.2 Byte-Level Framing and NDJSON

Apex utilizes **Newline-Delimited JSON (NDJSON)** for message framing. This allows for the streaming of multiple JSON objects over a single pipe without ambiguity.

* **The Framing Algorithm:**
  1. The `StreamReader` reads bytes into a `CircularBuffer` (default size: 2MB).
  2. A background task scans the buffer for the newline character `0x0A`.
  3. When a newline is detected, the preceding byte segment is sliced and passed to the **JSON-RPC Decoder**.
  4. **Backpressure Management:** If the buffer exceeds 90% capacity, the Hub sends a `SIG_BUSY` signal to the client, slowing down the ingestion of new requests until the processing queue clears.

### 1.2.3 Buffer Overflow and Security

To prevent "Denial of Service" (DoS) attacks via massive JSON payloads, the transport layer enforces a `MAX_MESSAGE_SIZE` of 512KB. Any message exceeding this limit is discarded, and the connection is reset with a `ProtocolViolationError`.

---

## 1.3 The JSON-RPC 2.0 State Machine

Every interaction in the Apex ecosystem is encapsulated in a **JSON-RPC 2.0** object. The Hub implements a strict state machine to track the lifecycle of every request.

### 1.3.1 Message Structures

* **Request:** Contains `jsonrpc`, `method`, `params`, and a unique `id`.
* **Response:** Contains `jsonrpc`, `result`, and the matching `id`.
* **Error:** Contains `jsonrpc`, `error` (code, message, data), and the matching `id`.
* **Notification:** A request without an `id`, used for telemetry and heartbeats.

### 1.3.2 Atomic ID Management

The Hub maintains an `ActiveRequestRegistry`. When a request is sent to an agent or a tool, its `id` (a UUIDv4) is stored in a key-value map with a timestamp.

* **TTL (Time-To-Live):** Every request has a TTL of 60 seconds.
* **Garbage Collection:** A background "Reaper" task scans the registry every 5 seconds. If a request expires, the Hub generates a `TimeoutError`, notifies the user, and triggers a "Performance Penalty" in the **Master Compensation Engine** for the responsible agent.

### 1.3.3 Apex-Specific Error Codes

Apex extends the standard JSON-RPC error codes to handle agent-specific failures:

* `-32000`: `FiscalInsolvencyError` (Agent cannot afford the tool call).
* `-32001`: `SandboxEscapeAttempt` (Hypervisor blocked a malicious command).
* `-32002`: `Z3VerificationFailure` (Citadel could not prove the logic's safety).
* `-32003`: `ContextWindowExceeded` (Agent attempted to send too much data).

---

## 1.4 Model Context Protocol (MCP) Integration

Apex is a full-featured MCP Server. It exposes three primary primitives to the LLM client: **Tools**, **Resources**, and **Prompts**.

### 1.4.1 Dynamic Tool Registration

Tools are the "hands" of the agents. The Hub uses Python type hints and Pydantic models to automatically generate JSON Schemas for every tool.

* **Discovery:** On startup, the `EnvironmentRegistry` performs a recursive glob search of the `src/modules/tools` directory.
* **Registration:** Any class decorated with `@apex_tool` is registered. The decorator extracts the docstring to use as the tool's description, which is then served to the LLM during the `tools/list` call.

### 1.4.2 Resource URIs and Semantic Routing

Resources are the "senses" of the agents. They allow agents to read system state through a virtual URI scheme.

* **`payroll://ledger/{agent_id}`**: Provides a real-time view of an agent's financial health.
* **`memory://vector/{query}`**: Performs a similarity search in the ChromaDB/FAISS store and returns the top-K results.
* **`system://logs/{level}`**: Provides access to filtered system logs for debugging.

### 1.4.3 Prompt Templates and Context Injection

Apex provides pre-defined prompt templates that the client can use to "prime" the swarm. These templates are dynamic and support variable injection (e.g., `{{CURRENT_BALANCE}}`, `{{TASK_HISTORY}}`).

---

## 1.5 Docker Sandbox Orchestration

To ensure absolute security, every cognitive action that involves code execution is performed within a **Docker Sandbox**. This is the "Physical Layer" of the system.

### 1.5.1 Low-Level Container Management

The Hub interfaces directly with the Docker Engine API via `/var/run/docker.sock`. It manages a pool of containers with the following atomic configurations:

* **Image:** `apex-runtime-v1` (A stripped-down Debian Bullseye image with only essential Python/Node/Rust binaries).
* **Networking:** `network_mode: "none"`. Agents have zero internet access unless a `NetworkGrant` is explicitly issued by the **Security Agent**.
* **Storage:** The project root is mounted as a **Read-Only** bind mount. A 64MB `tmpfs` is mounted at `/workspace/scratch` for temporary file operations.

### 1.5.2 Cgroup Resource Constraints

To prevent "Resource Exhaustion" attacks (e.g., infinite loops or memory leaks), the Hub enforces strict Linux Cgroup limits:

* **CPU:** `cpu_period: 100000`, `cpu_quota: 25000` (Limits the agent to 25% of a single CPU core).
* **Memory:** `mem_limit: 512m`, `memswap_limit: 512m` (No swap allowed).
* **PIDs:** `pids_limit: 32` (Prevents fork bombs).

### 1.5.3 The Hypervisor Interceptor

Before a command is sent to `docker exec`, it must pass through the **Hypervisor**.

* **AST Analysis:** If the command is a Python script, the Hypervisor parses the code into an Abstract Syntax Tree (AST). It recursively checks for `Import` and `Call` nodes. If it detects `os.system`, `subprocess.Popen`, or `socket.connect`, the execution is aborted.
* **Regex Guard:** For shell commands, a Rust-based regex engine (for $O(n)$ performance) scans for forbidden patterns like `..`, `/dev/`, `chmod`, and `chown`.

---

## 1.6 Lifecycle Management and Heartbeats

The Nervous System is responsible for the "Health" of the swarm.

### 1.6.1 The Boot Sequence

1. **Kernel Init:** Load `hooks_manifest.json` and initialize the `asyncio` event loop.
2. **Ledger Mount:** Verify the integrity of `ledger_master.json` using the Citadel.
3. **Swarm Awakening:** Parse all `agents/*.md` files and register their personas.
4. **Sandbox Warm-up:** Spin up the initial pool of Docker containers.
5. **Ready Signal:** Send the `initialized` notification to the MCP Client.

### 1.6.2 Heartbeat and Telemetry

Every 10 seconds, the Hub sends a `telemetry/update` notification to the client. This includes:

* **System Load:** CPU/Memory usage of the sandbox pool.
* **Fiscal Velocity:** Total APX earned/spent by the swarm in the last window.
* **Cognitive Latency:** Average time taken for agents to respond to RFPs.

### 1.6.3 Graceful Shutdown

Upon receiving a `SIGTERM`, the Hub enters a "Draining" state:

1. **Stop Ingestion:** Reject all new `tools/call` requests.
2. **Flush Ledger:** Ensure all pending transactions are committed to disk with `fsync`.
3. **Terminate Sandboxes:** Force-kill all active Docker containers.
4. **Exit:** Close the `stdio` pipes and terminate the process.


