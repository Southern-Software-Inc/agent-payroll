# 📑 SECTION 8: SWARM DYNAMICS & COLLABORATIVE BIDDING

**Module ID:** `APEX-SWARM-008`  
**Atomic Level:** RFP Decomposition Heuristics, Merit-Weighted Auction Theory, Internal Communication Bus (ICB) Protocols, Team Synergy Coefficients, and Logic Duel Conflict Resolution.

---

## 8.1 The Philosophy of the Decentralized Swarm

The **Swarm Dynamics** module is the social and political engine of the Apex ecosystem. In traditional multi-agent systems, agents are often "hard-coded" to collaborate or follow a rigid hierarchy. Apex rejects this in favor of a **Decentralized Marketplace of Intelligence**. 

Agents do not work together because they are told to; they work together because it is **Economically Rational**. The swarm operates as a high-frequency auction house where tasks are decomposed into machine-readable **Requests for Proposals (RFPs)**, and agents compete or form "Guilds" to fulfill them. This section defines the atomic protocols for how agents discover work, negotiate prices, communicate in real-time, and resolve logical disputes.

---

## 8.2 RFP Decomposition: The Orchestrator’s Calculus

Before a task reaches the swarm, it must be "Atomized." The **Orchestrator Agent** (the executive) is responsible for taking a vague user request (e.g., "Build a secure login system") and decomposing it into a series of technical RFPs.

### 8.2.1 The RFP Schema (Atomic Specification)

An RFP is a structured JSON object that defines the "Contract" for a task.

```json
{
  "rfp_id": "rfp_uuid_v4",
  "parent_project_id": "proj_uuid",
  "status": "OPEN",
  "constraints": {
    "complexity": "complex",
    "required_tier": "advanced",
    "required_skills": ["python", "cryptography", "jwt"],
    "max_token_budget": 12000,
    "deadline_ms": 45000
  },
  "economics": {
    "ceiling_price": 150.00,
    "bond_required": true,
    "royalty_eligible": true
  },
  "technical_spec": {
    "input_schema": "{...}",
    "output_schema": "{...}",
    "validation_criteria": "must_pass_z3_and_pytest"
  }
}
```

### 8.2.2 Complexity Scoring Heuristics

The Orchestrator uses a **Complexity Scoring Algorithm** to set the `ceiling_price`.

1. **Cyclomatic Estimation:** Predicts the number of logical branches required.
2. **Dependency Weight:** Counts the number of external libraries/APIs involved.
3. **Security Sensitivity:** A multiplier based on whether the task touches the `filesystem` or `network`.
4. **Formula:** $Score = (Branches \times 1.2) + (Deps \times 5.0) + (Security \times 10.0)$.

---

## 8.3 Merit-Weighted Auction Theory

Apex uses a modified **Second-Price Sealed-Bid Auction** (Vickrey Auction) combined with a **Merit Weighting** to select the winning agent.

### 8.3.1 The Bidding Heuristic

When an agent receives an RFP, it runs an internal "Profitability Simulation" to decide its bid ($B$):
$$B = (BasePay \times TimeEst) + (TokenCost \times 1.2) + RiskPremium$$

* **Risk Premium:** If the agent's balance is low, it may bid lower to ensure it wins the work, or higher if the task is outside its core expertise to cover potential bond forfeiture.

### 8.3.2 The Selection Metric: The Value Score ($V$)

The Orchestrator does not simply pick the lowest bid. It picks the highest **Value Score**:
$$V = \frac{R \times C}{B \times T_e}$$

* **$R$ (Reputation):** The agent's historical reliability (Section 7).
* **$C$ (Confidence):** The agent's self-reported probability of success for this specific task.
* **$B$ (Bid Price):** The APX requested.
* **$T_e$ (Estimated Tokens):** The agent's predicted resource consumption.

---

## 8.4 The Internal Communication Bus (ICB)

Once a team is assembled (e.g., a Builder, a QA Agent, and a Security Guardian), they must coordinate. They do this via the **Internal Communication Bus (ICB)**.

### 8.4.1 The `internal_comms` Tool

Agents use a specialized MCP tool to exchange structured messages.

* **Tool:** `send_swarm_message(recipient_id, message_type, payload)`
* **Message Types:** `PLAN_PROPOSAL`, `CODE_REVIEW_REQUEST`, `SECURITY_VETO`, `HANDOFF`.

### 8.4.2 The Anti-Spam Metabolic Tax

To prevent "Infinite Chatter Loops" (where agents talk in circles and drain the user's token budget), every message on the ICB carries a **Metabolic Tax**.

* **Cost:** 0.5 APX per message, deducted from the sender's balance.
* **Logic:** This forces agents to be concise and only communicate when necessary for task success. If an agent's balance hits 0 during a conversation, it is "Muted" until the task is resolved.

---

## 8.5 Team Synergy and Collective Bonuses

Apex recognizes that the whole is often greater than the sum of its parts. It models this through the **Synergy Coefficient ($\chi$)**.

### 8.5.1 The Synergy Bonus ($B_s$)

If a multi-agent swarm completes a project with high efficiency, the system bank pays a **Synergy Bonus**.
$$B_s = (TotalBudget \times 0.15) \times \chi$$

* **$\chi$ (Synergy Coefficient):** Calculated based on the "Communication-to-Action Ratio." Teams that achieve success with fewer, higher-impact messages have a higher $\chi$.

### 8.5.2 Distribution of the Bonus

The bonus is not split equally. It is distributed via **Contribution Analysis**:

1. **The Builder:** Receives 50% (for execution).
2. **The QA/Security:** Receives 30% (for verification).
3. **The Orchestrator:** Receives 20% (for successful decomposition and management).

---

## 8.6 Conflict Resolution: The Logic Duel

In a swarm, agents will inevitably disagree (e.g., the Builder wants to use a library that the Security Agent claims is vulnerable). Apex resolves this through a **Logic Duel**.

### 8.6.1 The Duel Protocol

1. **Escalation:** The disagreeing agents are moved to a "Duel Context."
2. **Assertion:** Each agent must provide a **Formal Assertion** of their position in SMT-LIB logic.
3. **Verification:** The **Citadel (Z3)** attempts to prove both assertions.
4. **Judgment:**
   * If Agent A's logic is proven and Agent B's is refuted: Agent A wins. Agent B is fined for "Logic Obstruction."
   * If both are logically sound but architecturally different: The **Orchestrator** makes a "Discretionary Call" based on the project's `priority` (Speed vs. Security).

---

## 8.7 Swarm Recruitment: The "Recruiter" Logic

The `swarm_recruiter.py` is the module that manages the agent roster. It uses a **Diversity Heuristic** to ensure the swarm is balanced.

### 8.7.1 The Diversity Heuristic

The Recruiter prevents "Cognitive Monocultures" by ensuring:

* **Role Balance:** No more than 60% of the swarm can be of the same `role` (e.g., all Builders).
* **Tier Mixing:** High-value tasks often require a "Master" to oversee "Advanced" agents, creating a mentorship-like structure that the **Dream Cycle** uses to propagate best practices.

### 8.7.2 The "Bounty Hunter" Summoning

If a task is flagged as `Expert` and `Security-Critical`, the Recruiter automatically summons a **Security Guardian** with "Veto Power." This agent does not write code; it only audits the Builder's output. Its reward is tied directly to the Builder's failure (Section 7.4).

---

## 8.8 Atomic Logic Gates for Swarm Dynamics

| Logic Gate         | Input                       | Condition     | Output                 |
|:------------------ |:--------------------------- |:------------- |:---------------------- |
| **Auction Gate**   | `bid_count`                 | `< 2`         | `EXTEND_RFP_DEADLINE`  |
| **Selection Gate** | `value_score`               | `max(V)`      | `AWARD_CONTRACT`       |
| **Chatter Gate**   | `msg_count / task_duration` | `> threshold` | `THROTTLE_COMMS`       |
| **Duel Gate**      | `z3_result`                 | `UNSAT`       | `ENFORCE_LOGIC_WINNER` |

---

## 8.9 Swarm Telemetry: The "Matrix" Dashboard

The system provides a real-time TUI (Terminal User Interface) dashboard (`tui_dashboard.py`) that visualizes the swarm's social dynamics:

* **The Heatmap:** Shows which agents are communicating most frequently.
* **The Auction Ticker:** Displays active RFPs and current high bids.
* **The Duel Log:** Shows ongoing logical disputes and their Z3 resolutions.


