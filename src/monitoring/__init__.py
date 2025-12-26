"""
Monitoring and Observability Module
Module ID: APEX-MON-001
Version: 0.1.0

Provides comprehensive monitoring, metrics collection, and observability
for the APEX Agent Payroll System.
"""

# Import components with lazy loading to avoid circular dependencies
def _lazy_import(module_name, item_name):
    """Lazy import helper to avoid circular dependencies."""
    def _import():
        module = __import__(module_name, fromlist=[item_name])
        return getattr(module, item_name)
    return _import

# Lazy imports
MetricsCollector = _lazy_import('.metrics', 'MetricsCollector')
MetricsType = _lazy_import('.metrics', 'MetricsType')
StructuredLogger = _lazy_import('.logging', 'StructuredLogger')
TracingManager = _lazy_import('.tracing', 'TracingManager')
HealthChecker = _lazy_import('.health', 'HealthChecker')
HealthStatus = _lazy_import('.health', 'HealthStatus')
AlertManager = _lazy_import('.alerts', 'AlertManager')
AlertSeverity = _lazy_import('.alerts', 'AlertSeverity')

__all__ = [
    'MetricsCollector',
    'MetricsType',
    'StructuredLogger',
    'TracingManager',
    'HealthChecker',
    'HealthStatus',
    'AlertManager',
    'AlertSeverity',
]