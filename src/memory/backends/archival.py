"""
L3 Archival Storage Backend
Module ID: APEX-MEM-ARCHIVAL-001
Version: 0.1.0

Provides L3 archival storage for long-term memory retention
in the APEX Agent Payroll System.
"""

import asyncio
import json
import gzip
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ArchivalStatus(Enum):
    """Archival storage status."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPRESSED = "compressed"
    DELETED = "deleted"


class CompressionType(Enum):
    """Compression types for archival."""
    GZIP = "gzip"
    NONE = "none"


@dataclass
class ArchivalMetadata:
    """Metadata for archived memory items."""
    id: str
    original_id: str
    timestamp: datetime
    status: ArchivalStatus
    compression_type: CompressionType
    size_bytes: int
    compressed_size_bytes: Optional[int] = None
    checksum: str = ""
    tags: List[str] = field(default_factory=list)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    retention_policy: str = "default"
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchivalConfig:
    """Configuration for archival storage."""
    base_path: str = "./archival_storage"
    compression_enabled: bool = True
    compression_type: CompressionType = CompressionType.GZIP
    auto_archive_days: int = 30
    auto_delete_days: int = 365
    max_storage_gb: float = 100.0
    checksum_enabled: bool = True
    index_enabled: bool = True


class ArchivalStorage:
    """
    L3 archival storage backend for long-term memory retention.
    
    Provides compressed, indexed storage for infrequently accessed
    memory items with retention policies and automatic cleanup.
    """
    
    def __init__(self, config: ArchivalConfig = None):
        """
        Initialize archival storage.
        
        Args:
            config: Archival configuration
        """
        self.config = config or ArchivalConfig()
        self.base_path = Path(self.config.base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.base_path / "data").mkdir(exist_ok=True)
        (self.base_path / "metadata").mkdir(exist_ok=True)
        (self.base_path / "index").mkdir(exist_ok=True)
        
        # In-memory index for fast lookups
        self._index: Dict[str, ArchivalMetadata] = {}
        self._tag_index: Dict[str, List[str]] = {}
        
        # Load existing index
        if self.config.index_enabled:
            self._load_index()
        
        logger.info(f"ArchivalStorage initialized at {self.base_path}")
    
    async def store(
        self,
        item_id: str,
        data: Dict[str, Any],
        tags: List[str] = None,
        retention_policy: str = "default",
        expires_at: datetime = None
    ) -> str:
        """
        Store an item in archival storage.
        
        Args:
            item_id: Original item ID
            data: Item data to archive
            tags: Optional tags
            retention_policy: Retention policy name
            expires_at: Optional expiration time
            
        Returns:
            Archival item ID
        """
        try:
            # Generate archival ID
            archival_id = self._generate_archival_id(item_id)
            
            # Serialize data
            json_data = json.dumps(data, default=str)
            data_bytes = json_data.encode('utf-8')
            
            # Compress if enabled
            if self.config.compression_enabled:
                compressed_bytes = gzip.compress(data_bytes)
                compression_type = self.config.compression_type
            else:
                compressed_bytes = data_bytes
                compression_type = CompressionType.NONE
            
            # Calculate checksum
            checksum = ""
            if self.config.checksum_enabled:
                checksum = hashlib.sha256(compressed_bytes).hexdigest()
            
            # Write data file
            data_path = self.base_path / "data" / f"{archival_id}.dat"
            with open(data_path, 'wb') as f:
                f.write(compressed_bytes)
            
            # Create metadata
            metadata = ArchivalMetadata(
                id=archival_id,
                original_id=item_id,
                timestamp=datetime.utcnow(),
                status=ArchivalStatus.ARCHIVED,
                compression_type=compression_type,
                size_bytes=len(data_bytes),
                compressed_size_bytes=len(compressed_bytes),
                checksum=checksum,
                tags=tags or [],
                retention_policy=retention_policy,
                expires_at=expires_at
            )
            
            # Write metadata file
            metadata_path = self.base_path / "metadata" / f"{archival_id}.json"
            with open(metadata_path, 'w') as f:
                json.dump(asdict(metadata), f, default=str)
            
            # Update index
            if self.config.index_enabled:
                self._update_index(metadata)
            
            logger.info(f"Archived item: {item_id} -> {archival_id}")
            return archival_id
            
        except Exception as e:
            logger.error(f"Failed to archive item {item_id}: {str(e)}")
            raise
    
    async def retrieve(self, archival_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an item from archival storage.
        
        Args:
            archival_id: Archival item ID
            
        Returns:
            Retrieved data or None if not found
        """
        try:
            # Get metadata
            metadata = self._get_metadata(archival_id)
            if not metadata:
                return None
            
            # Check if expired
            if metadata.expires_at and datetime.utcnow() > metadata.expires_at:
                logger.warning(f"Archived item {archival_id} has expired")
                return None
            
            # Read data file
            data_path = self.base_path / "data" / f"{archival_id}.dat"
            if not data_path.exists():
                logger.error(f"Data file not found for {archival_id}")
                return None
            
            with open(data_path, 'rb') as f:
                data_bytes = f.read()
            
            # Decompress if needed
            if metadata.compression_type == CompressionType.GZIP:
                data_bytes = gzip.decompress(data_bytes)
            
            # Parse JSON
            data = json.loads(data_bytes.decode('utf-8'))
            
            # Update access metadata
            metadata.access_count += 1
            metadata.last_accessed = datetime.utcnow()
            await self._update_metadata(metadata)
            
            logger.info(f"Retrieved archived item: {archival_id}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve archived item {archival_id}: {str(e)}")
            return None
    
    async def search(
        self,
        query: str = None,
        tags: List[str] = None,
        date_from: datetime = None,
        date_to: datetime = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search archived items.
        
        Args:
            query: Text query (not implemented for L3)
            tags: Filter by tags
            date_from: Filter by date from
            date_to: Filter by date to
            limit: Maximum results
            
        Returns:
            List of matching items metadata
        """
        try:
            results = []
            
            # Search through index
            for metadata in self._index.values():
                # Skip deleted items
                if metadata.status == ArchivalStatus.DELETED:
                    continue
                
                # Check expiration
                if metadata.expires_at and datetime.utcnow() > metadata.expires_at:
                    continue
                
                # Filter by tags
                if tags and not any(tag in metadata.tags for tag in tags):
                    continue
                
                # Filter by date range
                if date_from and metadata.timestamp < date_from:
                    continue
                if date_to and metadata.timestamp > date_to:
                    continue
                
                results.append(asdict(metadata))
                
                if len(results) >= limit:
                    break
            
            logger.info(f"Found {len(results)} archived items")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search archived items: {str(e)}")
            return []
    
    async def delete(self, archival_id: str) -> bool:
        """
        Delete an archived item.
        
        Args:
            archival_id: Archival item ID
            
        Returns:
            True if deleted successfully
        """
        try:
            # Get metadata
            metadata = self._get_metadata(archival_id)
            if not metadata:
                return False
            
            # Delete data file
            data_path = self.base_path / "data" / f"{archival_id}.dat"
            if data_path.exists():
                data_path.unlink()
            
            # Update metadata status
            metadata.status = ArchivalStatus.DELETED
            await self._update_metadata(metadata)
            
            # Update index
            if archival_id in self._index:
                del self._index[archival_id]
            
            logger.info(f"Deleted archived item: {archival_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete archived item {archival_id}: {str(e)}")
            return False
    
    async def cleanup_expired(self) -> int:
        """
        Clean up expired items.
        
        Returns:
            Number of items cleaned up
        """
        try:
            expired_count = 0
            now = datetime.utcnow()
            
            for archival_id, metadata in list(self._index.items()):
                if metadata.expires_at and now > metadata.expires_at:
                    if await self.delete(archival_id):
                        expired_count += 1
            
            logger.info(f"Cleaned up {expired_count} expired items")
            return expired_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired items: {str(e)}")
            return 0
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Storage statistics
        """
        try:
            total_items = len(self._index)
            total_size = sum(m.compressed_size_bytes or m.size_bytes for m in self._index.values())
            compression_ratio = 0
            
            if total_size > 0:
                original_size = sum(m.size_bytes for m in self._index.values())
                compression_ratio = (original_size - total_size) / original_size
            
            # Get disk usage
            disk_usage = sum(f.stat().st_size for f in self.base_path.rglob('*') if f.is_file())
            
            return {
                "total_items": total_items,
                "total_size_bytes": total_size,
                "disk_usage_bytes": disk_usage,
                "compression_ratio": compression_ratio,
                "base_path": str(self.base_path),
                "config": asdict(self.config)
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {str(e)}")
            return {}
    
    def _generate_archival_id(self, item_id: str) -> str:
        """Generate a unique archival ID."""
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{item_id}{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _get_metadata(self, archival_id: str) -> Optional[ArchivalMetadata]:
        """Get metadata for an archival item."""
        # Try index first
        if archival_id in self._index:
            return self._index[archival_id]
        
        # Load from file
        metadata_path = self.base_path / "metadata" / f"{archival_id}.json"
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r') as f:
                data = json.load(f)
            
            # Convert datetime strings
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            if data.get('last_accessed'):
                data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
            if data.get('expires_at'):
                data['expires_at'] = datetime.fromisoformat(data['expires_at'])
            
            metadata = ArchivalMetadata(**data)
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load metadata for {archival_id}: {str(e)}")
            return None
    
    async def _update_metadata(self, metadata: ArchivalMetadata) -> None:
        """Update metadata for an archival item."""
        try:
            metadata_path = self.base_path / "metadata" / f"{metadata.id}.json"
            with open(metadata_path, 'w') as f:
                json.dump(asdict(metadata), f, default=str)
            
            # Update index
            if self.config.index_enabled:
                self._update_index(metadata)
                
        except Exception as e:
            logger.error(f"Failed to update metadata for {metadata.id}: {str(e)}")
    
    def _load_index(self) -> None:
        """Load the archival index from disk."""
        try:
            index_path = self.base_path / "index" / "archival_index.json"
            if not index_path.exists():
                return
            
            with open(index_path, 'r') as f:
                index_data = json.load(f)
            
            for item_data in index_data:
                # Convert datetime strings
                item_data['timestamp'] = datetime.fromisoformat(item_data['timestamp'])
                if item_data.get('last_accessed'):
                    item_data['last_accessed'] = datetime.fromisoformat(item_data['last_accessed'])
                if item_data.get('expires_at'):
                    item_data['expires_at'] = datetime.fromisoformat(item_data['expires_at'])
                
                metadata = ArchivalMetadata(**item_data)
                self._index[metadata.id] = metadata
                
                # Update tag index
                for tag in metadata.tags:
                    if tag not in self._tag_index:
                        self._tag_index[tag] = []
                    if metadata.id not in self._tag_index[tag]:
                        self._tag_index[tag].append(metadata.id)
            
            logger.info(f"Loaded {len(self._index)} items from archival index")
            
        except Exception as e:
            logger.error(f"Failed to load archival index: {str(e)}")
    
    def _update_index(self, metadata: ArchivalMetadata) -> None:
        """Update the in-memory index."""
        self._index[metadata.id] = metadata
        
        # Update tag index
        for tag in metadata.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            if metadata.id not in self._tag_index[tag]:
                self._tag_index[tag].append(metadata.id)
    
    async def save_index(self) -> None:
        """Save the archival index to disk."""
        try:
            if not self.config.index_enabled:
                return
            
            index_path = self.base_path / "index" / "archival_index.json"
            index_data = [asdict(metadata) for metadata in self._index.values()]
            
            with open(index_path, 'w') as f:
                json.dump(index_data, f, default=str)
            
            logger.info(f"Saved {len(index_data)} items to archival index")
            
        except Exception as e:
            logger.error(f"Failed to save archival index: {str(e)}")


# Global archival storage instance
archival_storage = ArchivalStorage()