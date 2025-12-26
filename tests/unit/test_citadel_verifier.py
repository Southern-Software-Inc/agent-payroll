"""
Unit Tests for Citadel Z3 Verifier
Module ID: APEX-TEST-CITADEL-001
Version: 0.1.0
"""

import pytest
from unittest.mock import Mock, patch
from src.citadel.verifier import Z3Verifier, Theorem
from src.citadel import VerificationResult


@pytest.mark.unit
class TestZ3Verifier:
    """Test cases for Z3Verifier class."""
    
    def test_init(self):
        """Test Z3Verifier initialization."""
        verifier = Z3Verifier()
        
        assert verifier.verification_log == []
        assert verifier.theorems is not None
        assert "conservation" in verifier.theorems
        assert "solvency" in verifier.theorems
        assert "debt_ceiling" in verifier.theorems
        assert "non_negative" in verifier.theorems
    
    def test_define_theorems(self):
        """Test theorem definitions."""
        verifier = Z3Verifier()
        theorems = verifier.theorems
        
        # Check conservation theorem
        conservation = theorems["conservation"]
        assert isinstance(conservation, Theorem)
        assert conservation.name == "Conservation of Wealth"
        assert "bank_pre" in conservation.variables
        assert "agent_pre" in conservation.variables
        assert conservation.goal == "bank_pre + agent_pre == bank_post + agent_post"
        
        # Check solvency theorem
        solvency = theorems["solvency"]
        assert solvency.name == "Solvency Constraint"
        assert solvency.goal == "balance >= transaction_amount"
    
    @patch('src.citadel.verifier.Z3_AVAILABLE', True)
    def test_verify_theorem_conservation_valid(self, mock_z3_verifier):
        """Test conservation theorem verification with valid values."""
        verifier = Z3Verifier()
        
        # Mock Z3 solver
        mock_solver = Mock()
        mock_solver.check.return_value = "unsat"  # Theorem holds
        verifier.solver = mock_solver
        
        result = verifier.verify_theorem(
            "conservation",
            bank_pre=1000.0,
            agent_pre=100.0,
            reward=50.0,
            tax=5.0,
            bank_post=955.0,
            agent_post=150.0
        )
        
        assert result.is_valid is True
        assert result.theorem == "Conservation of Wealth"
        assert result.error_details == ""
    
    @patch('src.citadel.verifier.Z3_AVAILABLE', True)
    def test_verify_theorem_conservation_invalid(self, mock_z3_verifier):
        """Test conservation theorem verification with invalid values."""
        verifier = Z3Verifier()
        
        # Mock Z3 solver
        mock_solver = Mock()
        mock_solver.check.return_value = "sat"  # Theorem fails
        verifier.solver = mock_solver
        
        result = verifier.verify_theorem(
            "conservation",
            bank_pre=1000.0,
            agent_pre=100.0,
            reward=50.0,
            tax=5.0,
            bank_post=900.0,  # Wrong - should be 955
            agent_post=150.0
        )
        
        assert result.is_valid is False
        assert result.theorem == "Conservation of Wealth"
        assert "violation" in result.error_details.lower()
    
    @patch('src.citadel.verifier.Z3_AVAILABLE', False)
    def test_verify_theorem_stub_mode(self):
        """Test theorem verification in stub mode."""
        verifier = Z3Verifier()
        
        # Test conservation theorem
        result = verifier.verify_theorem(
            "conservation",
            bank_pre=1000.0,
            agent_pre=100.0,
            reward=50.0,
            tax=5.0,
            bank_post=955.0,
            agent_post=150.0
        )
        
        assert result.is_valid is True
        assert result.theorem == "Conservation of Wealth"
        
        # Test with invalid values
        result = verifier.verify_theorem(
            "conservation",
            bank_pre=1000.0,
            agent_pre=100.0,
            reward=50.0,
            tax=5.0,
            bank_post=900.0,
            agent_post=150.0
        )
        
        assert result.is_valid is False
        assert "mismatch" in result.error_details.lower()
    
    def test_verify_theorem_solvency_valid(self):
        """Test solvency theorem verification with valid values."""
        verifier = Z3Verifier()
        
        result = verifier.verify_theorem(
            "solvency",
            balance=100.0,
            transaction_amount=50.0
        )
        
        assert result.is_valid is True
        assert result.theorem == "Solvency Constraint"
    
    def test_verify_theorem_solvency_invalid(self):
        """Test solvency theorem verification with invalid values."""
        verifier = Z3Verifier()
        
        result = verifier.verify_theorem(
            "solvency",
            balance=100.0,
            transaction_amount=150.0
        )
        
        assert result.is_valid is False
        assert result.theorem == "Solvency Constraint"
        assert "insufficient" in result.error_details.lower()
    
    def test_verify_theorem_debt_ceiling_valid(self):
        """Test debt ceiling theorem verification with valid values."""
        verifier = Z3Verifier()
        
        result = verifier.verify_theorem(
            "debt_ceiling",
            balance=100.0,
            debt_ceiling=-1000.0
        )
        
        assert result.is_valid is True
        assert result.theorem == "Debt Ceiling Constraint"
    
    def test_verify_theorem_debt_ceiling_invalid(self):
        """Test debt ceiling theorem verification with invalid values."""
        verifier = Z3Verifier()
        
        result = verifier.verify_theorem(
            "debt_ceiling",
            balance=-1100.0,
            debt_ceiling=-1000.0
        )
        
        assert result.is_valid is False
        assert result.theorem == "Debt Ceiling Constraint"
        assert "exceeded" in result.error_details.lower()
    
    def test_verify_theorem_non_negative_valid(self):
        """Test non-negative theorem verification with valid values."""
        verifier = Z3Verifier()
        
        result = verifier.verify_theorem(
            "non_negative",
            balance=100.0
        )
        
        assert result.is_valid is True
        assert result.theorem == "Non-Negative Balance"
    
    def test_verify_theorem_non_negative_invalid(self):
        """Test non-negative theorem verification with invalid values."""
        verifier = Z3Verifier()
        
        result = verifier.verify_theorem(
            "non_negative",
            balance=-100.0
        )
        
        assert result.is_valid is False
        assert result.theorem == "Non-Negative Balance"
        assert "negative" in result.error_details.lower()
    
    def test_verify_theorem_unknown(self):
        """Test verification of unknown theorem."""
        verifier = Z3Verifier()
        
        result = verifier.verify_theorem(
            "unknown_theorem",
            balance=100.0
        )
        
        assert result.is_valid is False
        assert "Unknown theorem" in result.error_details
    
    def test_verify_transaction_batch(self):
        """Test batch transaction verification."""
        verifier = Z3Verifier()
        
        transactions = [
            {
                "bank_pre": 1000.0,
                "agent_pre": 100.0,
                "reward": 50.0,
                "tax": 5.0,
                "bank_post": 955.0,
                "agent_post": 150.0,
                "balance": 100.0,
                "amount": 50.0,
                "debt_ceiling": -1000.0
            },
            {
                "bank_pre": 955.0,
                "agent_pre": 150.0,
                "reward": 25.0,
                "tax": 2.5,
                "bank_post": 932.5,
                "agent_post": 175.0,
                "balance": 150.0,
                "amount": 25.0,
                "debt_ceiling": -1000.0
            }
        ]
        
        results = verifier.verify_transaction_batch(transactions)
        
        # Should have 6 results per transaction (conservation, solvency, debt_ceiling)
        assert len(results) == 6
        
        # All should be valid
        assert all(r.is_valid for r in results)
    
    def test_get_verification_summary_empty(self):
        """Test verification summary with empty log."""
        verifier = Z3Verifier()
        
        summary = verifier.get_verification_summary()
        
        assert summary["total"] == 0
        assert summary["passed"] == 0
        assert summary["failed"] == 0
        assert summary["pass_rate"] == 0.0
        assert "theorem_breakdown" in summary
    
    def test_get_verification_summary_with_data(self):
        """Test verification summary with data."""
        verifier = Z3Verifier()
        
        # Add some mock verifications
        verifier.verification_log = [
            VerificationResult(True, "conservation", "Valid", ""),
            VerificationResult(True, "solvency", "Valid", ""),
            VerificationResult(False, "debt_ceiling", "Invalid", "Exceeded"),
        ]
        
        summary = verifier.get_verification_summary()
        
        assert summary["total"] == 3
        assert summary["passed"] == 2
        assert summary["failed"] == 1
        assert summary["pass_rate"] == 66.66666666666666
        
        # Check theorem breakdown
        breakdown = summary["theorem_breakdown"]
        assert "conservation" in breakdown
        assert "solvency" in breakdown
        assert "debt_ceiling" in breakdown
        assert breakdown["conservation"]["total"] == 1
        assert breakdown["conservation"]["passed"] == 1
        assert breakdown["debt_ceiling"]["failed"] == 1
    
    def test_clear_log(self):
        """Test clearing verification log."""
        verifier = Z3Verifier()
        
        # Add some data
        verifier.verification_log = [VerificationResult(True, "test", "test", "")]
        
        # Clear log
        verifier.clear_log()
        
        assert verifier.verification_log == []
    
    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_export_log(self, mock_json_dump, mock_open):
        """Test exporting verification log."""
        verifier = Z3Verifier()
        
        # Add some data
        verifier.verification_log = [
            VerificationResult(True, "conservation", "Valid", "")
        ]
        
        # Export log
        verifier.export_log("test_log.json")
        
        # Verify file was opened and json.dump was called
        mock_open.assert_called_once_with("test_log.json", 'w')
        mock_json_dump.assert_called_once()
        
        # Check the exported data structure
        call_args = mock_json_dump.call_args[0]
        exported_data = call_args[0]
        
        assert len(exported_data) == 1
        assert exported_data[0]["theorem"] == "conservation"
        assert exported_data[0]["is_valid"] is True
        assert "timestamp" in exported_data[0]


@pytest.mark.unit
class TestTheorem:
    """Test cases for Theorem dataclass."""
    
    def test_theorem_creation(self):
        """Test theorem creation."""
        theorem = Theorem(
            name="Test Theorem",
            variables=["x", "y"],
            constraints=["x > 0", "y > 0"],
            goal="x + y > 0",
            description="Test theorem description"
        )
        
        assert theorem.name == "Test Theorem"
        assert theorem.variables == ["x", "y"]
        assert theorem.constraints == ["x > 0", "y > 0"]
        assert theorem.goal == "x + y > 0"
        assert theorem.description == "Test theorem description"


@pytest.mark.unit
class TestVerificationResult:
    """Test cases for VerificationResult dataclass."""
    
    def test_verification_result_creation(self):
        """Test verification result creation."""
        result = VerificationResult(
            is_valid=True,
            theorem="Test Theorem",
            reasoning="Test reasoning",
            error_details=""
        )
        
        assert result.is_valid is True
        assert result.theorem == "Test Theorem"
        assert result.reasoning == "Test reasoning"
        assert result.error_details == ""
    
    def test_verification_result_with_error(self):
        """Test verification result with error."""
        result = VerificationResult(
            is_valid=False,
            theorem="Test Theorem",
            reasoning="Test reasoning",
            error_details="Test error"
        )
        
        assert result.is_valid is False
        assert result.error_details == "Test error"