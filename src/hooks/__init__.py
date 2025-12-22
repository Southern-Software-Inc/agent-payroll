"""
Hypervisor & Hook Manager - Security and Orchestration Layer
Module ID: APEX-HYP-003
Version: 0.1.0

The Hypervisor is the non-bypassable security layer that intercepts all JSON-RPC streams.
It operates on a Zero Trust architecture with a Chain of Responsibility hook pipeline.

Phases:
- PRE_PROMPT: Cognitive shaping and fiscal injection
- PRE_TOOL: Security validation and AST scanning
- POST_TOOL: Self-healing, output sanitization, and telemetry

VERSION CONTROL FOOTER
File: src/hooks/__init__.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from src.core.constants import HOOKS_MANIFEST_FILE


class HookPhase(Enum):
    """Hook execution phases."""
    PRE_PROMPT = "PRE_PROMPT"
    PRE_TOOL = "PRE_TOOL"
    POST_TOOL = "POST_TOOL"


@dataclass
class Hook:
    """Hook definition."""
    id: str
    phase: HookPhase
    priority: int  # 1-100, executed in ascending order
    module_path: str
    config: Dict[str, Any]
    target_tool: Optional[str] = None  # For PRE_TOOL phase only
    enabled: bool = True

    def __lt__(self, other):
        """Support sorting by priority."""
        return self.priority < other.priority


class HookManager:
    """
    Manages the execution of hooks in the Hypervisor.
    Implements Chain of Responsibility pattern.
    """

    def __init__(self):
        """Initialize hook manager."""
        self.hooks: List[Hook] = []
        self.manifest_path = HOOKS_MANIFEST_FILE
        self._load_manifest()

    def _load_manifest(self) -> None:
        """Load hooks from manifest file."""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                manifest = json.load(f)
                self._parse_manifest(manifest)

    def _parse_manifest(self, manifest: Dict[str, Any]) -> None:
        """Parse manifest and register hooks."""
        for hook_config in manifest.get("hooks", []):
            try:
                phase = HookPhase[hook_config["type"]]
                hook = Hook(
                    id=hook_config["id"],
                    phase=phase,
                    priority=hook_config["priority"],
                    module_path=hook_config["module"],
                    config=hook_config.get("config", {}),
                    target_tool=hook_config.get("target_tool"),
                    enabled=hook_config.get("enabled", True)
                )
                self.hooks.append(hook)
            except (KeyError, ValueError) as e:
                print(f"Warning: Failed to load hook: {e}")

        # Sort by priority (ascending)
        self.hooks.sort()

    async def execute_phase(
        self,
        phase: HookPhase,
        payload: Dict[str, Any],
        target_tool: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute all hooks for a given phase.
        
        Args:
            phase: The execution phase (PRE_PROMPT, PRE_TOOL, POST_TOOL)
            payload: The data to process through hooks
            target_tool: For PRE_TOOL phase, the tool being called
            
        Returns:
            Modified payload after all hooks execute
        """
        relevant_hooks = [
            h for h in self.hooks
            if h.phase == phase and h.enabled
        ]

        # For PRE_TOOL, filter by target tool
        if phase == HookPhase.PRE_TOOL and target_tool:
            relevant_hooks = [
                h for h in relevant_hooks
                if h.target_tool is None or h.target_tool == target_tool
            ]

        for hook in relevant_hooks:
            try:
                payload = await self._execute_hook(hook, payload)
                if payload is None or payload.get("_halt"):
                    break
            except Exception as e:
                print(f"Error executing hook {hook.id}: {e}")
                raise

        return payload

    async def _execute_hook(self, hook: Hook, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single hook (stub implementation)."""
        # This is a placeholder. In production, hooks would be dynamically loaded
        # from their module paths and executed.
        return payload


# Global hook manager instance
_hook_manager: Optional[HookManager] = None


def get_hook_manager() -> HookManager:
    """Get or create the global hook manager instance."""
    global _hook_manager
    if _hook_manager is None:
        _hook_manager = HookManager()
    return _hook_manager


__all__ = [
    "HookManager",
    "HookPhase",
    "Hook",
    "get_hook_manager",
]
