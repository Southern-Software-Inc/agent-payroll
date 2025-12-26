"""
AST Scanner Hook - Security validation for Python code
Module ID: APEX-HOOK-SEC-001
Version: 0.1.0

Scans Python AST for security violations including:
- Blocked imports
- Dangerous function calls
- Restricted dunder method access
- Code injection patterns
"""

import ast
from typing import Dict, Any, List, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SecurityViolation:
    """Security violation detected in code."""
    violation_type: str
    line_number: int
    description: str
    severity: str  # "low", "medium", "high", "critical"


class ASTScannerHook:
    """
    Security hook for Python code validation.
    
    Scans Abstract Syntax Tree for potentially dangerous patterns
    and blocks execution if violations are found.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize AST scanner with configuration."""
        self.blocked_imports = set(config.get("blocked_imports", [
            "os", "sys", "subprocess", "socket", "urllib", "requests",
            "pickle", "marshal", "shelve", "dbm", "sqlite3", "psycopg2",
            "smtplib", "telnetlib", "ftplib", "poplib", "imaplib",
            "ctypes", "threading", "multiprocessing", "asyncio"
        ]))
        
        self.blocked_calls = set(config.get("blocked_calls", [
            "exec", "eval", "compile", "__import__", "open", "file",
            "input", "raw_input", "reload", "vars", "globals", "locals",
            "dir", "getattr", "setattr", "delattr", "hasattr",
            "exit", "quit", "help", "copyright", "credits", "license"
        ]))
        
        self.blocked_dunder_methods = set(config.get("blocked_dunder_methods", [
            "__import__", "__builtins__", "__file__", "__name__", "__package__",
            "__doc__", "__annotations__", "__dict__", "__module__", "__qualname__",
            "__code__", "__defaults__", "__closure__", "__globals__", "__kwdefaults__"
        ]))
        
        self.suspicious_patterns = config.get("suspicious_patterns", [
            "base64", "rot13", "caesar", "xor", "encode", "decode",
            "obfuscate", "deobfuscate", "compress", "decompress",
            "encrypt", "decrypt", "hash", "md5", "sha", "crc"
        ])
        
        self.max_line_length = config.get("max_line_length", 1000)
        self.max_ast_nodes = config.get("max_ast_nodes", 10000)
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute security scan on Python code.
        
        Args:
            payload: Dictionary containing code to scan
            
        Returns:
            Modified payload with security violations if found
        """
        code = payload.get("code", "")
        
        if not code:
            return payload
        
        try:
            # Basic checks before parsing
            if len(code) > 50000:  # 50KB limit
                payload["_halt"] = True
                payload["security_violations"] = [{
                    "type": "code_too_large",
                    "line": 0,
                    "description": f"Code too large: {len(code)} bytes",
                    "severity": "high"
                }]
                return payload
            
            # Check line lengths
            for i, line in enumerate(code.split('\n'), 1):
                if len(line) > self.max_line_length:
                    payload["_halt"] = True
                    payload["security_violations"] = [{
                        "type": "line_too_long",
                        "line": i,
                        "description": f"Line too long: {len(line)} characters",
                        "severity": "medium"
                    }]
                    return payload
            
            # Parse AST
            tree = ast.parse(code)
            
            # Check AST complexity
            node_count = len(list(ast.walk(tree)))
            if node_count > self.max_ast_nodes:
                payload["_halt"] = True
                payload["security_violations"] = [{
                    "type": "ast_too_complex",
                    "line": 0,
                    "description": f"AST too complex: {node_count} nodes",
                    "severity": "medium"
                }]
                return payload
            
            # Scan for violations
            violations = self._scan_ast(tree)
            
            if violations:
                payload["_halt"] = True
                payload["security_violations"] = [
                    {
                        "type": v.violation_type,
                        "line": v.line_number,
                        "description": v.description,
                        "severity": v.severity
                    }
                    for v in violations
                ]
                
                # Log violations
                for v in violations:
                    logger.warning(f"Security violation: {v.violation_type} at line {v.line_number}: {v.description}")
        
        except SyntaxError as e:
            payload["_halt"] = True
            payload["security_violations"] = [{
                "type": "syntax_error",
                "line": e.lineno or 0,
                "description": f"Syntax error: {str(e)}",
                "severity": "high"
            }]
            logger.warning(f"Syntax error in code: {e}")
        
        except Exception as e:
            payload["_halt"] = True
            payload["security_violations"] = [{
                "type": "scan_error",
                "line": 0,
                "description": f"Scan error: {str(e)}",
                "severity": "high"
            }]
            logger.error(f"Error scanning code: {e}")
        
        return payload
    
    def _scan_ast(self, tree: ast.AST) -> List[SecurityViolation]:
        """Scan AST for security violations."""
        violations = []
        
        for node in ast.walk(tree):
            # Check for blocked imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.name in self.blocked_imports:
                        violations.append(SecurityViolation(
                            violation_type="blocked_import",
                            line_number=node.lineno,
                            description=f"Import of blocked module: {alias.name}",
                            severity="high"
                        ))
            
            # Check for blocked calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.blocked_calls:
                        violations.append(SecurityViolation(
                            violation_type="blocked_call",
                            line_number=node.lineno,
                            description=f"Call to blocked function: {node.func.id}",
                            severity="high"
                        ))
                
                # Check for method calls on dangerous objects
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        obj_name = node.func.value.id
                        method_name = node.func.attr
                        
                        # Dangerous subprocess calls
                        if obj_name == "subprocess" and method_name in ["run", "call", "Popen", "check_output"]:
                            violations.append(SecurityViolation(
                                violation_type="dangerous_subprocess",
                                line_number=node.lineno,
                                description=f"Dangerous subprocess call: {obj_name}.{method_name}",
                                severity="critical"
                            ))
                        
                        # Dangerous os calls
                        elif obj_name == "os" and method_name in ["system", "popen", "spawn*", "exec*"]:
                            violations.append(SecurityViolation(
                                violation_type="dangerous_os_call",
                                line_number=node.lineno,
                                description=f"Dangerous OS call: {obj_name}.{method_name}",
                                severity="critical"
                            ))
            
            # Check for dunder method access
            elif isinstance(node, ast.Attribute):
                if node.attr in self.blocked_dunder_methods:
                    violations.append(SecurityViolation(
                        violation_type="blocked_dunder",
                        line_number=node.lineno,
                        description=f"Access to blocked dunder method: {node.attr}",
                        severity="high"
                    ))
            
            # Check for string literals with suspicious content
            elif isinstance(node, ast.Str):
                for pattern in self.suspicious_patterns:
                    if pattern.lower() in node.s.lower():
                        violations.append(SecurityViolation(
                            violation_type="suspicious_pattern",
                            line_number=node.lineno,
                            description=f"Suspicious pattern detected: {pattern}",
                            severity="medium"
                        ))
            
            # Check for function definitions with suspicious names
            elif isinstance(node, ast.FunctionDef):
                if any(pattern in node.name.lower() for pattern in self.suspicious_patterns):
                    violations.append(SecurityViolation(
                        violation_type="suspicious_function",
                        line_number=node.lineno,
                        description=f"Suspicious function name: {node.name}",
                        severity="medium"
                    ))
            
            # Check for class definitions with suspicious names
            elif isinstance(node, ast.ClassDef):
                if any(pattern in node.name.lower() for pattern in self.suspicious_patterns):
                    violations.append(SecurityViolation(
                        violation_type="suspicious_class",
                        line_number=node.lineno,
                        description=f"Suspicious class name: {node.name}",
                        severity="medium"
                    ))
        
        return violations


# Factory function for creating the hook
def create_ast_scanner_hook(config: Dict[str, Any]) -> ASTScannerHook:
    """Create an AST scanner hook with the given configuration."""
    return ASTScannerHook(config)


__all__ = [
    "ASTScannerHook",
    "SecurityViolation",
    "create_ast_scanner_hook",
]