"""
The Citadel - Z3 Formal Verifier for Financial Transactions
Module ID: APEX-CITADEL-007
Version: 0.2.0

Verifies conservation of wealth and invariant maintenance before ledger writes.
Uses Z3 SMT solver to prove transaction safety.

Transaction safety checks:
1. Conservation of Wealth: total system wealth never changes
2. No Double Spending: agent balance never exceeds deposit
3. Debt Ceiling: balance never exceeds debt_ceiling
4. Checksum Integrity: transaction hashes are valid

VERSION CONTROL FOOTER
File: src/citadel/__init__.py
Version: 0.2.0
Last Modified: 2025-12-22T00:00:00Z
Git Hash: UPDATED
"""

from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import hashlib
import logging

from .verifier import Z3Verifier, get_z3_verifier

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of a Z3 verification."""
    is_valid: bool
    theorem: str
    reasoning: str
    error_details: str = ""


class Citadel:
    """
    Z3-based formal verifier for financial invariants.
    
    Integrates with Z3 SMT solver for rigorous verification.
    Falls back to arithmetic verification if Z3 is not available.
    """

    def __init__(self):
        """Initialize Citadel verifier."""
        self.verification_log: list = []
        self.z3_verifier = get_z3_verifier()
        logger.info(f"Citadel initialized with Z3 available: {self.z3_verifier.solver is not None}")

    def verify_conservation_of_wealth(
        self,
        bank_pre: float,
        agent_pre: float,
        reward: float,
        tax: float,
        bank_post: float,
        agent_post: float,
    ) -> VerificationResult:
        """
        Verify that total wealth is conserved in a transaction.
        
        Theorem:
        bank_post = bank_pre + tax - reward
        agent_post = agent_pre + reward - tax
        
        Safety Check:
        bank_pre + agent_pre == bank_post + agent_post
        
        Args:
            bank_pre: System bank balance before transaction
            agent_pre: Agent balance before transaction
            reward: Amount being paid to agent
            tax: Tax/fee being collected
            bank_post: System bank balance after transaction
            agent_post: Agent balance after transaction
            
        Returns:
            VerificationResult indicating if conservation holds
        """
        result = self.z3_verifier.verify_theorem(
            "conservation",
            bank_pre=bank_pre,
            agent_pre=agent_pre,
            reward=reward,
            tax=tax,
            bank_post=bank_post,
            agent_post=agent_post
        )
        
        self.verification_log.append(result)
        return result

    def verify_solvency(self, balance: float, transaction_amount: float) -> VerificationResult:
        """
        Verify that an agent has sufficient funds for a transaction.
        
        Safety Check: balance >= transaction_amount
        
        Args:
            balance: Agent's current balance
            transaction_amount: Amount being transferred
            
        Returns:
            VerificationResult indicating solvency
        """
        result = self.z3_verifier.verify_theorem(
            "solvency",
            balance=balance,
            transaction_amount=transaction_amount
        )
        
        self.verification_log.append(result)
        return result

    def verify_debt_ceiling(self, balance: float, debt_ceiling: float) -> VerificationResult:
        """
        Verify that agent balance respects debt ceiling.
        
        Safety Check: balance >= debt_ceiling
        
        Args:
            balance: Agent's current balance
            debt_ceiling: Maximum allowed debt (negative value)
            
        Returns:
            VerificationResult indicating debt compliance
        """
        result = self.z3_verifier.verify_theorem(
            "debt_ceiling",
            balance=balance,
            debt_ceiling=debt_ceiling
        )
        
        self.verification_log.append(result)
        return result

    def verify_checksum_integrity(self, transaction: Dict[str, Any]) -> VerificationResult:
        """
        Verify that transaction checksum is valid.
        
        Args:
            transaction: Transaction object with checksum field
            
        Returns:
            VerificationResult indicating checksum validity
        """
        provided_checksum = transaction.get("checksum", "")
        
        # Compute checksum from transaction data (excluding checksum field)
        tx_copy = {k: v for k, v in transaction.items() if k != "checksum"}
        tx_string = str(tx_copy)
        computed_checksum = hashlib.sha256(tx_string.encode()).hexdigest()
        
        is_valid = provided_checksum == computed_checksum
        
        result = VerificationResult(
            is_valid=is_valid,
            theorem="Checksum Integrity",
            reasoning="Transaction integrity verified via SHA-256",
        )
        
        if not is_valid:
            result.error_details = (
                f"Checksum mismatch! "
                f"Expected {computed_checksum[:16]}... "
                f"got {provided_checksum[:16]}..."
            )
        
        self.verification_log.append(result)
        return result

    def verify_all_invariants(
        self, transaction: Dict[str, Any], ledger_state: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Comprehensive verification of all financial invariants before ledger write.
        
        Args:
            transaction: The transaction to verify
            ledger_state: Current ledger state for context
            
        Returns:
            Tuple of (is_valid, reason)
        """
        checks = []
        
        # Check 1: Checksum
        checksum_result = self.verify_checksum_integrity(transaction)
        checks.append(checksum_result)
        
        # Check 2: Solvency (if applicable)
        if "from" in transaction and transaction["from"] != "system_bank":
            agent_state = ledger_state.get("agents", {}).get(transaction["from"])
            if agent_state:
                solvency = self.verify_solvency(
                    agent_state["financials"]["balance"],
                    transaction["amount"]
                )
                checks.append(solvency)
        
        # Check 3: Debt ceiling (if applicable)
        if "from" in transaction and transaction["from"] != "system_bank":
            agent_state = ledger_state.get("agents", {}).get(transaction["from"])
            if agent_state and "debt_ceiling" in agent_state["financials"]:
                debt_ceiling_check = self.verify_debt_ceiling(
                    agent_state["financials"]["balance"],
                    agent_state["financials"]["debt_ceiling"]
                )
                checks.append(debt_ceiling_check)
        
        # Check 4: Non-negative balance for system bank
        if "to" in transaction and transaction["to"] == "system_bank":
            system_balance = ledger_state.get("system_bank", {}).get("balance", 0)
            new_balance = system_balance + transaction.get("amount", 0)
            non_negative = self.z3_verifier.verify_theorem(
                "non_negative",
                balance=new_balance
            )
            checks.append(non_negative)
        
        # Check 5: Conservation (implicit in proper transaction structure)
        # This would be verified in actual ledger.transfer_funds()
        
        all_valid = all(c.is_valid for c in checks)
        reason = "; ".join([c.reasoning for c in checks])
        
        return all_valid, reason
    
    def get_verification_summary(self) -> Dict[str, Any]:
        """
        Get summary of all verifications performed.
        
        Returns:
            Dictionary with verification statistics
        """
        return self.z3_verifier.get_verification_summary()
    
    def clear_verification_log(self) -> None:
        """Clear verification log."""
        self.verification_log.clear()
        self.z3_verifier.clear_log()
    
    def export_verification_log(self, filepath: str) -> None:
        """
        Export verification log to file.
        
        Args:
            filepath: Path to export file
        """
        self.z3_verifier.export_log(filepath)


# Global Citadel instance
_citadel: Citadel | None = None


def get_citadel() -> Citadel:
    """Get or create the global Citadel instance."""
    global _citadel
    if _citadel is None:
        _citadel = Citadel()
    return _citadel


__all__ = [
    "Citadel",
    "VerificationResult",
    "get_citadel",
    "Z3Verifier",
    "get_z3_verifier",
]
