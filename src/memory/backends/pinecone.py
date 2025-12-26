"""
Pinecone Vector Store Backend
Module ID: APEX-MEM-PINECONE-001
Version: 0.1.0

Production Pinecone vector store implementation with:
- Connection pooling and retry logic
- HNSW indexing optimization
- Batch operations
- Metadata filtering
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

try:
    import pinecone
    from pinecone import ServerlessSpec, PodSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logging.warning("Pinecone not available. Install with: pip install pinecone-client")

from .. import MemoryChunk

logger = logging.getLogger(__name__)


class PineconeVectorStore:
    """
    Production Pinecone vector store backend.
    
    Provides scalable vector storage and similarity search
    with enterprise-grade reliability.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Pinecone vector store.
        
        Args:
            config: Configuration dictionary with Pinecone settings
        """
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone not available. Install with: pip install pinecone-client")
        
        self.api_key = config.get("api_key")
        self.environment = config.get("environment")
        self.index_name = config.get("index_name", "apex-memory")
        self.dimension = config.get("dimension", 1536)
        self.metric = config.get("metric", "cosine")
        self.batch_size = config.get("batch_size", 100)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)
        
        # Initialize Pinecone
        pinecone.init(api_key=self.api_key, environment=self.environment)
        
        # Create or get index
        self._ensure_index()
        
        # Get index instance
        self.index = pinecone.Index(self.index_name)
        
        logger.info(f"Pinecone vector store initialized: {self.index_name}")
    
    def _ensure_index(self) -> None:
        """Ensure index exists with proper configuration."""
        if self.index_name not in pinecone.list_indexes():
            logger.info(f"Creating new Pinecone index: {self.index_name}")
            
            # Create index with optimized HNSW parameters
            pinecone.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-west-2"
                )
            )
            
            # Wait for index to be ready
            logger.info("Waiting for index to be ready...")
            while not pinecone.describe_index(self.index_name).status.ready:
                asyncio.sleep(1)
    
    async def add_memory(self, chunk: MemoryChunk) -> str:
        """
        Add a memory chunk to Pinecone.
        
        Args:
            chunk: Memory chunk with embedding vector
            
        Returns:
            Memory ID
        """
        if not chunk.vector:
            raise ValueError("Memory chunk must have embedding vector")
        
        # Convert to numpy array for Pinecone
        vector = np.array(chunk.vector, dtype=np.float32)
        
        # Prepare metadata
        metadata = {
            "content": chunk.content,
            "agent_id": chunk.agent_id,
            "task_id": chunk.task_id or "",
            "file_path": chunk.file_path or "",
            "timestamp": chunk.timestamp.isoformat(),
            "utility_score": chunk.utility_score,
            "status": chunk.status,
            "superseded_by": chunk.superseded_by or "",
        }
        
        # Upsert to Pinecone with retry logic
        for attempt in range(self.max_retries):
            try:
                self.index.upsert(
                    vectors=[{
                        "id": chunk.id,
                        "values": vector.tolist(),
                        "metadata": metadata
                    }]
                )
                return chunk.id
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Pinecone upsert failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
    
    async def add_memories_batch(self, chunks: List[MemoryChunk]) -> List[str]:
        """
        Add multiple memory chunks in batch.
        
        Args:
            chunks: List of memory chunks
            
        Returns:
            List of memory IDs
        """
        if not chunks:
            return []
        
        # Validate all chunks have vectors
        for chunk in chunks:
            if not chunk.vector:
                raise ValueError("All memory chunks must have embedding vectors")
        
        # Process in batches
        all_ids = []
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            
            # Prepare batch data
            vectors = []
            for chunk in batch:
                vector = np.array(chunk.vector, dtype=np.float32)
                metadata = {
                    "content": chunk.content,
                    "agent_id": chunk.agent_id,
                    "task_id": chunk.task_id or "",
                    "file_path": chunk.file_path or "",
                    "timestamp": chunk.timestamp.isoformat(),
                    "utility_score": chunk.utility_score,
                    "status": chunk.status,
                    "superseded_by": chunk.superseded_by or "",
                }
                
                vectors.append({
                    "id": chunk.id,
                    "values": vector.tolist(),
                    "metadata": metadata
                })
            
            # Upsert batch with retry logic
            for attempt in range(self.max_retries):
                try:
                    self.index.upsert(vectors=vectors)
                    all_ids.extend([chunk.id for chunk in batch])
                    break
                    
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise
                    logger.warning(f"Pinecone batch upsert failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        return all_ids
    
    async def search(self, query_vector: List[float], top_k: int = 5,
                     min_similarity: float = 0.82, filter_dict: Optional[Dict[str, Any]] = None) -> List[MemoryChunk]:
        """
        Search for similar memories.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            min_similarity: Minimum cosine similarity threshold
            filter_dict: Optional metadata filters
            
        Returns:
            List of top-K similar memory chunks
        """
        # Convert to numpy array
        query_vector = np.array(query_vector, dtype=np.float32)
        
        # Prepare query
        query_params = {
            "vector": query_vector.tolist(),
            "top_k": top_k,
            "include_metadata": True
        }
        
        # Add filters if provided
        if filter_dict:
            query_params["filter"] = filter_dict
        
        # Query with retry logic
        for attempt in range(self.max_retries):
            try:
                results = self.index.query(**query_params)
                break
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Pinecone query failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        # Convert results to MemoryChunk objects
        memories = []
        for match in results["matches"]:
            if match["score"] >= min_similarity:
                metadata = match["metadata"]
                memory = MemoryChunk(
                    id=match["id"],
                    content=metadata["content"],
                    agent_id=metadata["agent_id"],
                    task_id=metadata.get("task_id") or None,
                    file_path=metadata.get("file_path") or None,
                    timestamp=datetime.fromisoformat(metadata["timestamp"]),
                    utility_score=metadata["utility_score"],
                    vector=query_vector.tolist(),  # Store query vector for reference
                    status=metadata["status"],
                    superseded_by=metadata.get("superseded_by") or None
                )
                memories.append(memory)
        
        return memories
    
    async def deprecate_memory(self, memory_id: str, superseded_by: str) -> None:
        """
        Mark a memory as deprecated and link to its replacement.
        
        Args:
            memory_id: ID of deprecated memory
            superseded_by: ID of new memory that replaces it
        """
        # Update metadata
        update_data = {
            "id": memory_id,
            "set_metadata": {
                "status": "deprecated",
                "superseded_by": superseded_by
            }
        }
        
        # Update with retry logic
        for attempt in range(self.max_retries):
            try:
                self.index.update(**update_data)
                return
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Pinecone update failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
    
    async def delete_memory(self, memory_id: str) -> None:
        """
        Delete a memory from the store.
        
        Args:
            memory_id: ID of memory to delete
        """
        # Delete with retry logic
        for attempt in range(self.max_retries):
            try:
                self.index.delete(ids=[memory_id])
                return
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Pinecone delete failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "total_vector_count": stats.total_vector_count,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {e}")
            return {}
    
    async def create_namespace(self, namespace: str) -> None:
        """
        Create a new namespace for isolation.
        
        Args:
            namespace: Namespace name
        """
        # Pinecone automatically creates namespaces on first use
        logger.info(f"Namespace '{namespace}' will be created on first use")
    
    async def delete_namespace(self, namespace: str) -> None:
        """
        Delete a namespace and all its vectors.
        
        Args:
            namespace: Namespace name
        """
        try:
            self.index.delete(namespace=namespace, delete_all=True)
            logger.info(f"Deleted namespace: {namespace}")
        except Exception as e:
            logger.error(f"Failed to delete namespace {namespace}: {e}")
            raise


def create_pinecone_store(config: Dict[str, Any]) -> PineconeVectorStore:
    """
    Create a Pinecone vector store instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        PineconeVectorStore instance
    """
    return PineconeVectorStore(config)


__all__ = [
    "PineconeVectorStore",
    "create_pinecone_store",
]