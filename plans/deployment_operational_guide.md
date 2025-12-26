# APEX Deployment & Operational Guide

## Executive Summary

This guide provides comprehensive instructions for deploying, operating, and maintaining the APEX Agent Payroll System in production environments. It covers infrastructure requirements, deployment strategies, monitoring, security, and operational procedures to ensure reliable, scalable operation of the autonomous agent ecosystem.

## 1. System Requirements

### 1.1 Hardware Requirements

#### Minimum Requirements
- **CPU**: 4 cores (Intel i5 or AMD Ryzen 5)
- **Memory**: 8GB RAM
- **Storage**: 50GB SSD (NVMe preferred)
- **Network**: 100 Mbps connection

#### Recommended Requirements
- **CPU**: 8+ cores (Intel i7/i9 or AMD Ryzen 7/9)
- **Memory**: 16GB+ RAM
- **Storage**: 200GB+ NVMe SSD
- **Network**: 1 Gbps connection
- **GPU**: Optional for local LLM inference

#### Enterprise Requirements
- **CPU**: 16+ cores with AVX-512 support
- **Memory**: 32GB+ ECC RAM
- **Storage**: 500GB+ NVMe SSD with backup
- **Network**: 10 Gbps connection with redundancy
- **GPU**: NVIDIA A100/H100 for inference

### 1.2 Software Requirements

#### Operating System
- **Primary**: Ubuntu 22.04 LTS or later
- **Alternative**: CentOS Stream 9, RHEL 9
- **Development**: macOS 13+, Windows 11 with WSL2

#### Container Runtime
- **Docker**: 24.0+ with BuildKit
- **Docker Compose**: 2.20+
- **Container Runtime**: containerd 1.6+

#### Python Environment
- **Python**: 3.9-3.11
- **Package Manager**: pip 23.0+
- **Virtual Environment**: venv or conda

### 1.3 External Dependencies

#### LLM Providers
- **Anthropic**: Claude API access
- **OpenAI**: GPT API access
- **Google**: Gemini API access
- **Local**: Ollama for local models

#### Storage Backends
- **Vector Database**: ChromaDB, FAISS, or Pinecone
- **Object Storage**: S3-compatible storage
- **Database**: PostgreSQL 14+ (optional)

#### Monitoring Stack
- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack or Loki
- **Tracing**: Jaeger or Tempo

## 2. Deployment Architecture

### 2.1 Deployment Topologies

```mermaid
graph TB
    subgraph "Single Node Deployment"
        subgraph "Server"
            APEX[APEX Core]
            DOCKER[Docker Engine]
            STORAGE[Local Storage]
        end
        end
    
    subgraph "Multi-Node Deployment"
        subgraph "Load Balancer"
            LB[HAProxy/Nginx]
        end
        
        subgraph "Application Nodes"
            APEX1[APEX Node 1]
            APEX2[APEX Node 2]
            APEX3[APEX Node 3]
        end
        
        subgraph "Shared Storage"
            REDIS[Redis Cache]
            POSTGRES[PostgreSQL]
            S3[S3 Storage]
        end
    end
    
    subgraph "Enterprise Deployment"
        subgraph "DMZ"
            LB_EXT[External LB]
            WAF[Web App Firewall]
        end
        
        subgraph "Application Tier"
            APP_LB[Internal LB]
            APEX_CLUSTER[APEX Cluster]
        end
        
        subgraph "Data Tier"
            DB_CLUSTER[Database Cluster]
            VECTOR_CLUSTER[Vector DB Cluster]
            STORAGE_CLUSTER[Storage Cluster]
        end
        
        subgraph "Management"
            MONITOR[Monitoring]
            LOGGING[Centralized Logging]
            BACKUP[Backup System]
        end
    end
```

### 2.2 Container Architecture

```yaml
# docker-compose.yml
version: '3.8'

services:
  apex-core:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: apex-core
    restart: unless-stopped
    environment:
      - APEX_ENV=production
      - LOG_LEVEL=INFO
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://apex:password@postgres:5432/apex
    volumes:
      - ./data:/app/data
      - ./config:/app/config
      - ./logs:/app/logs
    ports:
      - "8080:8080"
    depends_on:
      - redis
      - postgres
    networks:
      - apex-network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  redis:
    image: redis:7-alpine
    container_name: apex-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    networks:
      - apex-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G

  postgres:
    image: postgres:15-alpine
    container_name: apex-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=apex
      - POSTGRES_USER=apex
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    networks:
      - apex-network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G

  chromadb:
    image: chromadb/chroma:latest
    container_name: apex-chromadb
    restart: unless-stopped
    environment:
      - CHROMA_SERVER_HOST=0.0.0.0
      - CHROMA_SERVER_HTTP_PORT=8000
    volumes:
      - chromadb-data:/chroma/chroma
    ports:
      - "8000:8000"
    networks:
      - apex-network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G

  prometheus:
    image: prom/prometheus:latest
    container_name: apex-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - apex-network

  grafana:
    image: grafana/grafana:latest
    container_name: apex-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    networks:
      - apex-network

volumes:
  redis-data:
  postgres-data:
  chromadb-data:
  prometheus-data:
  grafana-data:

networks:
  apex-network:
    driver: bridge
```

## 3. Installation & Setup

### 3.1 Quick Start Installation

```bash
#!/bin/bash
# quick-install.sh

set -e

echo "🚀 Installing APEX Agent Payroll System..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed."; exit 1; }

# Clone repository
if [ ! -d "agent-payroll" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/your-org/agent-payroll.git
    cd agent-payroll
else
    cd agent-payroll
    git pull origin main
fi

# Create environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating environment configuration..."
    cat > .env << EOF
# APEX Configuration
APEX_ENV=production
LOG_LEVEL=INFO

# Database Configuration
POSTGRES_PASSWORD=$(openssl rand -base64 32)
DATABASE_URL=postgresql://apex:\${POSTGRES_PASSWORD}@postgres:5432/apex

# Redis Configuration
REDIS_URL=redis://redis:6379

# LLM API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Grafana Configuration
GRAFANA_PASSWORD=$(openssl rand -base64 32)

# Security
JWT_SECRET=$(openssl rand -base64 64)
EOF
    echo "✅ Environment file created. Please edit .env with your API keys."
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Initialize database
echo "🗄️ Initializing database..."
docker-compose exec apex-core python -m src.scripts.init_database

# Create default agents
echo "🤖 Creating default agents..."
docker-compose exec apex-core python -m src.scripts.create_default_agents

echo "✅ APEX installation complete!"
echo ""
echo "🌐 Access points:"
echo "  - APEX API: http://localhost:8080"
echo "  - Grafana: http://localhost:3000 (admin/grafana_password)"
echo "  - Prometheus: http://localhost:9090"
echo ""
echo "📚 Next steps:"
echo "  1. Edit .env with your LLM API keys"
echo "  2. Restart services: docker-compose restart"
echo "  3. Check documentation: https://docs.apex.ai"
```

### 3.2 Production Deployment

```bash
#!/bin/bash
# production-deploy.sh

set -euo pipefail

# Configuration
DEPLOY_USER="apex"
DEPLOY_PATH="/opt/apex"
BACKUP_PATH="/opt/backups/apex"
SERVICE_NAME="apex"

echo "🚀 Deploying APEX to production..."

# Create deployment user
if ! id "$DEPLOY_USER" &>/dev/null; then
    echo "👤 Creating deployment user..."
    sudo useradd -m -s /bin/bash "$DEPLOY_USER"
    sudo usermod -aG docker "$DEPLOY_USER"
fi

# Create directories
echo "📁 Creating directories..."
sudo mkdir -p "$DEPLOY_PATH" "$BACKUP_PATH"
sudo chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_PATH" "$BACKUP_PATH"

# Deploy as deployment user
sudo -u "$DEPLOY_USER" bash << 'EOF'
cd /opt/apex

# Backup current deployment
if [ -d "current" ]; then
    echo "💾 Backing up current deployment..."
    tar -czf "/opt/backups/apex/backup-$(date +%Y%m%d-%H%M%S).tar.gz" current/
fi

# Clone or update repository
if [ ! -d "repo" ]; then
    git clone https://github.com/your-org/agent-payroll.git repo
else
    cd repo
    git fetch origin
    git checkout main
    git pull origin main
    cd ..
fi

# Build new release
echo "🔨 Building new release..."
cd repo
git checkout $(git describe --tags --abbrev=0)
docker-compose -f docker-compose.prod.yml build
cd ..

# Switch to new release
echo "🔄 Switching to new release..."
ln -sfn repo current
cd current

# Load environment
if [ -f "../.env.prod" ]; then
    cp ../.env.prod .env
fi

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml run --rm apex-core python -m src.scripts.migrate_database

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Health check
echo "🔍 Running health checks..."
sleep 30
docker-compose -f docker-compose.prod.yml ps

# Verify services
if docker-compose -f docker-compose.prod.yml exec -T apex-core python -c "import src.core; print('OK')"; then
    echo "✅ Deployment successful!"
else
    echo "❌ Deployment failed - rolling back..."
    docker-compose -f docker-compose.prod.yml down
    # Rollback logic here
    exit 1
fi
EOF

# Setup systemd service
echo "⚙️ Setting up systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=APEX Agent Payroll System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DEPLOY_PATH/current
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "✅ Production deployment complete!"
```

## 4. Configuration Management

### 4.1 Environment Configuration

```python
# config/settings.py
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Settings:
    """Centralized configuration management"""
    
    def __init__(self):
        self.load_from_env()
        self.load_from_files()
    
    def load_from_env(self):
        """Load configuration from environment variables"""
        # Core settings
        self.env = os.getenv("APEX_ENV", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Database settings
        self.database_url = os.getenv("DATABASE_URL")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # LLM API settings
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Security settings
        self.jwt_secret = os.getenv("JWT_SECRET")
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        
        # Storage settings
        self.storage_backend = os.getenv("STORAGE_BACKEND", "local")
        self.s3_bucket = os.getenv("S3_BUCKET")
        self.s3_region = os.getenv("S3_REGION", "us-east-1")
        
        # Performance settings
        self.max_workers = int(os.getenv("MAX_WORKERS", "4"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "60"))
        
        # Monitoring settings
        self.metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
        self.tracing_enabled = os.getenv("TRACING_ENABLED", "false").lower() == "true"
    
    def load_from_files(self):
        """Load configuration from files"""
        config_dir = Path("/app/config")
        
        # Load JSON configuration files
        for config_file in config_dir.glob("*.json"):
            config_name = config_file.stem
            with open(config_file) as f:
                setattr(self, config_name, json.load(f))
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        if self.database_url:
            return {"url": self.database_url}
        
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "apex"),
            "username": os.getenv("DB_USER", "apex"),
            "password": os.getenv("DB_PASSWORD"),
        }
    
    def get_vector_store_config(self) -> Dict[str, Any]:
        """Get vector store configuration"""
        backend = os.getenv("VECTOR_STORE_BACKEND", "chromadb")
        
        if backend == "chromadb":
            return {
                "backend": "chromadb",
                "host": os.getenv("CHROMADB_HOST", "localhost"),
                "port": int(os.getenv("CHROMADB_PORT", "8000")),
            }
        elif backend == "pinecone":
            return {
                "backend": "pinecone",
                "api_key": os.getenv("PINECONE_API_KEY"),
                "environment": os.getenv("PINECONE_ENVIRONMENT"),
            }
        else:
            return {"backend": "faiss"}
    
    def validate(self) -> List[str]:
        """Validate configuration"""
        errors = []
        
        # Required settings
        if not self.jwt_secret:
            errors.append("JWT_SECRET is required")
        
        if not self.anthropic_api_key and not self.openai_api_key:
            errors.append("At least one LLM API key is required")
        
        # Environment-specific validation
        if self.env == "production":
            if self.debug:
                errors.append("Debug mode should not be enabled in production")
            
            if self.log_level == "DEBUG":
                errors.append("DEBUG log level not recommended for production")
        
        return errors

# Global settings instance
settings = Settings()
```

### 4.2 Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash apex

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/temp && \
    chown -R apex:apex /app

# Switch to app user
USER apex

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Start command
CMD ["python", "-m", "src.main"]
```

```dockerfile
# Dockerfile.prod (Production optimized)
FROM python:3.11-slim as builder

# Build stage
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user
RUN useradd --create-home --shell /bin/bash apex

# Copy Python packages from builder
COPY --from=builder /root/.local /home/apex/.local

# Set work directory
WORKDIR /app

# Copy application code
COPY --chown=apex:apex . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/temp && \
    chown -R apex:apex /app

# Switch to app user
USER apex

# Add Python user bin to PATH
ENV PATH=/home/apex/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Start command with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "60", "src.main:app"]
```

## 5. Monitoring & Observability

### 5.1 Metrics Collection

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import functools

# Define metrics
REQUEST_COUNT = Counter(
    'apex_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'apex_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_AGENTS = Gauge(
    'apex_active_agents',
    'Number of active agents'
)

TRANSACTION_VOLUME = Gauge(
    'apex_transaction_volume_apx',
    'Total APX transaction volume'
)

LEDGER_SIZE = Gauge(
    'apex_ledger_size_bytes',
    'Size of ledger in bytes'
)

def track_requests(func):
    """Decorator to track request metrics"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            REQUEST_COUNT.labels(
                method=kwargs.get('method', 'unknown'),
                endpoint=kwargs.get('endpoint', 'unknown'),
                status='success'
            ).inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(
                method=kwargs.get('method', 'unknown'),
                endpoint=kwargs.get('endpoint', 'unknown'),
                status='error'
            ).inc()
            raise
        finally:
            REQUEST_DURATION.labels(
                method=kwargs.get('method', 'unknown'),
                endpoint=kwargs.get('endpoint', 'unknown')
            ).observe(time.time() - start_time)
    
    return wrapper

class MetricsCollector:
    """Collect system metrics"""
    
    def __init__(self):
        self.mce = get_mce()
        self.vector_store = get_vector_store()
    
    async def collect_metrics(self):
        """Collect all metrics"""
        # Agent metrics
        ledger = self.mce.get_ledger_snapshot()
        ACTIVE_AGENTS.set(len(ledger['agents']))
        
        # Economic metrics
        total_volume = sum(
            tx['amount'] for tx in ledger['transaction_log']
        )
        TRANSACTION_VOLUME.set(total_volume)
        
        # Storage metrics
        ledger_size = os.path.getsize(settings.ledger_file)
        LEDGER_SIZE.set(ledger_size)
    
    def start_metrics_server(self, port=8001):
        """Start Prometheus metrics server"""
        start_http_server(port)
```

### 5.2 Logging Configuration

```python
# logging_config.py
import logging
import logging.config
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'exc_info', 
                          'exc_text', 'stack_info', 'lineno', 'funcName', 
                          'created', 'msecs', 'relativeCreated', 'thread', 
                          'threadName', 'processName', 'process', 'message']:
                log_entry[key] = value
        
        return json.dumps(log_entry)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': JSONFormatter,
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'json' if settings.env == 'production' else 'detailed',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'json',
            'filename': '/app/logs/apex.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'json',
            'filename': '/app/logs/apex-error.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': settings.log_level,
            'propagate': False,
        },
        'apex': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'uvicorn': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

def setup_logging():
    """Setup logging configuration"""
    logging.config.dictConfig(LOGGING_CONFIG)
```

### 5.3 Health Checks

```python
# health.py
from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import asyncio
import time

app = FastAPI()

class HealthChecker:
    """Health check system"""
    
    def __init__(self):
        self.checks = {}
        self.last_check = {}
    
    def register_check(self, name: str, check_func):
        """Register a health check"""
        self.checks[name] = check_func
    
    async def run_check(self, name: str) -> Dict[str, Any]:
        """Run a specific health check"""
        start_time = time.time()
        
        try:
            result = await self.checks[name]()
            duration = time.time() - start_time
            
            return {
                'status': 'healthy',
                'duration': duration,
                'details': result
            }
        except Exception as e:
            duration = time.time() - start_time
            
            return {
                'status': 'unhealthy',
                'duration': duration,
                'error': str(e)
            }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_healthy = True
        
        for name in self.checks:
            result = await self.run_check(name)
            results[name] = result
            
            if result['status'] != 'healthy':
                overall_healthy = False
        
        return {
            'status': 'healthy' if overall_healthy else 'unhealthy',
            'checks': results,
            'timestamp': time.time()
        }

# Initialize health checker
health_checker = HealthChecker()

# Register health checks
@health_checker.register_check('database')
async def check_database():
    """Check database connectivity"""
    mce = get_mce()
    snapshot = mce.get_ledger_snapshot()
    return {'connected': True, 'agents_count': len(snapshot['agents'])}

@health_checker.register_check('redis')
async def check_redis():
    """Check Redis connectivity"""
    import redis
    client = redis.from_url(settings.redis_url)
    client.ping()
    return {'connected': True}

@health_checker.register_check('vector_store')
async def check_vector_store():
    """Check vector store connectivity"""
    vector_store = get_vector_store()
    # Simple search test
    results = await vector_store.search([0.0] * 1536, top_k=1)
    return {'connected': True, 'index_size': len(vector_store.index.nodes)}

@health_checker.register_check('llm_apis')
async def check_llm_apis():
    """Check LLM API connectivity"""
    apis = {}
    
    if settings.anthropic_api_key:
        try:
            # Test Anthropic API
            apis['anthropic'] = {'connected': True}
        except Exception as e:
            apis['anthropic'] = {'connected': False, 'error': str(e)}
    
    if settings.openai_api_key:
        try:
            # Test OpenAI API
            apis['openai'] = {'connected': True}
        except Exception as e:
            apis['openai'] = {'connected': False, 'error': str(e)}
    
    return apis

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return await health_checker.run_all_checks()

@app.get("/health/{check_name}")
async def specific_health_check(check_name: str):
    """Specific health check endpoint"""
    if check_name not in health_checker.checks:
        raise HTTPException(status_code=404, detail="Health check not found")
    
    return await health_checker.run_check(check_name)

@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    health = await health_checker.run_all_checks()
    
    if health['status'] == 'healthy':
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")
```

## 6. Security Configuration

### 6.1 Container Security

```yaml
# docker-compose.security.yml
version: '3.8'

services:
  apex-core:
    build:
      context: .
      dockerfile: Dockerfile.prod
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
      - /app/temp:noexec,nosuid,size=500m
    volumes:
      - ./data:/app/data:rw
      - ./logs:/app/logs:rw
    user: "1000:1000"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    environment:
      - APEX_ENV=production
    networks:
      - apex-secure
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

networks:
  apex-secure:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 6.2 Network Security

```bash
#!/bin/bash
# security-setup.sh

# Create network namespace
ip netns add apex-secure

# Create veth pair
ip link add veth0 type veth peer name veth1

# Move one end to namespace
ip link set veth1 netns apex-secure

# Configure interfaces
ip addr add 192.168.100.1/24 dev veth0
ip link set veth0 up

ip netns exec apex-secure ip addr add 192.168.100.2/24 dev veth1
ip netns exec apex-secure ip link set veth1 up
ip netns exec apex-secure ip link set lo up

# Add routing
ip netns exec apex-secure ip route add default via 192.168.100.1

# Configure firewall
iptables -A INPUT -s 192.168.100.0/24 -j ACCEPT
iptables -A OUTPUT -d 192.168.100.0/24 -j ACCEPT

# Block external access from container
iptables -A OUTPUT -m owner --uid-owner 1000 -j DROP
```

## 7. Backup & Recovery

### 7.1 Backup Strategy

```python
# backup.py
import asyncio
import tarfile
import shutil
from datetime import datetime
from pathlib import Path

class BackupManager:
    """Manage system backups"""
    
    def __init__(self):
        self.backup_dir = Path("/opt/backups/apex")
        self.data_dir = Path("/app/data")
        self.config_dir = Path("/app/config")
        
    async def create_full_backup(self):
        """Create full system backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"full_backup_{timestamp}.tar.gz"
        
        # Create backup
        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(self.data_dir, arcname="data")
            tar.add(self.config_dir, arcname="config")
            
            # Add database dump
            db_dump = await self._create_database_dump()
            tar.add(db_dump, arcname="database.sql")
            
            # Add vector store backup
            vector_backup = await self._create_vector_store_backup()
            tar.add(vector_backup, arcname="vector_store")
        
        # Verify backup
        if await self._verify_backup(backup_file):
            await self._cleanup_old_backups()
            return backup_file
        else:
            backup_file.unlink()
            raise Exception("Backup verification failed")
    
    async def _create_database_dump(self):
        """Create database dump"""
        dump_file = self.backup_dir / "database.sql"
        
        # Use pg_dump for PostgreSQL
        cmd = [
            "pg_dump",
            settings.database_url,
            "--no-owner",
            "--no-privileges",
            "--file", str(dump_file)
        ]
        
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()
        
        if process.returncode != 0:
            raise Exception("Database dump failed")
        
        return dump_file
    
    async def restore_from_backup(self, backup_file):
        """Restore system from backup"""
        # Extract backup
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall("/tmp/restore")
        
        # Stop services
        await self._stop_services()
        
        try:
            # Restore data
            if Path("/tmp/restore/data").exists():
                shutil.rmtree(self.data_dir)
                shutil.move("/tmp/restore/data", self.data_dir)
            
            # Restore database
            if Path("/tmp/restore/database.sql").exists():
                await self._restore_database("/tmp/restore/database.sql")
            
            # Restore vector store
            if Path("/tmp/restore/vector_store").exists():
                await self._restore_vector_store("/tmp/restore/vector_store")
            
            # Start services
            await self._start_services()
            
        finally:
            # Cleanup
            shutil.rmtree("/tmp/restore", ignore_errors=True)
    
    async def _cleanup_old_backups(self, keep_days=30):
        """Clean up old backups"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        for backup_file in self.backup_dir.glob("*.tar.gz"):
            file_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            if file_date < cutoff_date:
                backup_file.unlink()
```

## 8. Performance Tuning

### 8.1 System Optimization

```bash
#!/bin/bash
# performance-tuning.sh

# System limits
echo "apex soft nofile 65536" >> /etc/security/limits.conf
echo "apex hard nofile 65536" >> /etc/security/limits.conf

# Kernel parameters
cat >> /etc/sysctl.conf << EOF
# Network optimization
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728

# Memory optimization
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# File system optimization
fs.file-max = 2097152
EOF

sysctl -p

# Docker optimization
cat > /etc/docker/daemon.json << EOF
{
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  }
}
EOF

systemctl restart docker
```

### 8.2 Application Optimization

```python
# performance.py
import asyncio
import uvloop
from concurrent.futures import ThreadPoolExecutor

# Use uvloop for better performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class PerformanceOptimizer:
    """Optimize application performance"""
    
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
    
    async def optimize_database_queries(self):
        """Optimize database queries"""
        # Connection pooling
        engine = create_engine(
            settings.database_url,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Query optimization
        Session = sessionmaker(bind=engine)
        
        async def execute_query(query, params=None):
            with Session() as session:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    session.execute,
                    query,
                    params or {}
                )
                return result.fetchall()
        
        return execute_query
    
    def optimize_vector_search(self):
        """Optimize vector search performance"""
        # HNSW parameters tuning
        hnsw_config = {
            'M': 32,  # More connections for better recall
            'ef_construction': 400,  # Higher for better index quality
            'ef_search': 200,  # Higher for better search quality
        }
        
        return hnsw_config
    
    async def implement_caching(self):
        """Implement caching strategy"""
        import redis
        
        redis_client = redis.from_url(settings.redis_url)
        
        async def cached_call(key, func, ttl=300):
            # Check cache
            cached_result = await redis_client.get(key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function
            result = await func()
            
            # Cache result
            await redis_client.setex(key, ttl, json.dumps(result))
            
            return result
        
        return cached_call
```

## 9. Troubleshooting Guide

### 9.1 Common Issues

#### Issue: High Memory Usage
```bash
# Diagnose memory usage
docker stats apex-core
python -m memory_profiler src/main.py

# Solutions:
# 1. Reduce batch sizes
# 2. Implement streaming for large data
# 3. Add memory limits to containers
# 4. Optimize data structures
```

#### Issue: Slow Response Times
```bash
# Diagnose performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080/health

# Profile application
python -m cProfile -o profile.stats src/main.py
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

# Solutions:
# 1. Add database indexes
# 2. Implement caching
# 3. Optimize queries
# 4. Scale horizontally
```

#### Issue: Database Connection Errors
```bash
# Check database connectivity
docker-compose exec postgres pg_isready

# Monitor connections
docker-compose exec postgres psql -U apex -d apex -c "SELECT * FROM pg_stat_activity;"

# Solutions:
# 1. Increase connection pool size
# 2. Add connection timeout
# 3. Implement connection retry logic
# 4. Scale database resources
```

### 9.2 Debug Mode

```python
# debug.py
import asyncio
import logging
from contextlib import contextmanager

class DebugManager:
    """Debug utilities"""
    
    def __init__(self):
        self.debug_mode = settings.debug
        self.logger = logging.getLogger("debug")
    
    @contextmanager
    def debug_context(self, operation_name):
        """Debug context manager"""
        if not self.debug_mode:
            yield
            return
        
        self.logger.info(f"Starting {operation_name}")
        start_time = time.time()
        
        try:
            yield
            duration = time.time() - start_time
            self.logger.info(f"Completed {operation_name} in {duration:.2f}s")
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Failed {operation_name} after {duration:.2f}s: {e}")
            raise
    
    async def debug_request(self, request_data):
        """Debug request processing"""
        if not self.debug_mode:
            return
        
        self.logger.debug(f"Request: {json.dumps(request_data, indent=2)}")
        
        # Add request tracing
        trace_id = str(uuid.uuid4())
        self.logger.debug(f"Trace ID: {trace_id}")
        
        return trace_id
```

## 10. Maintenance Procedures

### 10.1 Daily Maintenance

```bash
#!/bin/bash
# daily-maintenance.sh

echo "🔧 Running daily maintenance..."

# Log rotation
logrotate /etc/logrotate.d/apex

# Cleanup temporary files
find /app/temp -type f -mtime +1 -delete

# Update metrics
curl -s http://localhost:8080/metrics > /var/log/apex/metrics-$(date +%Y%m%d).log

# Health check
if ! curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "❌ Health check failed"
    # Send alert
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"APEX health check failed"}' \
        $SLACK_WEBHOOK_URL
fi

echo "✅ Daily maintenance complete"
```

### 10.2 Weekly Maintenance

```bash
#!/bin/bash
# weekly-maintenance.sh

echo "🔧 Running weekly maintenance..."

# Database maintenance
docker-compose exec postgres psql -U apex -d apex -c "VACUUM ANALYZE;"

# Vector store optimization
curl -X POST http://localhost:8000/optimize

# Security updates
apt-get update
apt-get upgrade -y

# Performance analysis
python -m src.scripts.performance_analysis

echo "✅ Weekly maintenance complete"
```

This comprehensive deployment and operational guide provides the foundation for running the APEX system reliably in production environments. It covers all aspects from initial installation through ongoing maintenance, ensuring system stability, security, and performance throughout the deployment lifecycle.