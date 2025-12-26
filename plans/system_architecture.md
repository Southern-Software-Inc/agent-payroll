# APEX System Architecture & Data Flow Documentation

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "APEX Meritocratic Autonomous Environment"
        subgraph "Client Layer"
            LLM[LLM Client<br/>Claude/Gemini/GPT]
            UI[User Interface]
        end
        
        subgraph "Protocol Layer"
            MCP[MCP Server<br/>JSON-RPC 2.0 Hub]
        end
        
        subgraph "Security Layer"
            HV[Hypervisor<br/>Hook Manager]
            CIT[Citadel<br/>Z3 Verifier]
        end
        
        subgraph "Core Services"
            MCE[Master Compensation<br/>Engine]
            SP[Soul Parser<br/>Agent Compiler]
            DC[Dream Cycle<br/>Learning Engine]
            MEM[Semantic Memory<br/>Vector Store]
        end
        
        subgraph "Execution Layer"
            AG[Agent Swarm<br/>Personas]
            DOCK[Docker Sandbox<br/>Isolation]
        end
        
        subgraph "Persistence Layer"
            LED[Ledger<br/>ACID JSON]
            VEC[Vector DB<br/>HNSW Index]
            AUD[Audit Log<br/>Immutable]
        end
    end
    
    LLM --> MCP
    UI --> MCP
    MCP --> HV
    HV --> CIT
    HV --> MCE
    HV --> SP
    HV --> MEM
    SP --> AG
    AG --> DOCK
    MCE --> LED
    MEM --> VEC
    HV --> AUD
    DC --> SP
    DC --> MEM
```

## 2. Component Interaction Matrix

| Component | MCP Server | Hypervisor | Citadel | MCE | Soul Parser | Dream Cycle | Memory | Agents |
|-----------|------------|------------|---------|-----|-------------|-------------|--------|--------|
| **MCP Server** | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Hypervisor** | ✓ | - | ✓ | ✓ | ✓ | - | ✓ | ✓ |
| **Citadel** | ✓ | ✓ | - | ✓ | - | - | - | - |
| **MCE** | ✓ | ✓ | ✓ | - | - | - | - | ✓ |
| **Soul Parser** | ✓ | ✓ | - | - | - | ✓ | - | ✓ |
| **Dream Cycle** | ✓ | - | - | - | ✓ | - | ✓ | - |
| **Memory** | ✓ | ✓ | - | - | - | ✓ | - | ✓ |
| **Agents** | ✓ | ✓ | - | ✓ | ✓ | - | ✓ | - |

## 3. Detailed Data Flow Diagrams

### 3.1 Agent Task Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant MCP
    participant Hypervisor
    participant MCE
    participant SoulParser
    participant Agent
    participant Docker
    participant Citadel
    participant Memory
    
    User->>MCP: Submit Task Request
    MCP->>Hypervisor: PRE_PROMPT Phase
    Hypervisor->>MCE: Inject Fiscal Context
    Hypervisor->>Memory: Inject Semantic Context
    Hypervisor->>SoulParser: Compile Agent Persona
    SoulParser->>Agent: Awaken Agent with System Prompt
    Agent->>MCP: Request Tool Execution
    MCP->>Hypervisor: PRE_TOOL Phase
    Hypervisor->>Docker: Execute in Sandbox
    Docker->>Hypervisor: Return Tool Output
    Hypervisor->>MCP: POST_TOOL Phase
    MCP->>Citadel: Verify Transaction
    Citadel->>MCE: Update Ledger
    MCE->>Memory: Store Experience
    MCP->>User: Return Task Result
```

### 3.2 Financial Transaction Flow

```mermaid
flowchart TD
    START([Task Completion]) --> VERIFY{Citadel Verification}
    VERIFY -->|Valid| CHECK_SOLVENCY[Check Agent Solvency]
    VERIFY -->|Invalid| REJECT[Reject Transaction]
    CHECK_SOLVENCY -->|Sufficient| UPDATE_LEDGER[Update Ledger State]
    CHECK_SOLVENCY -->|Insufficient| REJECT
    UPDATE_LEDGER --> CALC_REWARD[Calculate Reward]
    CALC_REWARD --> APPLY_TAX[Apply Token Tax]
    APPLY_TAX --> UPDATE_BALANCES[Update Agent & System Balances]
    UPDATE_BALANCES --> LOG_TX[Log Transaction]
    LOG_TX --> PERSIST[Persist to Disk]
    PERSIST --> NOTIFY[Notify Agent]
    NOTIFY --> END([Transaction Complete])
    REJECT --> END
```

### 3.3 Memory Storage & Retrieval Flow

```mermaid
stateDiagram-v2
    [*] --> Input: Agent Output
    Input --> Sieve: Semantic Sieve
    Sieve --> Chunk: Text Chunking
    Chunk --> Embed: Vector Embedding
    Embed --> Index: HNSW Indexing
    Index --> Store: Vector Store
    Store --> L1: L1 Context Cache
    
    state Query {
        [*] --> Search: Vector Query
        Search --> Rank: Similarity Ranking
        Rank --> Filter: Utility Filter
        Filter --> Return: Return Results
    }
    
    L1 --> Query
    Query --> [*]
```

### 3.4 Hook Execution Pipeline

```mermaid
graph LR
    subgraph "PRE_PROMPT Phase"
        P1[fiscal_injector<br/>Priority 5]
        P2[memory_context_injector<br/>Priority 10]
    end
    
    subgraph "PRE_TOOL Phase"
        T1[python_ast_guard<br/>Priority 25]
        T2[bash_regex_guard<br/>Priority 30]
        T3[resource_metering<br/>Priority 40]
    end
    
    subgraph "POST_TOOL Phase"
        O1[self_healing_retry<br/>Priority 60]
        O2[output_sanitization<br/>Priority 70]
        O3[audit_logging<br/>Priority 90]
    end
    
    INPUT[Request/Input] --> P1
    P1 --> P2
    P2 --> AGENT_EXEC[Agent Execution]
    AGENT_EXEC --> T1
    T1 --> T2
    T2 --> T3
    T3 --> TOOL_EXEC[Tool Execution]
    TOOL_EXEC --> O1
    O1 --> O2
    O2 --> O3
    O3 --> OUTPUT[Response/Output]
```

## 4. Module Dependency Graph

```mermaid
graph TD
    subgraph "Foundation Layer"
        CONSTANTS[src/core/constants.py]
    end
    
    subgraph "Core Services"
        DREAM[src/core/dream_cycle.py]
        LEDGER[src/economics/ledger.py]
        SOUL[src/agents/soul_parser.py]
        MCP_SRV[src/mcp/server.py]
        HOOKS[src/hooks/__init__.py]
        MEMORY[src/memory/__init__.py]
        CITADEL[src/citadel/__init__.py]
    end
    
    subgraph "Application Layer"
        MAIN[main.py]
        TESTS[tests/]
    end
    
    CONSTANTS --> DREAM
    CONSTANTS --> LEDGER
    CONSTANTS --> SOUL
    CONSTANTS --> MCP_SRV
    CONSTANTS --> HOOKS
    CONSTANTS --> MEMORY
    
    LEDGER --> MCP_SRV
    CITADEL --> LEDGER
    SOUL --> DREAM
    MEMORY --> DREAM
    
    DREAM --> MAIN
    LEDGER --> MAIN
    SOUL --> MAIN
    MCP_SRV --> MAIN
    HOOKS --> MAIN
    MEMORY --> MAIN
    
    LEDGER --> TESTS
    SOUL --> TESTS
```

## 5. State Machine Diagrams

### 5.1 Agent Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> Inactive: Agent Created
    Inactive --> Available: Persona Compiled
    Available --> Busy: Task Assigned
    Busy --> Available: Task Complete
    Busy --> Warning: Performance Issues
    Warning --> Busy: Performance Improved
    Warning --> Restricted: PIP Initiated
    Restricted --> Busy: PIP Complete
    Restricted --> Bankrupt: Debt Ceiling Breach
    Bankrupt --> Restricted: Debt Repaid
    Bankrupt --> [*]: Agent Terminated
```

### 5.2 MCP Request State Machine

```mermaid
stateDiagram-v2
    [*] --> Received: JSON-RPC Request
    Received --> Validated: Structure Check
    Validated --> Registered: Add to Registry
    Registered --> Processing: Route to Handler
    Processing --> Success: Handler Returns
    Processing --> Error: Handler Fails
    Processing --> Timeout: TTL Expired
    Success --> Responding: Build Response
    Error --> Responding: Build Error
    Timeout --> Responding: Timeout Error
    Responding --> Completed: Send Response
    Completed --> [*]
```

### 5.3 Transaction State Machine

```mermaid
stateDiagram-v2
    [*] --> Proposed: Transaction Initiated
    Proposed --> Verified: Citadel Check
    Verified --> Locked: Funds Escrowed
    Verified --> Rejected: Verification Failed
    Locked --> Executed: Task Complete
    Locked --> Refunded: Task Failed
    Executed --> Committed: Ledger Updated
    Refunded --> Released: Funds Returned
    Committed --> [*]
    Released --> [*]
    Rejected --> [*]
```

## 6. Data Model Relationships

```mermaid
erDiagram
    AGENT {
        string agent_id PK
        string name
        string role
        string tier
        json economics
        json cognition
        json permissions
        json evolution
    }
    
    LEDGER {
        json metadata
        json system_bank
        json agents
        array transaction_log
    }
    
    TRANSACTION {
        string tx_id PK
        string timestamp
        string from_agent FK
        string to_agent FK
        float amount
        string tx_type
        string task_ref
        string checksum
    }
    
    MEMORY_CHUNK {
        string id PK
        string content
        string agent_id FK
        string task_id
        string file_path
        datetime timestamp
        float utility_score
        array vector
        string status
    }
    
    DREAM_SESSION {
        string session_id PK
        string agent_id FK
        datetime timestamp
        array issues_identified
        array optimizations_proposed
        float temperature_adjustment
        json prompt_changes
        float success_rate_improvement
        boolean verified
    }
    
    AGENT ||--o{ TRANSACTION : "from/to"
    AGENT ||--o{ MEMORY_CHUNK : "creates"
    AGENT ||--o{ DREAM_SESSION : "optimizes"
    LEDGER ||--o{ TRANSACTION : "contains"
```

## 7. Security Architecture Flow

```mermaid
graph TB
    subgraph "Security Boundaries"
        subgraph "User Space"
            USER[User Request]
        end
        
        subgraph "MCP Boundary"
            MCP[MCP Server]
        end
        
        subgraph "Hypervisor Boundary"
            HOOKS[Hook Manager]
            AST[AST Scanner]
            REGEX[Regex Guard]
        end
        
        subgraph "Sandbox Boundary"
            DOCKER[Docker Container]
            CGROUPS[Cgroup Limits]
            MOUNTS[Read-Only Mounts]
        end
        
        subgraph "System Boundary"
            FILESYSTEM[Host Filesystem]
            NETWORK[Network Stack]
        end
    end
    
    USER --> MCP
    MCP --> HOOKS
    HOOKS --> AST
    HOOKS --> REGEX
    AST --> DOCKER
    REGEX --> DOCKER
    DOCKER --> CGROUPS
    DOCKER --> MOUNTS
    MOUNTS -.-> FILESYSTEM
    DOCKER -.->|Blocked| NETWORK
```

## 8. Performance Optimization Points

### 8.1 Critical Path Analysis

1. **MCP Request Handling** (Latency Critical)
   - Async I/O optimization
   - Request batching
   - Connection pooling

2. **Ledger Operations** (Throughput Critical)
   - Write-ahead logging
   - Batch commits
   - In-memory caching

3. **Vector Search** (Latency Critical)
   - HNSW optimization
   - Query caching
   - Approximate search

4. **Agent Compilation** (Startup Critical)
   - Persona caching
   - Pre-compilation
   - Template optimization

### 8.2 Bottleneck Identification

```mermaid
graph LR
    INPUT[Input Request] --> P1[Parse: 1ms]
    P1 --> P2[Hook PRE_PROMPT: 5ms]
    P2 --> P3[Agent LLM Call: 100-1000ms]
    P3 --> P4[Hook PRE_TOOL: 2ms]
    P4 --> P5[Tool Execution: 10-5000ms]
    P5 --> P6[Hook POST_TOOL: 3ms]
    P6 --> P7[Ledger Update: 5ms]
    P7 --> P8[Memory Store: 10ms]
    P8 --> OUTPUT[Response: 1ms]
    
    style P3 fill:#ff9999
    style P5 fill:#ff9999
```

## 9. Scaling Architecture

### 9.1 Horizontal Scaling Points

1. **MCP Server Cluster**
   - Load balancer distribution
   - Shared state via Redis
   - Request affinity

2. **Agent Pool**
   - Dynamic scaling
   - Resource allocation
   - Load-based routing

3. **Vector Store Cluster**
   - Sharded indexing
   - Distributed search
   - Replication

### 9.2 Vertical Scaling Considerations

1. **Memory Requirements**
   - Agent context: 1-10MB per agent
   - Vector cache: 2-10GB
   - Ledger cache: 100MB-1GB

2. **CPU Requirements**
   - LLM inference: GPU preferred
   - Vector operations: Multi-core
   - Transaction processing: Single-threaded

3. **Storage Requirements**
   - Ledger: 100MB-1GB
   - Vector DB: 10-100GB
   - Audit logs: 1-10GB/day

## 10. Failure Mode Analysis

### 10.1 Single Points of Failure

1. **Ledger File**
   - Mitigation: WAL + backups
   - Recovery: Replay from WAL

2. **MCP Server**
   - Mitigation: Process supervision
   - Recovery: Automatic restart

3. **Docker Daemon**
   - Mitigation: Health checks
   - Recovery: Service restart

### 10.2 Cascade Failure Prevention

```mermaid
graph TB
    subgraph "Circuit Breaker Pattern"
        NORMAL[Normal Operation]
        DEGRADED[Degraded Mode]
        ISOLATED[Isolated Mode]
        RECOVERY[Recovery Mode]
    end
    
    NORMAL -->|Error Rate > 5%| DEGRADED
    DEGRADED -->|Error Rate > 20%| ISOLATED
    ISOLATED -->|Manual Intervention| RECOVERY
    RECOVERY -->|Health Check Pass| NORMAL
    DEGRADED -->|Error Rate < 1%| NORMAL
```

This architecture documentation provides a comprehensive view of the APEX system's structure, data flows, and operational characteristics. The diagrams illustrate the complex interactions between components while maintaining clarity about the system's design principles and security boundaries.