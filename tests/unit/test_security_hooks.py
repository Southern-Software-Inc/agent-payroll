"""
Unit Tests for Security Hooks
Module ID: APEX-TEST-SECURITY-001
Version: 0.1.0
"""

import pytest
import ast
from src.hooks.security.ASTScannerHook import ASTScannerHook, SecurityViolation
from src.hooks.security.BashGuardHook import BashGuardHook, CommandViolation


@pytest.mark.unit
class TestASTScannerHook:
    """Test cases for ASTScannerHook."""
    
    @pytest.fixture
    def hook_config(self):
        """Default hook configuration."""
        return {
            "blocked_imports": ["os", "sys", "subprocess"],
            "blocked_calls": ["exec", "eval", "open"],
            "blocked_dunder_methods": ["__import__", "__builtins__"],
            "suspicious_patterns": ["base64", "obfuscate"],
            "max_line_length": 1000,
            "max_ast_nodes": 10000
        }
    
    @pytest.fixture
    def ast_hook(self, hook_config):
        """Create AST scanner hook instance."""
        return ASTScannerHook(hook_config)
    
    async def test_safe_code_passes(self, ast_hook):
        """Test that safe code passes validation."""
        safe_code = """
def add_numbers(a, b):
    return a + b

result = add_numbers(1, 2)
print(result)
"""
        payload = {"code": safe_code}
        result = await ast_hook.execute(payload)
        
        assert "_halt" not in result
        assert "security_violations" not in result
    
    async def test_blocked_import_detected(self, ast_hook):
        """Test detection of blocked imports."""
        malicious_code = """
import os
os.system("ls")
"""
        payload = {"code": malicious_code}
        result = await ast_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert len(violations) == 1
        assert violations[0]["type"] == "blocked_import"
        assert "os" in violations[0]["description"]
        assert violations[0]["severity"] == "high"
    
    async def test_blocked_call_detected(self, ast_hook):
        """Test detection of blocked function calls."""
        malicious_code = """
result = eval("1 + 1")
"""
        payload = {"code": malicious_code}
        result = await ast_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert len(violations) == 1
        assert violations[0]["type"] == "blocked_call"
        assert "eval" in violations[0]["description"]
    
    async def test_blocked_dunder_method_detected(self, ast_hook):
        """Test detection of blocked dunder method access."""
        malicious_code = """
builtins = __import__("builtins")
"""
        payload = {"code": malicious_code}
        result = await ast_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert len(violations) >= 1
        assert any(v["type"] == "blocked_dunder" for v in violations)
    
    async def test_suspicious_pattern_detected(self, ast_hook):
        """Test detection of suspicious patterns."""
        suspicious_code = """
def encode_data(data):
    import base64
    return base64.b64encode(data.encode())
"""
        payload = {"code": suspicious_code}
        result = await ast_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert any(v["type"] == "suspicious_pattern" for v in violations)
        assert any("base64" in v["description"] for v in violations)
    
    async def test_code_too_large(self, ast_hook):
        """Test rejection of overly large code."""
        large_code = "x" * 50001  # Exceeds 50KB limit
        payload = {"code": large_code}
        result = await ast_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert violations[0]["type"] == "code_too_large"
        assert violations[0]["severity"] == "high"
    
    async def test_line_too_long(self, ast_hook):
        """Test rejection of code with overly long lines."""
        long_line_code = "x" * 1001  # Exceeds default limit
        payload = {"code": long_line_code}
        result = await ast_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert violations[0]["type"] == "line_too_long"
        assert violations[0]["severity"] == "medium"
    
    async def test_syntax_error_handling(self, ast_hook):
        """Test handling of syntax errors."""
        invalid_code = """
def broken_function(
    # Missing closing parenthesis
"""
        payload = {"code": invalid_code}
        result = await ast_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert violations[0]["type"] == "syntax_error"
        assert violations[0]["severity"] == "high"
    
    async def test_empty_code(self, ast_hook):
        """Test handling of empty code."""
        payload = {"code": ""}
        result = await ast_hook.execute(payload)
        
        assert "_halt" not in result
        assert "security_violations" not in result
    
    async def test_multiple_violations(self, ast_hook):
        """Test detection of multiple violations."""
        malicious_code = """
import os
import sys
result = eval("os.system('ls')")
"""
        payload = {"code": malicious_code}
        result = await ast_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert len(violations) >= 2  # At least 2 blocked imports
    
    async def test_suspicious_function_name(self, ast_hook):
        """Test detection of suspicious function names."""
        suspicious_code = """
def obfuscate_data(data):
    return data
"""
        payload = {"code": suspicious_code}
        result = await ast_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert any(v["type"] == "suspicious_function" for v in violations)
    
    async def test_suspicious_class_name(self, ast_hook):
        """Test detection of suspicious class names."""
        suspicious_code = """
class Obfuscator:
    def __init__(self):
        pass
"""
        payload = {"code": suspicious_code}
        result = await ast_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert any(v["type"] == "suspicious_class" for v in violations)


@pytest.mark.unit
class TestBashGuardHook:
    """Test cases for BashGuardHook."""
    
    @pytest.fixture
    def bash_config(self):
        """Default bash guard configuration."""
        return {
            "blocked_commands": ["rm", "sudo", "chmod", "passwd"],
            "allowed_commands": ["ls", "pwd", "echo", "cat"],
            "allowed_paths": ["/tmp", "/app"],
            "max_command_length": 1000
        }
    
    @pytest.fixture
    def bash_hook(self, bash_config):
        """Create bash guard hook instance."""
        return BashGuardHook(bash_config)
    
    async def test_safe_command_passes(self, bash_hook):
        """Test that safe commands pass validation."""
        safe_command = "ls -la /tmp"
        payload = {"command": safe_command}
        result = await bash_hook.execute(payload)
        
        assert "_halt" not in result
        assert "security_violations" not in result
    
    async def test_blocked_command_detected(self, bash_hook):
        """Test detection of blocked commands."""
        malicious_command = "rm -rf /"
        payload = {"command": malicious_command}
        result = await bash_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert len(violations) == 1
        assert violations[0]["type"] == "blocked_command"
        assert "rm" in violations[0]["description"]
        assert violations[0]["severity"] == "high"
    
    async def test_unauthorized_command_detected(self, bash_hook):
        """Test detection of unauthorized commands."""
        unauthorized_command = "git status"
        payload = {"command": unauthorized_command}
        result = await bash_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert violations[0]["type"] == "unauthorized_command"
        assert "git" in violations[0]["description"]
    
    async def test_command_chaining_detected(self, bash_hook):
        """Test detection of command chaining."""
        chained_command = "ls; rm -rf /"
        payload = {"command": chained_command}
        result = await bash_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert any(v["type"] == "command_chaining" for v in violations)
        assert violations[0]["severity"] == "critical"
    
    async def test_unauthorized_path_detected(self, bash_hook):
        """Test detection of unauthorized paths."""
        unauthorized_path_command = "cat /etc/passwd"
        payload = {"command": unauthorized_path_command}
        result = await bash_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert any(v["type"] == "unauthorized_path" for v in violations)
    
    async def test_authorized_path_passes(self, bash_hook):
        """Test that authorized paths pass validation."""
        authorized_command = "cat /tmp/test.txt"
        payload = {"command": authorized_command}
        result = await bash_hook.execute(payload)
        
        assert "_halt" not in result
        assert "security_violations" not in result
    
    async def test_command_too_long(self, bash_hook):
        """Test rejection of overly long commands."""
        long_command = "echo " + "x" * 1001
        payload = {"command": long_command}
        result = await bash_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert violations[0]["type"] == "command_too_long"
    
    async def test_empty_command(self, bash_hook):
        """Test handling of empty command."""
        payload = {"command": ""}
        result = await bash_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert violations[0]["type"] == "empty_command"
    
    async def test_invalid_syntax(self, bash_hook):
        """Test handling of invalid command syntax."""
        invalid_command = "'unclosed quote"
        payload = {"command": invalid_command}
        result = await bash_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert violations[0]["type"] == "invalid_syntax"
    
    async def test_environment_variable_usage(self, bash_hook):
        """Test detection of environment variable usage."""
        env_command = "echo $HOME"
        payload = {"command": env_command}
        result = await bash_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert any(v["type"] == "env_variable" for v in violations)
    
    async def test_redirection_detected(self, bash_hook):
        """Test detection of I/O redirection."""
        redirect_command = "ls > /tmp/listing.txt"
        payload = {"command": redirect_command}
        result = await bash_hook.execute(payload)
        
        assert result["_halt"] is True
        assert "security_violations" in result
        
        violations = result["security_violations"]
        assert any(v["type"] == "redirection" for v in violations)
    
    def test_is_command_safe_safe(self, bash_hook):
        """Test is_command_safe with safe command."""
        assert bash_hook.is_command_safe("ls -la") is True
        assert bash_hook.is_command_safe("echo hello") is True
        assert bash_hook.is_command_safe("cat /tmp/file") is True
    
    def test_is_command_safe_unsafe(self, bash_hook):
        """Test is_command_safe with unsafe command."""
        assert bash_hook.is_command_safe("rm -rf /") is False
        assert bash_hook.is_command_safe("ls; rm -rf /") is False
        assert bash_hook.is_command_safe("echo $HOME") is False
        assert bash_hook.is_command_safe("cat /etc/passwd") is False
    
    def test_is_command_safe_invalid(self, bash_hook):
        """Test is_command_safe with invalid command."""
        assert bash_hook.is_command_safe("'unclosed") is False
        assert bash_hook.is_command_safe("") is False


@pytest.mark.unit
class TestSecurityViolation:
    """Test cases for SecurityViolation dataclass."""
    
    def test_security_violation_creation(self):
        """Test security violation creation."""
        violation = SecurityViolation(
            violation_type="blocked_import",
            line_number=10,
            description="Import of blocked module: os",
            severity="high"
        )
        
        assert violation.violation_type == "blocked_import"
        assert violation.line_number == 10
        assert violation.description == "Import of blocked module: os"
        assert violation.severity == "high"


@pytest.mark.unit
class TestCommandViolation:
    """Test cases for CommandViolation dataclass."""
    
    def test_command_violation_creation(self):
        """Test command violation creation."""
        violation = CommandViolation(
            violation_type="blocked_command",
            command="rm -rf /",
            description="Blocked command: rm",
            severity="critical"
        )
        
        assert violation.violation_type == "blocked_command"
        assert violation.command == "rm -rf /"
        assert violation.description == "Blocked command: rm"
        assert violation.severity == "critical"