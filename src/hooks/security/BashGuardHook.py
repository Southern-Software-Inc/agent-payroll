"""
Bash Guard Hook - Security validation for shell commands
Module ID: APEX-HOOK-SEC-002
Version: 0.1.0

Validates and filters shell commands to prevent:
- Command injection attacks
- Privilege escalation
- File system abuse
- Network access violations
"""

import re
import shlex
from typing import Dict, Any, List, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CommandViolation:
    """Security violation detected in command."""
    violation_type: str
    command: str
    description: str
    severity: str  # "low", "medium", "high", "critical"


class BashGuardHook:
    """
    Security hook for shell command validation.
    
    Filters and blocks dangerous shell commands to prevent
    command injection and system abuse.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize bash guard with configuration."""
        # Blocked commands
        self.blocked_commands = set(config.get("blocked_commands", [
            "rm", "rmdir", "mv", "cp", "chmod", "chown", "chgrp",
            "dd", "fdisk", "mkfs", "mount", "umount", "swapon", "swapoff",
            "reboot", "shutdown", "halt", "poweroff", "init", "systemctl",
            "service", "chkconfig", "update-rc.d", "sysv-rc-conf",
            "passwd", "useradd", "usermod", "userdel", "groupadd", "groupmod",
            "su", "sudo", "doas", "pkexec", "gksudo", "kdesudo",
            "iptables", "ufw", "firewall-cmd", "netfilter",
            "crontab", "at", "batch", "nohup", "screen", "tmux",
            "wget", "curl", "nc", "netcat", "telnet", "ssh", "scp", "rsync",
            "python", "python3", "perl", "ruby", "node", "npm", "pip",
            "gcc", "g++", "make", "cmake", "cargo", "go", "java", "javac",
            "docker", "podman", "kubectl", "helm", "minikube",
            "git", "svn", "hg", "bzr", "cvs"
        ]))
        
        # Dangerous patterns
        self.dangerous_patterns = [
            r"[;&|`$(){}[\]\\]",  # Shell metacharacters
            r"\.\./.*",           # Directory traversal
            r"/etc/",             # System config access
            r"/proc/",            # Process filesystem
            r"/sys/",             # System filesystem
            r"/dev/",             # Device files
            r"/boot/",            # Boot files
            r"/root/",            # Root directory
            r"/var/log/",         # Log files
            r"/var/spool/",       # Spool directories
            r"/tmp/",             # Temp files (if not allowed)
            r"~/.ssh/",           # SSH keys
            r"~/.gnupg/",         # GPG keys
            r"~/.aws/",           # AWS credentials
            r"~/.config/",        # Config files
        ]
        
        # Allowed commands (whitelist)
        self.allowed_commands = set(config.get("allowed_commands", [
            "ls", "pwd", "cd", "echo", "cat", "head", "tail", "grep", "wc",
            "sort", "uniq", "cut", "awk", "sed", "tr", "date", "whoami",
            "id", "uname", "df", "du", "free", "ps", "top", "uptime",
            "which", "whereis", "type", "help", "history", "alias",
            "export", "env", "printenv", "set", "unset", "readonly"
        ]))
        
        # Allowed paths
        self.allowed_paths = config.get("allowed_paths", [
            "/app", "/tmp", "/home", "/workspace"
        ])
        
        # Max command length
        self.max_command_length = config.get("max_command_length", 1000)
        
        # Compile regex patterns
        self.compiled_patterns = [re.compile(pattern) for pattern in self.dangerous_patterns]
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute security validation on shell command.
        
        Args:
            payload: Dictionary containing command to validate
            
        Returns:
            Modified payload with security violations if found
        """
        command = payload.get("command", "")
        
        if not command:
            return payload
        
        try:
            # Basic checks
            if len(command) > self.max_command_length:
                payload["_halt"] = True
                payload["security_violations"] = [{
                    "type": "command_too_long",
                    "command": command[:100] + "...",
                    "description": f"Command too long: {len(command)} characters",
                    "severity": "medium"
                }]
                return payload
            
            # Parse command
            try:
                parts = shlex.split(command)
                if not parts:
                    payload["_halt"] = True
                    payload["security_violations"] = [{
                        "type": "empty_command",
                        "command": command,
                        "description": "Empty command",
                        "severity": "low"
                    }]
                    return payload
                
                base_command = parts[0]
                args = parts[1:]
                
            except ValueError as e:
                payload["_halt"] = True
                payload["security_violations"] = [{
                    "type": "invalid_syntax",
                    "command": command,
                    "description": f"Invalid command syntax: {str(e)}",
                    "severity": "high"
                }]
                return payload
            
            # Check violations
            violations = []
            
            # Check blocked commands
            if base_command in self.blocked_commands:
                violations.append(CommandViolation(
                    violation_type="blocked_command",
                    command=command,
                    description=f"Blocked command: {base_command}",
                    severity="high"
                ))
            
            # Check if command is in whitelist (if whitelist is enabled)
            if self.allowed_commands and base_command not in self.allowed_commands:
                violations.append(CommandViolation(
                    violation_type="unauthorized_command",
                    command=command,
                    description=f"Unauthorized command: {base_command}",
                    severity="medium"
                ))
            
            # Check dangerous patterns
            for pattern in self.compiled_patterns:
                if pattern.search(command):
                    violations.append(CommandViolation(
                        violation_type="dangerous_pattern",
                        command=command,
                        description=f"Dangerous pattern detected: {pattern.pattern}",
                        severity="high"
                    ))
            
            # Check arguments for dangerous content
            for i, arg in enumerate(args):
                # Check for file paths
                if "/" in arg:
                    # Check if path is allowed
                    if not any(arg.startswith(path) for path in self.allowed_paths):
                        violations.append(CommandViolation(
                            violation_type="unauthorized_path",
                            command=command,
                            description=f"Unauthorized path: {arg}",
                            severity="medium"
                        ))
                
                # Check for suspicious arguments
                if any(pattern.search(arg) for pattern in self.compiled_patterns):
                    violations.append(CommandViolation(
                        violation_type="dangerous_argument",
                        command=command,
                        description=f"Dangerous argument: {arg}",
                        severity="high"
                    ))
            
            # Check for command chaining
            if any(char in command for char in [";", "&", "|", "`", "$"]):
                violations.append(CommandViolation(
                    violation_type="command_chaining",
                    command=command,
                    description="Command chaining detected",
                    severity="critical"
                ))
            
            # Check for environment variable manipulation
            if re.search(r'\$\{[^}]*\}', command) or re.search(r'\$[A-Za-z_][A-Za-z0-9_]*', command):
                violations.append(CommandViolation(
                    violation_type="env_variable",
                    command=command,
                    description="Environment variable usage detected",
                    severity="medium"
                ))
            
            # Check for redirection
            if any(op in command for op in [">", ">>", "<", "<<", "2>", "2>>"]):
                violations.append(CommandViolation(
                    violation_type="redirection",
                    command=command,
                    description="I/O redirection detected",
                    severity="medium"
                ))
            
            # If violations found, halt execution
            if violations:
                payload["_halt"] = True
                payload["security_violations"] = [
                    {
                        "type": v.violation_type,
                        "command": v.command,
                        "description": v.description,
                        "severity": v.severity
                    }
                    for v in violations
                ]
                
                # Log violations
                for v in violations:
                    logger.warning(f"Command violation: {v.violation_type} - {v.description}")
        
        except Exception as e:
            payload["_halt"] = True
            payload["security_violations"] = [{
                "type": "validation_error",
                "command": command,
                "description": f"Validation error: {str(e)}",
                "severity": "high"
            }]
            logger.error(f"Error validating command: {e}")
        
        return payload
    
    def is_command_safe(self, command: str) -> bool:
        """
        Quick check if a command is safe.
        
        Args:
            command: Command to check
            
        Returns:
            True if command appears safe, False otherwise
        """
        try:
            parts = shlex.split(command)
            if not parts:
                return False
            
            base_command = parts[0]
            
            # Quick checks
            if base_command in self.blocked_commands:
                return False
            
            if self.allowed_commands and base_command not in self.allowed_commands:
                return False
            
            # Check for dangerous patterns
            for pattern in self.compiled_patterns:
                if pattern.search(command):
                    return False
            
            # Check for command chaining
            if any(char in command for char in [";", "&", "|", "`", "$"]):
                return False
            
            return True
            
        except:
            return False


# Factory function for creating the hook
def create_bash_guard_hook(config: Dict[str, Any]) -> BashGuardHook:
    """Create a bash guard hook with the given configuration."""
    return BashGuardHook(config)


__all__ = [
    "BashGuardHook",
    "CommandViolation",
    "create_bash_guard_hook",
]