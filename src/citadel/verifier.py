"""
Z3 Formal Verifier for Financial Transactions
Module ID: APEX-CITADEL-007
Version: 0.2.0

Production Z3 verifier for financial invariants.
Implements theorem proving for conservation of wealth, solvency, and debt ceiling.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

try:
    from z3 import *
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    logging.warning("Z3 not available. Using stub implementation.")

from . import VerificationResult


logger = logging.getLogger(__name__)


@dataclass
class Theorem:
    """Mathematical theorem definition for Z3 verification."""
    name: str
    variables: List[str]
    constraints: List[str]
    goal: str
    description: str


class Z3Verifier:
    """
    Production Z3 verifier for financial invariants.
    
    Provides formal verification of:
    1. Conservation of Wealth
    2. Solvency Constraints
    3. Debt Ceiling Compliance
    4. Transaction Integrity
    """
    
    def __init__(self):
        """Initialize Z3 verifier."""
        self.verification_log: List[VerificationResult] = []
        self.theorems = self._define_theorems()
        
        if Z3_AVAILABLE:
            self.solver = Solver()
            self.solver.set("timeout", 30000)  # 30 second timeout
        else:
            self.solver = None
            logger.warning("Z3 solver not initialized - using stub verification")
    
    def _define_theorems(self) -> Dict[str, Theorem]:
        """Define all financial theorems for verification."""
        theorems = {}
        
        # Conservation of Wealth Theorem
        theorems['conservation'] = Theorem(
            name="Conservation of Wealth",
            variables=["bank_pre", "agent_pre", "reward", "tax", "bank_post", "agent_post"],
            constraints=[
                "bank_post == bank_pre + tax - reward",
                "agent_post == agent_pre + reward - tax"
            ],
            goal="bank_pre + agent_pre == bank_post + agent_post",
            description="Total system wealth must remain constant in transactions"
        )
        
        # Solvency Theorem
        theorems['solvency'] = Theorem(
            name="Solvency Constraint",
            variables=["balance", "transaction_amount"],
            constraints=[],
            goal="balance >= transaction_amount",
            description="Agent must have sufficient funds for transactions"
        )
        
        # Debt Ceiling Theorem
        theorems['debt_ceiling'] = Theorem(
            name="Debt Ceiling Constraint",
            variables=["balance", "debt_ceiling"],
            constraints=[],
            goal="balance >= debt_ceiling",
            description="Agent balance cannot exceed debt ceiling"
        )
        
        # Non-Negative Balance Theorem
        theorems['non_negative'] = Theorem(
            name="Non-Negative Balance",
            variables=["balance"],
            constraints=[],
            goal="balance >= 0",
            description="System balances should remain non-negative"
        )
        
        return theorems
    
    def verify_theorem(self, theorem_name: str, **kwargs) -> VerificationResult:
        """
        Verify a specific theorem with given values.
        
        Args:
            theorem_name: Name of theorem to verify
            **kwargs: Values for theorem variables
            
        Returns:
            VerificationResult with theorem validity
        """
        theorem = self.theorems.get(theorem_name)
        if not theorem:
            return VerificationResult(
                is_valid=False,
                theorem=theorem_name,
                reasoning=f"Unknown theorem: {theorem_name}",
                error_details="Theorem not defined"
            )
        
        if not Z3_AVAILABLE or not self.solver:
            # Fallback to simple arithmetic verification
            return self._stub_verify(theorem, **kwargs)
        
        try:
            # Reset solver
            self.solver.push()
            
            # Declare symbolic variables
            variables = {}
            for var_name in theorem.variables:
                variables[var_name] = Real(var_name)
            
            # Add constraints
            for constraint_str in theorem.constraints:
                constraint = eval(constraint_str, {}, variables)
                self.solver.add(constraint)
            
            # Add variable assignments
            for var_name, value in kwargs.items():
                if var_name in variables:
                    self.solver.add(variables[var_name] == value)
            
            # Add negation of goal to test for contradiction
            goal_expr = eval(theorem.goal, {}, variables)
            self.solver.add(Not(goal_expr))
            
            # Check if unsat (theorem holds)
            result = self.solver.check() == unsat
            
            # Pop to clean up
            self.solver.pop()
            
            verification = VerificationResult(
                is_valid=result,
                theorem=theorem.name,
                reasoning=f"Z3 verification: {theorem.description}",
                error_details="" if result else "Theorem violation detected"
            )
            
            self.verification_log.append(verification)
            return verification
            
        except Exception as e:
            # Pop to clean up on error
            try:
                self.solver.pop()
            except:
                pass
            
            logger.error(f"Z3 verification error: {e}")
            return VerificationResult(
                is_valid=False,
                theorem=theorem.name,
                reasoning=f"Z3 verification failed: {str(e)}",
                error_details=str(e)
            )
    
    def _stub_verify(self, theorem: Theorem, **kwargs) -> VerificationResult:
        """
        Stub verification when Z3 is not available.
        Uses simple arithmetic checks.
        """
        try:
            if theorem.name == "conservation":
                bank_pre = kwargs.get("bank_pre", 0)
                agent_pre = kwargs.get("agent_pre", 0)
                reward = kwargs.get("reward", 0)
                tax = kwargs.get("tax", 0)
                bank_post = kwargs.get("bank_post", 0)
                agent_post = kwargs.get("agent_post", 0)
                
                wealth_pre = bank_pre + agent_pre
                wealth_post = bank_post + agent_post
                is_valid = abs(wealth_pre - wealth_post) < 1e-6
                
                return VerificationResult(
                    is_valid=is_valid,
                    theorem=theorem.name,
                    reasoning=f"Wealth before: {wealth_pre}, after: {wealth_post}",
                    error_details="" if is_valid else f"Wealth mismatch: {wealth_post - wealth_pre}"
                )
            
            elif theorem.name == "solvency":
                balance = kwargs.get("balance", 0)
                transaction_amount = kwargs.get("transaction_amount", 0)
                is_valid = balance >= transaction_amount
                
                return VerificationResult(
                    is_valid=is_valid,
                    theorem=theorem.name,
                    reasoning=f"Balance {balance} >= Transaction {transaction_amount}",
                    error_details="" if is_valid else f"Insufficient funds: {balance} < {transaction_amount}"
                )
            
            elif theorem.name == "debt_ceiling":
                balance = kwargs.get("balance", 0)
                debt_ceiling = kwargs.get("debt_ceiling", 0)
                is_valid = balance >= debt_ceiling
                
                return VerificationResult(
                    is_valid=is_valid,
                    theorem=theorem.name,
                    reasoning=f"Balance {balance} >= Ceiling {debt_ceiling}",
                    error_details="" if is_valid else f"Debt ceiling exceeded: {balance} < {debt_ceiling}"
                )
            
            elif theorem.name == "non_negative":
                balance = kwargs.get("balance", 0)
                is_valid = balance >= 0
                
                return VerificationResult(
                    is_valid=is_valid,
                    theorem=theorem.name,
                    reasoning=f"Balance {balance} >= 0",
                    error_details="" if is_valid else f"Negative balance: {balance}"
                )
            
            else:
                return VerificationResult(
                    is_valid=False,
                    theorem=theorem.name,
                    reasoning="Stub verification not implemented for this theorem",
                    error_details="Theorem not supported in stub mode"
                )
                
        except Exception as e:
            return VerificationResult(
                is_valid=False,
                theorem=theorem.name,
                reasoning=f"Stub verification error: {str(e)}",
                error_details=str(e)
            )
    
    def verify_transaction_batch(self, transactions: List[Dict[str, Any]]) -> List[VerificationResult]:
        """
        Verify a batch of transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of verification results
        """
        results = []
        
        for tx in transactions:
            # Verify conservation of wealth
            if all(k in tx for k in ["bank_pre", "agent_pre", "reward", "tax", "bank_post", "agent_post"]):
                result = self.verify_theorem("conservation", **tx)
                results.append(result)
            
            # Verify solvency
            if "balance" in tx and "amount" in tx:
                result = self.verify_theorem("solvency", balance=tx["balance"], transaction_amount=tx["amount"])
                results.append(result)
            
            # Verify debt ceiling
            if "balance" in tx and "debt_ceiling" in tx:
                result = self.verify_theorem("debt_ceiling", balance=tx["balance"], debt_ceiling=tx["debt_ceiling"])
                results.append(result)
        
        return results
    
    def get_verification_summary(self) -> Dict[str, Any]:
        """
        Get summary of all verifications performed.
        
        Returns:
            Dictionary with verification statistics
        """
        if not self.verification_log:
            return {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0}
        
        total = len(self.verification_log)
        passed = sum(1 for v in self.verification_log if v.is_valid)
        failed = total - passed
        pass_rate = (passed / total) * 100 if total > 0 else 0
        
        # Group by theorem
        theorem_stats = {}
        for verification in self.verification_log:
            theorem = verification.theorem
            if theorem not in theorem_stats:
                theorem_stats[theorem] = {"total": 0, "passed": 0, "failed": 0}
            
            theorem_stats[theorem]["total"] += 1
            if verification.is_valid:
                theorem_stats[theorem]["passed"] += 1
            else:
                theorem_stats[theorem]["failed"] += 1
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "theorem_breakdown": theorem_stats,
            "z3_available": Z3_AVAILABLE
        }
    
    def clear_log(self) -> None:
        """Clear verification log."""
        self.verification_log.clear()
    
    def export_log(self, filepath: str) -> None:
        """
        Export verification log to file.
        
        Args:
            filepath: Path to export file
        """
        import json
        
        log_data = []
        for verification in self.verification_log:
            log_data.append({
                "timestamp": datetime.now().isoformat(),
                "theorem": verification.theorem,
                "is_valid": verification.is_valid,
                "reasoning": verification.reasoning,
                "error_details": verification.error_details
            })
        
        with open(filepath, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        logger.info(f"Verification log exported to {filepath}")


# Global Z3 verifier instance
_z3_verifier: Optional[Z3Verifier] = None


def get_z3_verifier() -> Z3Verifier:
    """Get or create the global Z3 verifier instance."""
    global _z3_verifier
    if _z3_verifier is None:
        _z3_verifier = Z3Verifier()
    return _z3_verifier


__all__ = [
    "Z3Verifier",
    "Theorem",
    "get_z3_verifier",
]