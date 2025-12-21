"""
Soul Parser - Agent Persona Compiler
Module ID: APEX-SOUL-006
Version: 0.1.0

Transforms Markdown agent specifications into compiled system prompts.
Validates YAML frontmatter, extracts skill trees, and compiles cognitive instructions.

VERSION CONTROL FOOTER
File: src/agents/soul_parser.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

import yaml
import frontmatter
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, ValidationError, field_validator
from src.core.constants import AGENTS_DIR, REQUIRED_PERSONA_FIELDS


class AgentEconomics(BaseModel):
    """Agent economic parameters."""

    base_pay_rate: float
    complexity_access: int
    bond_rate: float
    royalty_share: float
    penalty_multiplier: float

    @field_validator("complexity_access")
    @classmethod
    def validate_complexity_access(cls, v: int) -> int:
        """Validate complexity access level."""
        if not 1 <= v <= 5:
            raise ValueError("Complexity access must be between 1 and 5")
        return v


class AgentCognition(BaseModel):
    """Agent cognitive configuration."""

    model_preference: str
    temperature: float
    max_tokens_per_turn: int
    context_strategy: str


class AgentPermissions(BaseModel):
    """Agent permission matrix."""

    tools: list[str]
    filesystem: Dict[str, Any]
    network: Dict[str, Any]


class AgentEvolution(BaseModel):
    """Agent evolution metadata."""

    generation: int
    parent_hash: str
    last_optimized: str


class AgentGenotype(BaseModel):
    """Complete YAML frontmatter specification (Genotype)."""

    agent_id: str
    name: str
    role: str
    tier: str
    economics: AgentEconomics
    cognition: AgentCognition
    permissions: AgentPermissions
    evolution: AgentEvolution

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        """Validate agent tier."""
        valid_tiers = ["novice", "established", "advanced", "expert", "master"]
        if v not in valid_tiers:
            raise ValueError(f"Tier must be one of {valid_tiers}")
        return v


class PersonaCorruptionError(Exception):
    """Raised when agent persona frontmatter is invalid."""

    pass


class SoulParser:
    """
    Compiler that transforms Markdown agent specifications into system prompts.

    Stages:
    1. Genetic Extraction & Validation (YAML frontmatter)
    2. Fiscal Integrity Check (compare with ledger)
    3. Markdown Phenotype Parsing (behavior directives)
    4. System Prompt Compilation (token-optimized output)
    """

    def __init__(self):
        """Initialize the Soul Parser."""
        self.parsed_personas: Dict[str, Dict[str, Any]] = {}

    def parse_persona_file(self, persona_path: Path) -> Tuple[AgentGenotype, str]:
        """
        Parse a Markdown agent file and extract genotype + phenotype.

        Args:
            persona_path: Path to agent Markdown file.

        Returns:
            Tuple of (parsed AgentGenotype, markdown body)

        Raises:
            PersonaCorruptionError: If frontmatter is invalid.
        """
        try:
            with open(persona_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except Exception as e:
            raise PersonaCorruptionError(f"Failed to parse {persona_path}: {e}")

        # Extract and validate YAML frontmatter
        try:
            genotype = AgentGenotype(
                agent_id=post.metadata.get("agent_id"),
                name=post.metadata.get("name"),
                role=post.metadata.get("role"),
                tier=post.metadata.get("tier"),
                economics=AgentEconomics(**post.metadata.get("economics", {})),
                cognition=AgentCognition(**post.metadata.get("cognition", {})),
                permissions=AgentPermissions(**post.metadata.get("permissions", {})),
                evolution=AgentEvolution(**post.metadata.get("evolution", {})),
            )
        except ValidationError as e:
            raise PersonaCorruptionError(f"Genotype validation failed: {e}")

        return genotype, post.content

    def parse_semantic_blocks(self, markdown_body: str) -> Dict[str, str]:
        """
        Parse Markdown body into semantic blocks.

        Expected sections:
        - # 🧠 SYSTEM IDENTITY
        - # 🧱 ARCHITECTURAL CONSTRAINTS
        - # 💰 FISCAL PROTOCOL
        - # 🧱 MANDATORY FOOTER (output template)

        Args:
            markdown_body: Raw markdown content.

        Returns:
            Dictionary of semantic blocks.
        """
        blocks = {}
        current_block = None
        current_content = []

        for line in markdown_body.split("\n"):
            if line.startswith("# "):
                if current_block:
                    blocks[current_block] = "\n".join(current_content).strip()
                current_block = line[2:].strip()
                current_content = []
            else:
                current_content.append(line)

        if current_block:
            blocks[current_block] = "\n".join(current_content).strip()

        return blocks

    def compile_system_prompt(
        self, genotype: AgentGenotype, phenotype_blocks: Dict[str, str]
    ) -> str:
        """
        Compile a complete system prompt from genotype and phenotype.

        Generates a token-optimized prompt with:
        - Agent identity and mission
        - Architectural constraints
        - Fiscal awareness
        - Output format template

        Args:
            genotype: Parsed YAML frontmatter.
            phenotype_blocks: Parsed Markdown sections.

        Returns:
            Complete system prompt string.
        """
        prompt_parts = [
            f"## Agent Identity: {genotype.name}",
            f"You are agent '{genotype.agent_id}' with role '{genotype.role}' at tier '{genotype.tier}'.",
            "",
        ]

        # Inject system identity
        if "SYSTEM IDENTITY" in phenotype_blocks:
            prompt_parts.append(phenotype_blocks["SYSTEM IDENTITY"])
            prompt_parts.append("")

        # Inject architectural constraints
        if "ARCHITECTURAL CONSTRAINTS" in phenotype_blocks:
            prompt_parts.append("## Your Constraints")
            prompt_parts.append(phenotype_blocks["ARCHITECTURAL CONSTRAINTS"])
            prompt_parts.append("")

        # Inject fiscal protocol
        if "FISCAL PROTOCOL" in phenotype_blocks:
            prompt_parts.append("## Fiscal Awareness")
            prompt_parts.append(phenotype_blocks["FISCAL PROTOCOL"])
            prompt_parts.append("")

        # Append economic context
        prompt_parts.append("## Your Economics")
        prompt_parts.append(f"- Base Pay Rate: {genotype.economics.base_pay_rate} APX/hour")
        prompt_parts.append(
            f"- Max Complexity Access: Level {genotype.economics.complexity_access}"
        )
        prompt_parts.append(f"- Bond Rate: {genotype.economics.bond_rate * 100:.0f}%")
        prompt_parts.append("")

        # Append cognitive configuration
        prompt_parts.append("## Your Cognitive Style")
        prompt_parts.append(
            f"- Preferred Model: {genotype.cognition.model_preference}"
        )
        prompt_parts.append(f"- Temperature: {genotype.cognition.temperature}")
        prompt_parts.append(f"- Max Tokens per Turn: {genotype.cognition.max_tokens_per_turn}")
        prompt_parts.append("")

        # Append output template
        if "MANDATORY FOOTER" in phenotype_blocks:
            prompt_parts.append("## Output Format (MANDATORY)")
            prompt_parts.append(phenotype_blocks["MANDATORY FOOTER"])

        return "\n".join(prompt_parts)

    def awaken_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Fully "awaken" an agent by compiling its complete cognitive system.

        Args:
            agent_id: Agent identifier (e.g., "polyglot_builder_01").

        Returns:
            Dictionary containing compiled system prompt and metadata.

        Raises:
            PersonaCorruptionError: If agent persona is invalid.
        """
        persona_path = AGENTS_DIR / f"{agent_id}.md"

        if not persona_path.exists():
            raise PersonaCorruptionError(f"Agent persona not found: {persona_path}")

        genotype, phenotype_body = self.parse_persona_file(persona_path)
        phenotype_blocks = self.parse_semantic_blocks(phenotype_body)
        system_prompt = self.compile_system_prompt(genotype, phenotype_blocks)

        compiled_agent = {
            "agent_id": genotype.agent_id,
            "name": genotype.name,
            "role": genotype.role,
            "tier": genotype.tier,
            "genotype": genotype.model_dump(),
            "system_prompt": system_prompt,
            "phenotype_blocks": phenotype_blocks,
        }

        self.parsed_personas[agent_id] = compiled_agent
        return compiled_agent

    def list_available_agents(self) -> list[str]:
        """List all available agent personas in the agents directory."""
        agent_files = list(AGENTS_DIR.glob("*.md"))
        return [f.stem for f in agent_files]


# Global Soul Parser instance
_soul_parser_instance: Optional[SoulParser] = None


def get_soul_parser() -> SoulParser:
    """Get or create the global Soul Parser instance."""
    global _soul_parser_instance
    if _soul_parser_instance is None:
        _soul_parser_instance = SoulParser()
    return _soul_parser_instance
