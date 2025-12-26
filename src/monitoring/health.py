"""
Health Checking Module
Module ID: APEX-MON-HEALTH-001
Version: 0.1.0

Provides comprehensive health checking for the APEX Agent Payroll System.
"""

import asyncio
import time
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None


@dataclass
class SystemHealth:
    """Overall system health status."""
    status: HealthStatus
    checks: List[HealthCheckResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    uptime_seconds: float = 0.0
    version: str = "0.1.0"


class HealthCheck:
    """Base class for health checks."""
    
    def __init__(self, name: str, timeout: float = 5.0, critical: bool = True):
        """
        Initialize health check.
        
        Args:
            name: Check name
            timeout: Timeout in seconds
            critical: Whether this is a critical check
        """
        self.name = name
        self.timeout = timeout
        self.critical = critical
    
    async def check(self) -> HealthCheckResult:
        """
        Perform the health check.
        
        Returns:
            HealthCheckResult with check status
        """
        start_time = time.time()
        
        try:
            # Implement timeout
            result = await asyncio.wait_for(
                self._check_impl(),
                timeout=self.timeout
            )
            result.duration_ms = (time.time() - start_time) * 1000
            return result
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {self.timeout}s",
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                duration_ms=duration_ms,
                error=str(e)
            )
    
    async def _check_impl(self) -> HealthCheckResult:
        """
        Implement the actual health check logic.
        
        Returns:
            HealthCheckResult with check status
        """
        raise NotImplementedError("Subclasses must implement _check_impl")


class DatabaseHealthCheck(HealthCheck):
    """Health check for database connectivity."""
    
    def __init__(self, name: str = "database", connection_func: Callable = None, **kwargs):
        """
        Initialize database health check.
        
        Args:
            name: Check name
            connection_func: Function to test database connection
            **kwargs: Additional arguments for HealthCheck
        """
        super().__init__(name, **kwargs)
        self.connection_func = connection_func
    
    async def _check_impl(self) -> HealthCheckResult:
        """Check database connectivity."""
        if not self.connection_func:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message="No connection function provided"
            )
        
        try:
            # Test database connection
            start_time = time.time()
            await self.connection_func()
            duration = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                details={"query_time_ms": duration}
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                error=str(e)
            )


class RedisHealthCheck(HealthCheck):
    """Health check for Redis connectivity."""
    
    def __init__(self, name: str = "redis", redis_client=None, **kwargs):
        """
        Initialize Redis health check.
        
        Args:
            name: Check name
            redis_client: Redis client instance
            **kwargs: Additional arguments for HealthCheck
        """
        super().__init__(name, **kwargs)
        self.redis_client = redis_client
    
    async def _check_impl(self) -> HealthCheckResult:
        """Check Redis connectivity."""
        if not self.redis_client:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message="No Redis client provided"
            )
        
        try:
            # Test Redis connection
            start_time = time.time()
            await self.redis_client.ping()
            duration = (time.time() - start_time) * 1000
            
            # Get Redis info
            info = await self.redis_client.info()
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                details={
                    "ping_time_ms": duration,
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory_human", "unknown")
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
                error=str(e)
            )


class VectorStoreHealthCheck(HealthCheck):
    """Health check for vector store connectivity."""
    
    def __init__(self, name: str = "vector_store", vector_store=None, **kwargs):
        """
        Initialize vector store health check.
        
        Args:
            name: Check name
            vector_store: Vector store instance
            **kwargs: Additional arguments for HealthCheck
        """
        super().__init__(name, **kwargs)
        self.vector_store = vector_store
    
    async def _check_impl(self) -> HealthCheckResult:
        """Check vector store connectivity."""
        if not self.vector_store:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message="No vector store provided"
            )
        
        try:
            # Test vector store connection
            start_time = time.time()
            
            # Try a simple query
            test_embedding = [0.1] * 1536  # Typical OpenAI embedding size
            results = await self.vector_store.search(
                query_vector=test_embedding,
                limit=1
            )
            
            duration = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Vector store connection successful",
                details={
                    "query_time_ms": duration,
                    "result_count": len(results) if results else 0
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Vector store connection failed: {str(e)}",
                error=str(e)
            )


class MemoryHealthCheck(HealthCheck):
    """Health check for system memory usage."""
    
    def __init__(self, name: str = "memory", threshold_percent: float = 90.0, **kwargs):
        """
        Initialize memory health check.
        
        Args:
            name: Check name
            threshold_percent: Memory usage threshold percentage
            **kwargs: Additional arguments for HealthCheck
        """
        super().__init__(name, **kwargs)
        self.threshold_percent = threshold_percent
    
    async def _check_impl(self) -> HealthCheckResult:
        """Check system memory usage."""
        try:
            import psutil
            
            # Get memory info
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            # Determine status
            if usage_percent >= self.threshold_percent:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critical: {usage_percent:.1f}%"
            elif usage_percent >= self.threshold_percent * 0.8:
                status = HealthStatus.DEGRADED
                message = f"Memory usage high: {usage_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {usage_percent:.1f}%"
            
            return HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                details={
                    "usage_percent": usage_percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3),
                    "threshold_percent": self.threshold_percent
                }
            )
        except ImportError:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message="psutil not available for memory monitoring"
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
                error=str(e)
            )


class DiskHealthCheck(HealthCheck):
    """Health check for disk space usage."""
    
    def __init__(self, name: str = "disk", path: str = "/", threshold_percent: float = 90.0, **kwargs):
        """
        Initialize disk health check.
        
        Args:
            name: Check name
            path: Path to check
            threshold_percent: Disk usage threshold percentage
            **kwargs: Additional arguments for HealthCheck
        """
        super().__init__(name, **kwargs)
        self.path = path
        self.threshold_percent = threshold_percent
    
    async def _check_impl(self) -> HealthCheckResult:
        """Check disk space usage."""
        try:
            import psutil
            
            # Get disk info
            disk = psutil.disk_usage(self.path)
            usage_percent = (disk.used / disk.total) * 100
            
            # Determine status
            if usage_percent >= self.threshold_percent:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage critical: {usage_percent:.1f}%"
            elif usage_percent >= self.threshold_percent * 0.8:
                status = HealthStatus.DEGRADED
                message = f"Disk usage high: {usage_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {usage_percent:.1f}%"
            
            return HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                details={
                    "usage_percent": usage_percent,
                    "free_gb": disk.free / (1024**3),
                    "total_gb": disk.total / (1024**3),
                    "path": self.path,
                    "threshold_percent": self.threshold_percent
                }
            )
        except ImportError:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message="psutil not available for disk monitoring"
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Disk check failed: {str(e)}",
                error=str(e)
            )


class HealthChecker:
    """
    Comprehensive health checker for the APEX system.
    
    Manages multiple health checks and provides overall system health status.
    """
    
    def __init__(self, start_time: float = None):
        """Initialize the health checker."""
        self.start_time = start_time or time.time()
        self._checks: List[HealthCheck] = []
        self._last_check: Optional[SystemHealth] = None
        
        logger.info("HealthChecker initialized")
    
    def add_check(self, check: HealthCheck) -> None:
        """Add a health check."""
        self._checks.append(check)
        logger.info(f"Added health check: {check.name}")
    
    def remove_check(self, name: str) -> bool:
        """Remove a health check by name."""
        for i, check in enumerate(self._checks):
            if check.name == name:
                removed = self._checks.pop(i)
                logger.info(f"Removed health check: {removed.name}")
                return True
        return False
    
    async def check_health(self) -> SystemHealth:
        """
        Perform all health checks and return system health.
        
        Returns:
            SystemHealth with overall status and individual check results
        """
        if not self._checks:
            return SystemHealth(
                status=HealthStatus.UNKNOWN,
                message="No health checks configured"
            )
        
        # Run all checks concurrently
        tasks = [check.check() for check in self._checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        check_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                check_results.append(HealthCheckResult(
                    name=self._checks[i].name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed with exception: {str(result)}",
                    error=str(result)
                ))
            else:
                check_results.append(result)
        
        # Determine overall status
        overall_status = self._determine_overall_status(check_results)
        
        # Calculate uptime
        uptime_seconds = time.time() - self.start_time
        
        system_health = SystemHealth(
            status=overall_status,
            checks=check_results,
            uptime_seconds=uptime_seconds
        )
        
        self._last_check = system_health
        return system_health
    
    def _determine_overall_status(self, results: List[HealthCheckResult]) -> HealthStatus:
        """Determine overall system health from individual check results."""
        if not results:
            return HealthStatus.UNKNOWN
        
        # Check for critical failures
        for result in results:
            check = next((c for c in self._checks if c.name == result.name), None)
            if check and check.critical and result.status == HealthStatus.UNHEALTHY:
                return HealthStatus.UNHEALTHY
        
        # Check for any unhealthy
        if any(r.status == HealthStatus.UNHEALTHY for r in results):
            return HealthStatus.DEGRADED
        
        # Check for any degraded
        if any(r.status == HealthStatus.DEGRADED for r in results):
            return HealthStatus.DEGRADED
        
        # Check for any unknown
        if any(r.status == HealthStatus.UNKNOWN for r in results):
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def get_last_check(self) -> Optional[SystemHealth]:
        """Get the last health check result."""
        return self._last_check
    
    async def run_continuous_checks(self, interval: float = 30.0) -> None:
        """
        Run health checks continuously.
        
        Args:
            interval: Check interval in seconds
        """
        while True:
            try:
                health = await self.check_health()
                logger.info(f"Health check completed: {health.status.value}")
                
                # Sleep until next check
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Continuous health check failed: {str(e)}")
                await asyncio.sleep(interval)


# Global health checker instance
health_checker = HealthChecker()