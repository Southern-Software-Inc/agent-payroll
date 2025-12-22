"""
The Dream Cycle - Agent Optimization and Cognitive Evolution Engine
Module ID: APEX-DREAM-005
Version: 0.1.0

The Dream Cycle is the learning and self-improvement mechanism for agents.
It analyzes audit logs, identifies failure patterns, and proposes persona optimizations.

Phases:
1. Sleep: Agent enters training mode
2. Replay: Analyze recent task history (audit logs)
3. Analysis: Identify failure patterns and improvement areas
4. Proposal: Generate optimized system prompt
5. Verification: Test optimizations on historical scenarios
6. Awakening: Deploy improved persona

VERSION CONTROL FOOTER
File: src/core/dream_cycle.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json

from src.core.constants import TEMP_DIR, AGENTS_DIR


@dataclass
class DreamSessionResult:
    """Result of a dream cycle session."""
    agent_id: str
    session_id: str
    timestamp: datetime
    issues_identified: List[str]
    optimizations_proposed: List[str]
    temperature_adjustment: float  # New temperature
    prompt_changes: Dict[str, str]  # old -> new sections
    success_rate_improvement: float
    verified: bool


class DreamCycle:
    """
    Agent optimization engine that learns from audit logs and evolves agent personas.
    """

    def __init__(self, audit_log_path: Path = TEMP_DIR / "audit_log.jsonl"):
        """Initialize dream cycle engine."""
        self.audit_log_path = audit_log_path
        self.dream_sessions: List[DreamSessionResult] = []

    async def enter_sleep(self, agent_id: str, lookback_days: int = 7) -> List[Dict[str, Any]]:
        """
        Enter sleep phase: retrieve recent task history for analysis.
        
        Args:
            agent_id: Agent to analyze
            lookback_days: How many days of history to review
            
        Returns:
            List of recent audit log entries
        """
        if not self.audit_log_path.exists():
            return []
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        relevant_logs = []
        
        try:
            with open(self.audit_log_path, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("agent_id") != agent_id:
                            continue
                        
                        entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                        if entry_time >= cutoff_time:
                            relevant_logs.append(entry)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        
        return relevant_logs

    def analyze_failure_patterns(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze audit logs to identify failure patterns.
        
        Identifies:
        - Most common error types
        - Tasks with high token waste (verbosity)
        - Security violations
        - Performance trends
        
        Args:
            logs: Audit log entries
            
        Returns:
            Analysis report
        """
        if not logs:
            return {
                "total_tasks": 0,
                "success_rate": 1.0,
                "issues": [],
                "optimization_areas": [],
            }
        
        successes = sum(1 for log in logs if log.get("success_flag", False))
        failures = len(logs) - successes
        success_rate = successes / len(logs) if logs else 1.0
        
        issues = []
        if success_rate < 0.8:
            issues.append(f"Low success rate: {success_rate:.1%}")
        
        # Check for token waste
        avg_tokens = sum(log.get("token_count", 0) for log in logs) / len(logs) if logs else 0
        if avg_tokens > 5000:
            issues.append(f"High token consumption: avg {avg_tokens:.0f} tokens/task")
        
        # Check for security violations
        security_violations = sum(1 for log in logs if "security" in log.get("error_type", "").lower())
        if security_violations > 0:
            issues.append(f"Security violations: {security_violations} incidents")
        
        optimization_areas = self._suggest_optimizations(issues, success_rate)
        
        return {
            "total_tasks": len(logs),
            "success_rate": success_rate,
            "avg_tokens_per_task": avg_tokens,
            "issues": issues,
            "optimization_areas": optimization_areas,
        }

    def _suggest_optimizations(self, issues: List[str], success_rate: float) -> List[str]:
        """Suggest optimizations based on identified issues."""
        optimizations = []
        
        if success_rate < 0.8:
            optimizations.append("Add more detailed error handling examples to system prompt")
            optimizations.append("Increase temperature for more exploratory thinking")
        
        if any("token" in issue.lower() for issue in issues):
            optimizations.append("Reduce temperature for more concise responses")
            optimizations.append("Add emphasis on efficiency in system prompt")
        
        if any("security" in issue.lower() for issue in issues):
            optimizations.append("Reinforce sandbox constraints in system prompt")
            optimizations.append("Add explicit security guidelines")
        
        return optimizations

    async def propose_optimizations(
        self, agent_id: str, analysis: Dict[str, Any]
    ) -> DreamSessionResult:
        """
        Propose persona optimizations based on analysis.
        
        Args:
            agent_id: Agent to optimize
            analysis: Analysis report from analyze_failure_patterns
            
        Returns:
            Dream session result with proposed changes
        """
        session_id = f"dream_{agent_id}_{datetime.now(timezone.utc).timestamp()}"
        
        # Read current persona
        persona_path = AGENTS_DIR / f"{agent_id}.md"
        if not persona_path.exists():
            # Try to find it in subdirectories
            for agent_file in AGENTS_DIR.rglob(f"*{agent_id}*.md"):
                persona_path = agent_file
                break
        
        prompt_changes = {}
        temperature_adjustment = 0.0
        success_improvement = 0.05  # Stub: assume 5% improvement
        
        # Simple heuristic adjustments
        if analysis.get("success_rate", 1.0) < 0.8:
            temperature_adjustment = 0.1
            prompt_changes["temperature"] = "Increased for exploration"
        
        if any("token" in issue.lower() for issue in analysis.get("issues", [])):
            temperature_adjustment = -0.1
            prompt_changes["efficiency_emphasis"] = "Added token cost awareness"
        
        result = DreamSessionResult(
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(timezone.utc),
            issues_identified=analysis.get("issues", []),
            optimizations_proposed=analysis.get("optimization_areas", []),
            temperature_adjustment=temperature_adjustment,
            prompt_changes=prompt_changes,
            success_rate_improvement=success_improvement,
            verified=False,
        )
        
        self.dream_sessions.append(result)
        return result

    async def awaken_agent(self, agent_id: str, optimization: DreamSessionResult) -> bool:
        """
        Awaken agent with optimized persona.
        
        In production, this would:
        1. Create a new generation of the agent persona
        2. Update the ledger with a new generation hash
        3. Reset the agent's recent failure counters
        
        Args:
            agent_id: Agent to awaken
            optimization: Dream session result
            
        Returns:
            True if awakening successful
        """
        # Stub: Mark optimization as verified
        optimization.verified = True
        
        # In production, would update agent file and ledger
        return True


class DreamCycleScheduler:
    """Schedules and manages dream cycle execution for agents."""

    def __init__(self):
        """Initialize scheduler."""
        self.dream_engine = DreamCycle()
        self.scheduled_agents: Dict[str, datetime] = {}

    async def schedule_dream(self, agent_id: str, delay_hours: int = 24) -> None:
        """Schedule a dream cycle for an agent."""
        self.scheduled_agents[agent_id] = datetime.now(timezone.utc) + timedelta(hours=delay_hours)

    async def execute_scheduled_dreams(self) -> List[DreamSessionResult]:
        """Execute all scheduled dreams whose time has come."""
        now = datetime.now(timezone.utc)
        results = []
        
        for agent_id, scheduled_time in list(self.scheduled_agents.items()):
            if scheduled_time <= now:
                # Execute dream cycle
                logs = await self.dream_engine.enter_sleep(agent_id)
                analysis = self.dream_engine.analyze_failure_patterns(logs)
                optimization = await self.dream_engine.propose_optimizations(agent_id, analysis)
                await self.dream_engine.awaken_agent(agent_id, optimization)
                
                results.append(optimization)
                del self.scheduled_agents[agent_id]
        
        return results


# Global instance
_dream_cycle: Optional[DreamCycle] = None
_dream_scheduler: Optional[DreamCycleScheduler] = None


def get_dream_cycle() -> DreamCycle:
    """Get or create global dream cycle engine."""
    global _dream_cycle
    if _dream_cycle is None:
        _dream_cycle = DreamCycle()
    return _dream_cycle


def get_dream_scheduler() -> DreamCycleScheduler:
    """Get or create global dream cycle scheduler."""
    global _dream_scheduler
    if _dream_scheduler is None:
        _dream_scheduler = DreamCycleScheduler()
    return _dream_scheduler


__all__ = [
    "DreamCycle",
    "DreamCycleScheduler",
    "DreamSessionResult",
    "get_dream_cycle",
    "get_dream_scheduler",
]
