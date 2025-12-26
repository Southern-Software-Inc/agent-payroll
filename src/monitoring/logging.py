"""
Structured Logging Module
Module ID: APEX-MON-LOGGING-001
Version: 0.1.0

Provides structured logging with correlation IDs and context tracking
for the APEX Agent Payroll System.
"""

import json
import logging
import time
import uuid
import threading
from typing import Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
from datetime import datetime


class LogLevel(Enum):
    """Log levels with numeric values."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class LogContext:
    """Structured log context with correlation tracking."""
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    agent_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Create base log entry
        log_entry = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': threading.current_thread().name,
            'process': record.process,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add stack trace if present
        if record.stack_info:
            log_entry['stack_trace'] = self.formatStack(record.stack_info)
        
        # Add context if available
        if hasattr(record, 'context'):
            context_dict = asdict(record.context)
            # Only include non-empty fields
            context_dict = {k: v for k, v in context_dict.items() if v is not None and v != {}}
            if context_dict:
                log_entry['context'] = context_dict
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info', 'context'
            }:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class StructuredLogger:
    """
    Structured logger with correlation tracking and context management.
    
    Provides enhanced logging capabilities with automatic correlation ID
    generation and context propagation.
    """
    
    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        """Initialize the structured logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            # Create console handler with structured formatter
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(console_handler)
        
        # Thread-local context storage
        self._context = threading.local()
        
        # Default context
        self._default_context = LogContext()
    
    def set_default_context(self, **kwargs) -> None:
        """Set default context values."""
        for key, value in kwargs.items():
            if hasattr(self._default_context, key):
                setattr(self._default_context, key, value)
    
    def get_context(self) -> LogContext:
        """Get current context (thread-local or default)."""
        if hasattr(self._context, 'value'):
            return self._context.value
        return self._default_context
    
    def set_context(self, context: LogContext) -> None:
        """Set current context (thread-local)."""
        self._context.value = context
    
    def update_context(self, **kwargs) -> None:
        """Update current context with new values."""
        current = self.get_context()
        for key, value in kwargs.items():
            if hasattr(current, key):
                setattr(current, key, value)
        self.set_context(current)
    
    @contextmanager
    def context(self, **kwargs):
        """Context manager for temporary context updates."""
        original_context = self.get_context()
        try:
            self.update_context(**kwargs)
            yield self.get_context()
        finally:
            self.set_context(original_context)
    
    def _log(self, level: LogLevel, message: str, **kwargs) -> None:
        """Internal logging method with context."""
        # Create log record with context
        record = self.logger.makeRecord(
            self.logger.name, level.value, "", 0, message, (), None
        )
        record.context = self.get_context()
        
        # Add extra fields
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        self.logger.handle(record)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        kwargs['exc_info'] = True
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def audit(self, action: str, resource: str, **kwargs) -> None:
        """Log audit event."""
        self.info(
            f"Audit: {action} on {resource}",
            audit_action=action,
            audit_resource=resource,
            **kwargs
        )
    
    def performance(self, operation: str, duration: float, **kwargs) -> None:
        """Log performance metric."""
        self.info(
            f"Performance: {operation} completed in {duration:.3f}s",
            perf_operation=operation,
            perf_duration=duration,
            **kwargs
        )
    
    def security(self, event: str, severity: str = "medium", **kwargs) -> None:
        """Log security event."""
        level = LogLevel.WARNING if severity == "high" else LogLevel.INFO
        self._log(
            level,
            f"Security: {event}",
            security_event=event,
            security_severity=severity,
            **kwargs
        )
    
    def business(self, event: str, **kwargs) -> None:
        """Log business event."""
        self.info(
            f"Business: {event}",
            business_event=event,
            **kwargs
        )
    
    def transaction(self, transaction_id: str, status: str, **kwargs) -> None:
        """Log transaction event."""
        self.info(
            f"Transaction: {transaction_id} - {status}",
            transaction_id=transaction_id,
            transaction_status=status,
            **kwargs
        )


class LoggerManager:
    """Manager for multiple structured loggers."""
    
    def __init__(self):
        """Initialize the logger manager."""
        self._loggers: Dict[str, StructuredLogger] = {}
        self._global_context = LogContext()
    
    def get_logger(self, name: str, level: LogLevel = LogLevel.INFO) -> StructuredLogger:
        """Get or create a structured logger."""
        if name not in self._loggers:
            logger = StructuredLogger(name, level)
            # Set global context as default
            logger.set_default_context(**asdict(self._global_context))
            self._loggers[name] = logger
        return self._loggers[name]
    
    def set_global_context(self, **kwargs) -> None:
        """Set global context for all loggers."""
        for key, value in kwargs.items():
            if hasattr(self._global_context, key):
                setattr(self._global_context, key, value)
        
        # Update all existing loggers
        for logger in self._loggers.values():
            logger.set_default_context(**asdict(self._global_context))
    
    def update_global_context(self, **kwargs) -> None:
        """Update global context for all loggers."""
        self.set_global_context(**kwargs)
    
    def set_level(self, name: str, level: LogLevel) -> None:
        """Set log level for a specific logger."""
        if name in self._loggers:
            self._loggers[name].logger.setLevel(level.value)
    
    def set_all_levels(self, level: LogLevel) -> None:
        """Set log level for all loggers."""
        for logger in self._loggers.values():
            logger.logger.setLevel(level.value)


# Global logger manager instance
logger_manager = LoggerManager()


def get_logger(name: str, level: LogLevel = LogLevel.INFO) -> StructuredLogger:
    """Get a structured logger."""
    return logger_manager.get_logger(name, level)


def set_global_context(**kwargs) -> None:
    """Set global context for all loggers."""
    logger_manager.set_global_context(**kwargs)


def configure_logging(
    level: LogLevel = LogLevel.INFO,
    format_json: bool = True,
    include_console: bool = True,
    file_path: Optional[str] = None
) -> None:
    """Configure global logging settings."""
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level.value)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    if format_json:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Add console handler
    if include_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler
    if file_path:
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)