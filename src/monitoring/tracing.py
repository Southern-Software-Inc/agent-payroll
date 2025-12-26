"""
Distributed Tracing Module
Module ID: APEX-MON-TRACING-001
Version: 0.1.0

Provides distributed tracing capabilities for the APEX Agent Payroll System.
"""

import time
import uuid
from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Generator, AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class SpanKind(Enum):
    """Span kinds for different types of operations."""
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"
    INTERNAL = "internal"


class SpanStatus:
    """Span status with code and description."""
    
    def __init__(self, code: int, description: str = ""):
        self.code = code
        self.description = description
    
    @classmethod
    def OK(cls) -> 'SpanStatus':
        """Create OK status."""
        return cls(0, "OK")
    
    @classmethod
    def ERROR(cls, description: str = "Error") -> 'SpanStatus':
        """Create ERROR status."""
        return cls(1, description)


@dataclass
class SpanEvent:
    """Event within a span."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    name: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Link to another span."""
    trace_id: str
    span_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)


class Span:
    """
    Represents a span in a distributed trace.
    
    A span represents a single operation within a trace.
    """
    
    def __init__(
        self,
        name: str,
        trace_id: str = None,
        span_id: str = None,
        parent_span_id: str = None,
        kind: SpanKind = SpanKind.INTERNAL,
        start_time: datetime = None
    ):
        """
        Initialize a span.
        
        Args:
            name: Span name
            trace_id: Trace ID (generated if not provided)
            span_id: Span ID (generated if not provided)
            parent_span_id: Parent span ID
            kind: Span kind
            start_time: Start time (now if not provided)
        """
        self.name = name
        self.trace_id = trace_id or str(uuid.uuid4())
        self.span_id = span_id or str(uuid.uuid4())
        self.parent_span_id = parent_span_id
        self.kind = kind
        self.start_time = start_time or datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.status: Optional[SpanStatus] = None
        self.attributes: Dict[str, Any] = {}
        self.events: List[SpanEvent] = []
        self.links: List[SpanLink] = []
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the span."""
        self.attributes[key] = value
    
    def set_attributes(self, attributes: Dict[str, Any]) -> None:
        """Set multiple attributes on the span."""
        self.attributes.update(attributes)
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None) -> None:
        """Add an event to the span."""
        event = SpanEvent(name=name, attributes=attributes or {})
        self.events.append(event)
    
    def add_link(self, trace_id: str, span_id: str, attributes: Dict[str, Any] = None) -> None:
        """Add a link to another span."""
        link = SpanLink(trace_id=trace_id, span_id=span_id, attributes=attributes or {})
        self.links.append(link)
    
    def set_status(self, status: SpanStatus) -> None:
        """Set the span status."""
        self.status = status
    
    def end(self, end_time: datetime = None) -> None:
        """End the span."""
        self.end_time = end_time or datetime.utcnow()
        if self.status is None:
            self.status = SpanStatus.OK()
    
    def duration(self) -> Optional[float]:
        """Get span duration in seconds."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary representation."""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "kind": self.kind.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration(),
            "status": {
                "code": self.status.code,
                "description": self.status.description
            } if self.status else None,
            "attributes": self.attributes,
            "events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "name": event.name,
                    "attributes": event.attributes
                }
                for event in self.events
            ],
            "links": [
                {
                    "trace_id": link.trace_id,
                    "span_id": link.span_id,
                    "attributes": link.attributes
                }
                for link in self.links
            ]
        }


class Tracer:
    """
    Tracer for creating and managing spans.
    
    Provides context management for span lifecycle.
    """
    
    def __init__(self, name: str):
        """
        Initialize tracer.
        
        Args:
            name: Tracer name (usually component name)
        """
        self.name = name
        self._active_span: Optional[Span] = None
    
    def start_span(
        self,
        name: str,
        parent: Span = None,
        kind: SpanKind = SpanKind.INTERNAL
    ) -> Span:
        """
        Start a new span.
        
        Args:
            name: Span name
            parent: Parent span (if None, uses current active span)
            kind: Span kind
            
        Returns:
            New span
        """
        # Determine parent
        if parent is None:
            parent = self._active_span
        
        # Create span
        span = Span(
            name=name,
            trace_id=parent.trace_id if parent else None,
            parent_span_id=parent.span_id if parent else None,
            kind=kind
        )
        
        # Set component attribute
        span.set_attribute("component", self.name)
        
        return span
    
    @contextmanager
    def span(
        self,
        name: str,
        parent: Span = None,
        kind: SpanKind = SpanKind.INTERNAL
    ) -> Generator[Span, None, None]:
        """
        Context manager for creating a span.
        
        Args:
            name: Span name
            parent: Parent span
            kind: Span kind
            
        Yields:
            Active span
        """
        span = self.start_span(name, parent, kind)
        previous_active = self._active_span
        self._active_span = span
        
        try:
            yield span
            span.set_status(SpanStatus.OK())
        except Exception as e:
            span.set_status(SpanStatus.ERROR(str(e)))
            raise
        finally:
            span.end()
            self._active_span = previous_active
    
    @asynccontextmanager
    async def async_span(
        self,
        name: str,
        parent: Span = None,
        kind: SpanKind = SpanKind.INTERNAL
    ) -> AsyncGenerator[Span, None]:
        """
        Async context manager for creating a span.
        
        Args:
            name: Span name
            parent: Parent span
            kind: Span kind
            
        Yields:
            Active span
        """
        span = self.start_span(name, parent, kind)
        previous_active = self._active_span
        self._active_span = span
        
        try:
            yield span
            span.set_status(SpanStatus.OK())
        except Exception as e:
            span.set_status(SpanStatus.ERROR(str(e)))
            raise
        finally:
            span.end()
            self._active_span = previous_active
    
    def get_active_span(self) -> Optional[Span]:
        """Get the currently active span."""
        return self._active_span


class TracingManager:
    """
    Manages distributed tracing across the APEX system.
    
    Provides global tracing context and span collection.
    """
    
    def __init__(self):
        """Initialize the tracing manager."""
        self._tracers: Dict[str, Tracer] = {}
        self._spans: List[Span] = []
        self._max_spans = 10000  # Maximum spans to keep in memory
        
        logger.info("TracingManager initialized")
    
    def get_tracer(self, name: str) -> Tracer:
        """
        Get or create a tracer.
        
        Args:
            name: Tracer name
            
        Returns:
            Tracer instance
        """
        if name not in self._tracers:
            self._tracers[name] = Tracer(name)
        return self._tracers[name]
    
    def add_span(self, span: Span) -> None:
        """
        Add a span to the collection.
        
        Args:
            span: Span to add
        """
        self._spans.append(span)
        
        # Limit span collection size
        if len(self._spans) > self._max_spans:
            self._spans = self._spans[-self._max_spans:]
    
    def get_spans(
        self,
        trace_id: str = None,
        span_id: str = None,
        limit: int = 100
    ) -> List[Span]:
        """
        Get spans with optional filtering.
        
        Args:
            trace_id: Filter by trace ID
            span_id: Filter by span ID
            limit: Maximum number of spans to return
            
        Returns:
            List of spans
        """
        spans = self._spans
        
        # Apply filters
        if trace_id:
            spans = [span for span in spans if span.trace_id == trace_id]
        
        if span_id:
            spans = [span for span in spans if span.span_id == span_id]
        
        # Sort by start time (newest first)
        spans.sort(key=lambda s: s.start_time, reverse=True)
        
        return spans[:limit]
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """
        Get all spans in a trace.
        
        Args:
            trace_id: Trace ID
            
        Returns:
            List of spans in the trace
        """
        spans = [span for span in self._spans if span.trace_id == trace_id]
        
        # Sort by start time
        spans.sort(key=lambda s: s.start_time)
        
        return spans
    
    def clear_spans(self) -> None:
        """Clear all collected spans."""
        self._spans.clear()
        logger.info("Cleared all spans")
    
    def export_spans(self, format: str = "json") -> str:
        """
        Export spans in specified format.
        
        Args:
            format: Export format ("json" or "zipkin")
            
        Returns:
            Exported spans as string
        """
        if format == "json":
            import json
            return json.dumps([span.to_dict() for span in self._spans], indent=2)
        elif format == "zipkin":
            # Convert to Zipkin format
            zipkin_spans = []
            for span in self._spans:
                zipkin_span = {
                    "traceId": span.trace_id.replace("-", ""),
                    "id": span.span_id.replace("-", ""),
                    "name": span.name,
                    "timestamp": int(span.start_time.timestamp() * 1000000),  # microseconds
                    "duration": int(span.duration() * 1000000) if span.duration() else None,
                    "localEndpoint": {"serviceName": span.attributes.get("component", "unknown")},
                    "tags": {k: str(v) for k, v in span.attributes.items()},
                    "annotations": [
                        {
                            "timestamp": int(event.timestamp.timestamp() * 1000000),
                            "value": event.name
                        }
                        for event in span.events
                    ]
                }
                
                if span.parent_span_id:
                    zipkin_span["parentId"] = span.parent_span_id.replace("-", "")
                
                zipkin_spans.append(zipkin_span)
            
            import json
            return json.dumps(zipkin_spans, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global tracing manager instance
tracing_manager = TracingManager()


def get_tracer(name: str) -> Tracer:
    """Get a tracer from the global tracing manager."""
    return tracing_manager.get_tracer(name)


def trace_function(name: str = None):
    """
    Decorator for tracing function execution.
    
    Args:
        name: Span name (function name if not provided)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer(func.__module__)
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            with tracer.span(span_name) as span:
                # Add function arguments as attributes (excluding sensitive data)
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                span.set_attribute("function.args_count", len(args))
                span.set_attribute("function.kwargs_count", len(kwargs))
                
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def trace_async_function(name: str = None):
    """
    Decorator for tracing async function execution.
    
    Args:
        name: Span name (function name if not provided)
        
    Returns:
        Decorated async function
    """
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = get_tracer(func.__module__)
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            async with tracer.async_span(span_name) as span:
                # Add function arguments as attributes (excluding sensitive data)
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                span.set_attribute("function.args_count", len(args))
                span.set_attribute("function.kwargs_count", len(kwargs))
                
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator