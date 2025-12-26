"""
Metrics Collection Module
Module ID: APEX-MON-METRICS-001
Version: 0.1.0

Provides comprehensive metrics collection for the APEX Agent Payroll System.
"""

import time
import threading
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import logging

logger = logging.getLogger(__name__)


class MetricsType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricValue:
    """Represents a metric value with metadata."""
    name: str
    value: Union[int, float]
    metric_type: MetricsType
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    help_text: str = ""


@dataclass
class HistogramBucket:
    """Represents a histogram bucket."""
    upper_bound: float
    count: int


class MetricsCollector:
    """
    Comprehensive metrics collector for the APEX system.
    
    Supports counters, gauges, histograms, and timers with labels.
    Thread-safe for concurrent operations.
    """
    
    def __init__(self, max_history: int = 1000):
        """Initialize the metrics collector."""
        self.max_history = max_history
        self._lock = threading.RLock()
        
        # Metric storage
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        
        # Metric metadata
        self._metric_help: Dict[str, str] = {}
        self._metric_types: Dict[str, MetricsType] = {}
        
        # Aggregated metrics
        self._aggregated_metrics: Dict[str, MetricValue] = {}
        
        logger.info("MetricsCollector initialized")
    
    def counter(self, name: str, value: float = 1, labels: Dict[str, str] = None, help_text: str = "") -> None:
        """
        Increment a counter metric.
        
        Args:
            name: Metric name
            value: Value to increment by (default: 1)
            labels: Optional labels
            help_text: Optional help text
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] += value
            self._metric_types[key] = MetricsType.COUNTER
            if help_text:
                self._metric_help[key] = help_text
            
            logger.debug(f"Counter incremented: {key} += {value}")
    
    def gauge(self, name: str, value: float, labels: Dict[str, str] = None, help_text: str = "") -> None:
        """
        Set a gauge metric value.
        
        Args:
            name: Metric name
            value: Gauge value
            labels: Optional labels
            help_text: Optional help text
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value
            self._metric_types[key] = MetricsType.GAUGE
            if help_text:
                self._metric_help[key] = help_text
            
            logger.debug(f"Gauge set: {key} = {value}")
    
    def histogram(self, name: str, value: float, labels: Dict[str, str] = None, help_text: str = "") -> None:
        """
        Record a value in a histogram.
        
        Args:
            name: Metric name
            value: Value to record
            labels: Optional labels
            help_text: Optional help text
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._histograms[key].append(value)
            self._metric_types[key] = MetricsType.HISTOGRAM
            if help_text:
                self._metric_help[key] = help_text
            
            logger.debug(f"Histogram recorded: {key} = {value}")
    
    def timer(self, name: str, duration: float, labels: Dict[str, str] = None, help_text: str = "") -> None:
        """
        Record a timer duration.
        
        Args:
            name: Metric name
            duration: Duration in seconds
            labels: Optional labels
            help_text: Optional help text
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._timers[key].append(duration)
            self._metric_types[key] = MetricsType.TIMER
            if help_text:
                self._metric_help[key] = help_text
            
            logger.debug(f"Timer recorded: {key} = {duration}s")
    
    def context_timer(self, name: str, labels: Dict[str, str] = None, help_text: str = "") -> 'TimerContext':
        """
        Create a timer context manager.
        
        Args:
            name: Metric name
            labels: Optional labels
            help_text: Optional help text
            
        Returns:
            TimerContext manager
        """
        return TimerContext(self, name, labels, help_text)
    
    def get_counter(self, name: str, labels: Dict[str, str] = None) -> Optional[float]:
        """Get counter value."""
        key = self._make_key(name, labels)
        with self._lock:
            return self._counters.get(key)
    
    def get_gauge(self, name: str, labels: Dict[str, str] = None) -> Optional[float]:
        """Get gauge value."""
        key = self._make_key(name, labels)
        with self._lock:
            return self._gauges.get(key)
    
    def get_histogram_stats(self, name: str, labels: Dict[str, str] = None) -> Optional[Dict[str, float]]:
        """Get histogram statistics."""
        key = self._make_key(name, labels)
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            
            sorted_values = sorted(values)
            count = len(values)
            total = sum(values)
            
            return {
                'count': count,
                'sum': total,
                'min': min(values),
                'max': max(values),
                'mean': total / count,
                'p50': sorted_values[int(count * 0.5)],
                'p90': sorted_values[int(count * 0.9)],
                'p95': sorted_values[int(count * 0.95)],
                'p99': sorted_values[int(count * 0.99)],
            }
    
    def get_timer_stats(self, name: str, labels: Dict[str, str] = None) -> Optional[Dict[str, float]]:
        """Get timer statistics."""
        key = self._make_key(name, labels)
        with self._lock:
            durations = list(self._timers.get(key, []))
            if not durations:
                return None
            
            sorted_durations = sorted(durations)
            count = len(durations)
            total = sum(durations)
            
            return {
                'count': count,
                'sum': total,
                'min': min(durations),
                'max': max(durations),
                'mean': total / count,
                'p50': sorted_durations[int(count * 0.5)],
                'p90': sorted_durations[int(count * 0.9)],
                'p95': sorted_durations[int(count * 0.95)],
                'p99': sorted_durations[int(count * 0.99)],
                'rate': count / (max(durations) - min(durations)) if count > 1 else 0,
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics in a structured format."""
        with self._lock:
            metrics = {
                'counters': dict(self._counters),
                'gauges': dict(self._gauges),
                'histograms': {k: self.get_histogram_stats(k.split('{')[0]) 
                             for k in self._histograms.keys()},
                'timers': {k: self.get_timer_stats(k.split('{')[0]) 
                          for k in self._timers.keys()},
                'metadata': {
                    'help': dict(self._metric_help),
                    'types': {k: v.value for k, v in self._metric_types.items()},
                }
            }
            return metrics
    
    def reset_metric(self, name: str, labels: Dict[str, str] = None) -> None:
        """Reset a specific metric."""
        key = self._make_key(name, labels)
        with self._lock:
            self._counters.pop(key, None)
            self._gauges.pop(key, None)
            self._histograms.pop(key, None)
            self._timers.pop(key, None)
            self._metric_help.pop(key, None)
            self._metric_types.pop(key, None)
    
    def reset_all_metrics(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timers.clear()
            self._metric_help.clear()
            self._metric_types.clear()
            self._aggregated_metrics.clear()
        
        logger.info("All metrics reset")
    
    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        with self._lock:
            lines = []
            
            # Export counters
            for key, value in self._counters.items():
                name = key.split('{')[0]
                labels = self._extract_labels(key)
                help_text = self._metric_help.get(key, "")
                
                if help_text:
                    lines.append(f"# HELP {name} {help_text}")
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name}{labels} {value}")
            
            # Export gauges
            for key, value in self._gauges.items():
                name = key.split('{')[0]
                labels = self._extract_labels(key)
                help_text = self._metric_help.get(key, "")
                
                if help_text:
                    lines.append(f"# HELP {name} {help_text}")
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name}{labels} {value}")
            
            # Export histograms
            for key in self._histograms.keys():
                name = key.split('{')[0]
                labels = self._extract_labels(key)
                help_text = self._metric_help.get(key, "")
                stats = self.get_histogram_stats(name)
                
                if stats and help_text:
                    lines.append(f"# HELP {name} {help_text}")
                    lines.append(f"# TYPE {name} histogram")
                    lines.append(f"{name}_count{labels} {stats['count']}")
                    lines.append(f"{name}_sum{labels} {stats['sum']}")
                    lines.append(f"{name}_bucket{{le=\"+Inf\"}}{labels} {stats['count']}")
            
            # Export timers
            for key in self._timers.keys():
                name = key.split('{')[0]
                labels = self._extract_labels(key)
                help_text = self._metric_help.get(key, "")
                stats = self.get_timer_stats(name)
                
                if stats and help_text:
                    lines.append(f"# HELP {name} {help_text}")
                    lines.append(f"# TYPE {name} histogram")
                    lines.append(f"{name}_count{labels} {stats['count']}")
                    lines.append(f"{name}_sum{labels} {stats['sum']}")
                    lines.append(f"{name}_bucket{{le=\"+Inf\"}}{labels} {stats['count']}")
            
            return '\n'.join(lines)
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Create a metric key with labels."""
        if not labels:
            return name
        
        label_str = ','.join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def _extract_labels(self, key: str) -> str:
        """Extract labels from a metric key."""
        if '{' not in key:
            return ''
        return f'{{{key.split("{")[1]}'


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, name: str, labels: Dict[str, str] = None, help_text: str = ""):
        self.collector = collector
        self.name = name
        self.labels = labels or {}
        self.help_text = help_text
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.collector.timer(self.name, duration, self.labels, self.help_text)


# Global metrics collector instance
metrics = MetricsCollector()