"""
Configuration Management System
Module ID: APEX-CONFIG-001
Version: 0.1.0

Centralized configuration management with environment-specific settings,
validation, and secret management.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Supported deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: Optional[str] = None
    host: str = "localhost"
    port: int = 5432
    database: str = "apex"
    username: str = "apex"
    password: Optional[str] = None
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class RedisConfig:
    """Redis configuration."""
    url: str = "redis://localhost:6379"
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 100


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""
    backend: str = "chromadb"
    embedding_model: str = "text-embedding-3-small"
    dimension: int = 1536
    distance_metric: str = "cosine"
    
    # ChromaDB settings
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    
    # Pinecone settings
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index: str = "apex-memory"
    
    # Weaviate settings
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: Optional[str] = None
    
    # Qdrant settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None


@dataclass
class LLMConfig:
    """LLM API configuration."""
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Default model settings
    default_provider: str = "anthropic"
    default_model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 4096
    temperature: float = 0.7
    
    # Rate limiting
    requests_per_minute: int = 60
    tokens_per_minute: int = 40000


@dataclass
class SecurityConfig:
    """Security configuration."""
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    jwt_refresh_expiry_days: int = 7
    
    # Encryption
    encryption_key: Optional[str] = None
    encryption_algorithm: str = "AES-256-GCM"
    
    # Access control
    enable_rbac: bool = True
    session_timeout_minutes: int = 30
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst_size: int = 20


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    metrics_enabled: bool = True
    metrics_port: int = 8001
    tracing_enabled: bool = False
    tracing_endpoint: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: Optional[str] = None
    
    # Health checks
    health_check_interval_seconds: int = 30
    
    # Performance
    enable_profiling: bool = False
    profile_output_dir: Optional[str] = None


@dataclass
class StorageConfig:
    """Storage configuration."""
    backend: str = "local"
    
    # Local storage
    local_data_dir: str = "./data"
    local_temp_dir: str = "./temp"
    
    # S3 storage
    s3_bucket: Optional[str] = None
    s3_region: str = "us-east-1"
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_endpoint_url: Optional[str] = None


@dataclass
class PerformanceConfig:
    """Performance tuning configuration."""
    max_workers: int = 4
    request_timeout_seconds: int = 60
    connection_timeout_seconds: int = 30
    read_timeout_seconds: int = 30
    
    # Caching
    cache_ttl_seconds: int = 300
    cache_max_size: int = 1000
    
    # Memory management
    memory_limit_mb: int = 2048
    gc_threshold: float = 0.8


class Settings:
    """
    Centralized configuration management.
    
    Loads configuration from environment variables,
    configuration files, and provides validation.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize settings."""
        self.environment = Environment(os.getenv("APEX_ENV", "development"))
        self.debug = os.getenv("APEX_DEBUG", "false").lower() == "true"
        
        # Load configuration
        self._load_from_file(config_file)
        self._load_from_env()
        
        # Initialize configuration objects
        self.database = DatabaseConfig(**self._get_section("database"))
        self.redis = RedisConfig(**self._get_section("redis"))
        self.vector_store = VectorStoreConfig(**self._get_section("vector_store"))
        self.llm = LLMConfig(**self._get_section("llm"))
        self.security = SecurityConfig(**self._get_section("security"))
        self.monitoring = MonitoringConfig(**self._get_section("monitoring"))
        self.storage = StorageConfig(**self._get_section("storage"))
        self.performance = PerformanceConfig(**self._get_section("performance"))
        
        # Validate configuration
        self._validate()
    
    def _load_from_file(self, config_file: Optional[str] = None) -> None:
        """Load configuration from file."""
        self._config_data = {}
        
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                self._config_data = json.load(f)
        else:
            # Try default locations
            default_paths = [
                "config.json",
                "config/config.json",
                "/app/config/config.json",
                f"config.{self.environment.value}.json",
                f"config/config.{self.environment.value}.json",
            ]
            
            for path in default_paths:
                if Path(path).exists():
                    with open(path, 'r') as f:
                        self._config_data = json.load(f)
                    break
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            # Database
            "DATABASE_URL": ["database", "url"],
            "DB_HOST": ["database", "host"],
            "DB_PORT": ["database", "port"],
            "DB_NAME": ["database", "database"],
            "DB_USER": ["database", "username"],
            "DB_PASSWORD": ["database", "password"],
            
            # Redis
            "REDIS_URL": ["redis", "url"],
            "REDIS_HOST": ["redis", "host"],
            "REDIS_PORT": ["redis", "port"],
            "REDIS_PASSWORD": ["redis", "password"],
            
            # Vector Store
            "VECTOR_STORE_BACKEND": ["vector_store", "backend"],
            "PINECONE_API_KEY": ["vector_store", "pinecone_api_key"],
            "PINECONE_ENVIRONMENT": ["vector_store", "pinecone_environment"],
            "WEAVIATE_URL": ["vector_store", "weaviate_url"],
            "WEAVIATE_API_KEY": ["vector_store", "weaviate_api_key"],
            "QDRANT_HOST": ["vector_store", "qdrant_host"],
            "QDRANT_PORT": ["vector_store", "qdrant_port"],
            "QDRANT_API_KEY": ["vector_store", "qdrant_api_key"],
            
            # LLM
            "ANTHROPIC_API_KEY": ["llm", "anthropic_api_key"],
            "OPENAI_API_KEY": ["llm", "openai_api_key"],
            "GOOGLE_API_KEY": ["llm", "google_api_key"],
            
            # Security
            "JWT_SECRET": ["security", "jwt_secret"],
            "ENCRYPTION_KEY": ["security", "encryption_key"],
            
            # Storage
            "STORAGE_BACKEND": ["storage", "backend"],
            "S3_BUCKET": ["storage", "s3_bucket"],
            "S3_REGION": ["storage", "s3_region"],
            "S3_ACCESS_KEY": ["storage", "s3_access_key"],
            "S3_SECRET_KEY": ["storage", "s3_secret_key"],
            
            # Monitoring
            "LOG_LEVEL": ["monitoring", "log_level"],
            "METRICS_ENABLED": ["monitoring", "metrics_enabled"],
            "TRACING_ENABLED": ["monitoring", "tracing_enabled"],
            "TRACING_ENDPOINT": ["monitoring", "tracing_endpoint"],
            
            # Performance
            "MAX_WORKERS": ["performance", "max_workers"],
            "REQUEST_TIMEOUT": ["performance", "request_timeout_seconds"],
        }
        
        for env_var, path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Type conversion
                if env_var.endswith("_PORT") or env_var in ["DB_PORT", "REDIS_PORT", "QDRANT_PORT"]:
                    value = int(value)
                elif env_var.endswith("_ENABLED") or env_var in ["METRICS_ENABLED", "TRACING_ENABLED"]:
                    value = value.lower() == "true"
                elif env_var in ["MAX_WORKERS", "REQUEST_TIMEOUT"]:
                    value = int(value)
                
                # Set nested value
                self._set_nested_value(path, value)
    
    def _get_section(self, section: str) -> Dict[str, Any]:
        """Get configuration section."""
        return self._config_data.get(section, {})
    
    def _set_nested_value(self, path: List[str], value: Any) -> None:
        """Set nested configuration value."""
        current = self._config_data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def _validate(self) -> None:
        """Validate configuration."""
        errors = []
        
        # Required settings
        if not self.security.jwt_secret and self.environment == Environment.PRODUCTION:
            errors.append("JWT_SECRET is required in production")
        
        if not self.llm.anthropic_api_key and not self.llm.openai_api_key:
            errors.append("At least one LLM API key is required")
        
        # Environment-specific validation
        if self.environment == Environment.PRODUCTION:
            if self.debug:
                errors.append("Debug mode should not be enabled in production")
            
            if self.monitoring.log_level == "DEBUG":
                errors.append("DEBUG log level not recommended for production")
            
            if not self.security.encryption_key:
                errors.append("Encryption key is required in production")
        
        # Database validation
        if not self.database.url and not all([self.database.host, self.database.database]):
            errors.append("Database URL or host/database is required")
        
        # Vector store validation
        if self.vector_store.backend == "pinecone" and not self.vector_store.pinecone_api_key:
            errors.append("Pinecone API key is required for Pinecone backend")
        
        if self.vector_store.backend == "weaviate" and not self.vector_store.weaviate_url:
            errors.append("Weaviate URL is required for Weaviate backend")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)
    
    def get_database_url(self) -> str:
        """Get complete database URL."""
        if self.database.url:
            return self.database.url
        
        return (
            f"postgresql://{self.database.username}:{self.database.password}"
            f"@{self.database.host}:{self.database.port}/{self.database.database}"
        )
    
    def get_redis_url(self) -> str:
        """Get complete Redis URL."""
        if self.redis.url:
            return self.redis.url
        
        auth = f":{self.redis.password}@" if self.redis.password else ""
        return f"redis://{auth}{self.redis.host}:{self.redis.port}/{self.redis.db}"
    
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == Environment.DEVELOPMENT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "environment": self.environment.value,
            "debug": self.debug,
            "database": self.database.__dict__,
            "redis": self.redis.__dict__,
            "vector_store": self.vector_store.__dict__,
            "llm": self.llm.__dict__,
            "security": self.security.__dict__,
            "monitoring": self.monitoring.__dict__,
            "storage": self.storage.__dict__,
            "performance": self.performance.__dict__,
        }


# Global settings instance
_settings: Optional[Settings] = None


def get_settings(config_file: Optional[str] = None) -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings(config_file)
    return _settings


def reload_settings(config_file: Optional[str] = None) -> Settings:
    """Reload settings from configuration."""
    global _settings
    _settings = Settings(config_file)
    return _settings


__all__ = [
    "Settings",
    "Environment",
    "DatabaseConfig",
    "RedisConfig",
    "VectorStoreConfig",
    "LLMConfig",
    "SecurityConfig",
    "MonitoringConfig",
    "StorageConfig",
    "PerformanceConfig",
    "get_settings",
    "reload_settings",
]