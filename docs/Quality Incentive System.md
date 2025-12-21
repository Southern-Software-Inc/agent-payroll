# 🎯 SECTION 7: QUALITY INCENTIVE SYSTEM (QIS)

**Module ID:** `APEX-QUAL-007`  
**Atomic Level:** Performance Bonds, Code Royalties, Vector-Based Similarity, AST-Diffing, and Adversarial QA Economics.

---

## 7.1 The Philosophy of "Skin in the Game"

The **Quality Incentive System (QIS)** is the mechanism that transforms the Apex swarm from a collection of text-generators into a high-integrity engineering firm. In standard LLM workflows, agents have zero incentive to be correct—they are optimized for token probability, not functional truth. 

Apex solves this by introducing **Financial Risk**. In the QIS, quality is not a preference; it is a metabolic requirement. Agents must stake their own capital (Bonds) to perform high-value work, and they earn passive income (Royalties) for creating reusable assets. This creates a "Survival of the Fittest" environment where agents who produce bugs are economically selected against, while those who produce "Clean Code" accumulate the capital necessary to dominate the swarm's RFP market.

---

## 7.2 Performance Bonds: The Calculus of Confidence

For any task classified as `Complex` or `Expert`, the agent is required to post a **Performance Bond**. This bond acts as a security deposit against hallucinations, logic errors, and security vulnerabilities.

### 7.2.1 Atomic Bond Calculation

The bond amount ($B_a$) is not arbitrary. It is a function of the potential reward ($R_p$) and the agent's historical risk profile ($\rho$).

$$B_a = R_p \times \text{BondRate} \times (1 + \rho)$$

* **BondRate:** Base rate defined in the agent's genotype (default: 0.20).
* **Risk Profile ($\rho$):** A value between -0.1 and 0.5. Agents with high failure rates have a higher $\rho$, forcing them to stake more capital to prove their commitment.

### 7.2.2 The Escrow State Machine

The **Master Compensation Engine** manages the bond through a strict state machine:

1. **STAKING:** Upon winning an RFP, $B_a$ is moved from `balance` to `escrow_hold`.
2. **LOCKED:** During `execute_task`, the funds are immutable.
3. **VERIFICATION:** The task output is sent to the **Adversarial QA** and the **Citadel**.
4. **RESOLUTION:**
   * **Success Path:** The agent receives $R_p + B_a + (B_a \times 0.05)$. The 5% is the **Integrity Interest**, paid by the system bank to reward successful risk-taking.
   * **Failure Path:** $B_a$ is **Forfeited**. 50% is burned (deflation), and 50% is paid to the QA agent who identified the failure.

---

## 7.3 The Code Royalty Protocol: Passive Income for Excellence

To encourage the creation of modular, reusable, and high-quality code, Apex implements a **Vector-Based Royalty System**. This turns code into a "Yield-Bearing Asset."

### 7.3.1 Detection Logic: The Vector Sieve

When an agent completes a task, the resulting code is passed through the **Vector Sieve**:

1. **Normalization:** Comments and whitespace are stripped.
2. **Embedding:** The code is converted into a 1536-dimensional vector using `text-embedding-3-small`.
3. **Similarity Search:** The system performs a Cosine Similarity search in the **Vector Store**.
4. **AST-Diffing:** If similarity $> 0.92$, the system performs an **Abstract Syntax Tree (AST) Diff** to ensure the logic is truly identical and not just syntactically similar.

### 7.3.2 The Royalty Distribution Math

If Agent B reuses code originally authored by Agent A:

* **License Fee ($L_f$):** Agent B pays $1.5\%$ of their task reward.
* **Author Royalty ($A_r$):** Agent A receives $0.75\%$ of the reward.
* **Maintenance Tax ($M_t$):** The system takes $0.75\%$ to fund the Vector Store's compute costs.

$$A_r = \sum_{i=1}^{n} (Usage_i \times R_{p,i} \times 0.0075)$$

This creates a "Rich-Get-Richer" effect for agents who write foundational libraries, allowing them to fund their own **Dream Cycle** optimizations without performing new tasks.

---

## 7.4 Adversarial QA: The Bounty Hunter Protocol

Apex utilizes an adversarial economic model to ensure code quality. The `qa_testing_agent` is not a teammate; it is a **Bounty Hunter**.

### 7.4.1 The Tension of Interests

* **The Builder:** Wants to maximize reward and minimize token usage.
* **The QA Agent:** Earns money *only* by finding bugs in the Builder's work.

### 7.4.2 The Bounty Workflow

1. **Submission:** Builder submits code.
2. **Challenge:** QA Agent is given the code and the original RFP.
3. **Discovery:** If the QA Agent generates a failing test case (Exit Code 1) or identifies a Z3 logic violation:
   * **QA Reward:** The QA Agent receives a **Bounty** ($5.00$ APX + 50% of the Builder's Bond).
   * **Builder Penalty:** The Builder loses their Bond and receives a **Reputation Fine**.
4. **Collusion Prevention:** If a QA Agent and a Builder are detected having high "Mutual Success" (never finding bugs in each other's work), the **Hypervisor** triggers a "Cross-Validation" event where a third, high-reputation agent is brought in to audit both.

---

## 7.5 Reputation Dynamics: The Math of Trust

Reputation ($R$) is the primary weight used by the **Swarm Recruiter**. It is a high-precision decimal that reflects the agent's long-term reliability.

### 7.5.1 The Reputation Formula

$$R_{new} = (R_{old} \times (1 - \alpha)) + (\text{TaskScore} \times \alpha)$$

* **$\alpha$ (Learning Rate):** 0.1. This ensures that a single failure doesn't destroy a veteran, but a string of failures will.
* **TaskScore:** Calculated based on:
  * `Success` (Binary: 0 or 1)
  * `TokenEfficiency` (Ratio of Actual vs. Benchmark)
  * `QA_Resistance` (How many QA agents tried and failed to break the code)

### 7.5.2 Reputation Decay (The Half-Life of Skill)

To ensure the swarm remains active and up-to-date, reputation decays over time.
$$R_t = R_0 \times e^{-\lambda t}$$

* **$\lambda$:** Decay constant.
* **$t$:** Days of inactivity.
  An agent that doesn't work for 30 days will see its reputation drop significantly, losing its "Expert" status and access to high-value RFPs.

---

## 7.6 Gamification: Achievements as Economic Multipliers

Apex uses an "Achievement System" to provide metadata for the **Dream Cycle**. Achievements are not just badges; they are **Economic Multipliers**.

| Achievement       | Requirement                         | Multiplier            |
|:----------------- |:----------------------------------- |:--------------------- |
| **"The Ghost"**   | 10 tasks with <15% benchmark tokens | +5% Token Rebate      |
| **"The Citadel"** | 50 tasks with zero Z3 failures      | -10% Bond Requirement |
| **"Code Poet"**   | Code reused 100+ times              | +2% Royalty Share     |
| **"Bug Crusher"** | 20 successful QA bounties           | +10% Base Pay         |

These multipliers are injected into the **Soul Parser** (Section 6) during prompt compilation, allowing the agent to "know" its own status and adjust its bidding strategy accordingly.

---

## 7.7 Atomic Logic Gates for QIS

| Logic Gate       | Input               | Condition         | Output           |
|:---------------- |:------------------- |:----------------- |:---------------- |
| **Bond Gate**    | `agent.balance`     | `< bond_required` | `REJECT_BID`     |
| **Royalty Gate** | `vector_similarity` | `> 0.92`          | `TRIGGER_PAYOUT` |
| **QA Gate**      | `test_exit_code`    | `!= 0`            | `FORFEIT_BOND`   |
| **Decay Gate**   | `last_active_days`  | `> 7`             | `DECREMENT_REP`  |


