"""
Weaviate Vector Store Backend
Module ID: APEX-MEM-WEAVIATE-001
Version: 0.1.0

Production Weaviate vector store implementation with:
- GraphQL API integration
- Schema management
- Batch operations
- Hybrid search capabilities
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

try:
    import weaviate
    from weaviate.client import Client
    from weaviate.config import ConnectionConfig, Auth
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    logging.warning("Weaviate not available. Install with: pip install weaviate-client")

from .. import MemoryChunk

logger = logging.getLogger(__name__)


class WeaviateVectorStore:
    """
    Production Weaviate vector store backend.
    
    Provides scalable vector storage with GraphQL API,
    schema management, and hybrid search.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Weaviate vector store.
        
        Args:
            config: Configuration dictionary with Weaviate settings
        """
        if not WEAVIATE_AVAILABLE:
            raise ImportError("Weaviate not available. Install with: pip install weaviate-client")
        
        self.url = config.get("url", "http://localhost:8080")
        self.api_key = config.get("api_key")
        self.batch_size = config.get("batch_size", 100)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)
        self.class_name = "MemoryChunk"
        
        # Initialize Weaviate client
        self.client = self._create_client()
        
        # Ensure schema exists
        self._ensure_schema()
        
        logger.info(f"Weaviate vector store initialized: {self.url}")
    
    def _create_client(self) -> Client:
        """Create Weaviate client with authentication."""
        auth_config = None
        if self.api_key:
            auth_config = Auth.api_key(self.api_key)
        
        connection_config = ConnectionConfig.from_url(
            url=self.url,
            auth_config=auth_config
        )
        
        return weaviate.Client(connection_config)
    
    def _ensure_schema(self) -> None:
        """Ensure the MemoryChunk class schema exists."""
        schema = {
            "class": self.class_name,
            "description": "APEX Memory Chunk",
            "vectorizer": "none",  # We provide our own vectors
            "moduleConfig": {
                "q2a-50e": {
                    "vectorizeClassName": False
                }
            },
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "Memory content"
                },
                {
                    "name": "agent_id",
                    "dataType": ["string"],
                    "description": "Agent identifier"
                },
                {
                    "name": "task_id",
                    "dataType": ["string"],
                    "description": "Task identifier"
                },
                {
                    "name": "file_path",
                    "dataType": ["string"],
                    "description": "Source file path"
                },
                {
                    "name": "timestamp",
                    "dataType": ["date"],
                    "description": "Creation timestamp"
                },
                {
                    "name": "utility_score",
                    "dataType": ["number"],
                    "description": "Utility score"
                },
                {
                    "name": "status",
                    "dataType": ["string"],
                    "description": "Memory status"
                },
                {
                    "name": "superseded_by",
                    "dataType": ["string"],
                    "description": "ID of superseding memory"
                }
            ]
        }
        
        # Check if class exists
        existing = self.client.schema.get(self.class_name)
        if not existing:
            logger.info(f"Creating Weaviate class: {self.class_name}")
            self.client.schema.create_class(schema)
    
    async def add_memory(self, chunk: MemoryChunk) -> str:
        """
        Add a memory chunk to Weaviate.
        
        Args:
            chunk: Memory chunk with embedding vector
            
        Returns:
            Memory ID
        """
        if not chunk.vector:
            raise ValueError("Memory chunk must have embedding vector")
        
        # Prepare data object
        data_object = {
            "content": chunk.content,
            "agent_id": chunk.agent_id,
            "task_id": chunk.task_id or "",
            "file_path": chunk.file_path or "",
            "timestamp": chunk.timestamp.isoformat(),
            "utility_score": chunk.utility_score,
            "status": chunk.status,
            "superseded_by": chunk.superseded_by or "",
        }
        
        # Add with retry logic
        for attempt in range(self.max_retries):
            try:
                result = self.client.data_object.create(
                    data_object=data_object,
                    class_name=self.class_name,
                    vector=chunk.vector,
                    uuid=chunk.id
                )
                return chunk.id
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Weaviate create failed (attempt {attempt + 1}): {e}")
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
        
        # Configure batch
        self.client.batch.configure(
            batch_size=self.batch_size,
            dynamic=True,
            callback=self._batch_callback
        )
        
        # Add chunks to batch
        all_ids = []
        with self.client.batch as batch:
            for chunk in chunks:
                data_object = {
                    "content": chunk.content,
                    "agent_id": chunk.agent_id,
                    "task_id": chunk.task_id or "",
                    "file_path": chunk.file_path or "",
                    "timestamp": chunk.timestamp.isoformat(),
                    "utility_score": chunk.utility_score,
                    "status": chunk.status,
                    "superseded_by": chunk.superseded_by or "",
                }
                
                batch.add_data_object(
                    data_object=data_object,
                    class_name=self.class_name,
                    vector=chunk.vector,
                    uuid=chunk.id
                )
                all_ids.append(chunk.id)
        
        return all_ids
    
    def _batch_callback(self, results: List[Dict[str, Any]]) -> None:
        """Callback for batch operations."""
        for result in results:
            if result.get("result", {}).get("errors"):
                logger.error(f"Batch error: {result}")
    
    async def search(self, query_vector: List[float], top_k: int = 5,
                     min_similarity: float = 0.82, filter_dict: Optional[Dict[str, Any]] = None) -> List[MemoryChunk]:
        """
        Search for similar memories.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            filter_dict: Optional metadata filters
            
        Returns:
            List of top-K similar memory chunks
        """
        # Build near vector query
        near_vector = {"vector": query_vector}
        
        # Add certainty threshold (Weaviate uses certainty = (1 + cosine) / 2)
        certainty = (1 + min_similarity) / 2
        near_vector["certainty"] = certainty
        
        # Build query
        query = self.client.query.get(self.class_name, [
            "content",
            "agent_id",
            "task_id",
            "file_path",
            "timestamp",
            "utility_score",
            "status",
            "superseded_by",
            "_additional {id certainty}"
        ])
        
        # Add filters if provided
        if filter_dict:
            where_filter = self._build_where_filter(filter_dict)
            query = query.with_where(where_filter)
        
        # Execute near vector search
        query = query.with_near_vector(near_vector).with_limit(top_k)
        
        # Execute with retry logic
        for attempt in range(self.max_retries):
            try:
                result = query.do()
                break
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Weaviate query failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        # Convert results to MemoryChunk objects
        memories = []
        if result and "data" in result and "Get" in result["data"]:
            for item in result["data"]["Get"][self.class_name]:
                # Convert certainty back to cosine similarity
                certainty = item["_additional"]["certainty"]
                similarity = (certainty * 2) - 1
                
                if similarity >= min_similarity:
                    memory = MemoryChunk(
                        id=item["_additional"]["id"],
                        content=item["content"],
                        agent_id=item["agent_id"],
                        task_id=item.get("task_id") or None,
                        file_path=item.get("file_path") or None,
                        timestamp=datetime.fromisoformat(item["timestamp"]),
                        utility_score=item["utility_score"],
                        vector=query_vector,  # Store query vector for reference
                        status=item["status"],
                        superseded_by=item.get("superseded_by") or None
                    )
                    memories.append(memory)
        
        return memories
    
    def _build_where_filter(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build Weaviate where filter from dictionary."""
        if not filter_dict:
            return {}
        
        operators = {
            "eq": "Equal",
            "ne": "NotEqual",
            "gt": "GreaterThan",
            "gte": "GreaterThanEqual",
            "lt": "LessThan",
            "lte": "LessThanEqual",
            "like": "Like",
            "in": "In",
            "not_in": "NotIn"
        }
        
        filters = []
        for field, condition in filter_dict.items():
            if isinstance(condition, dict):
                for op, value in condition.items():
                    if op in operators:
                        filters.append({
                            "path": [field],
                            "operator": operators[op],
                            "valueText": value if isinstance(value, str) else str(value)
                        })
            else:
                # Default to equality
                filters.append({
                    "path": [field],
                    "operator": "Equal",
                    "valueText": condition if isinstance(condition, str) else str(condition)
                })
        
        if len(filters) == 1:
            return filters[0]
        else:
            return {"operator": "And", "operands": filters}
    
    async def deprecate_memory(self, memory_id: str, superseded_by: str) -> None:
        """
        Mark a memory as deprecated and link to its replacement.
        
        Args:
            memory_id: ID of deprecated memory
            superseded_by: ID of new memory that replaces it
        """
        # Update with retry logic
        for attempt in range(self.max_retries):
            try:
                self.client.data_object.update(
                    uuid=memory_id,
                    class_name=self.class_name,
                    data_object={
                        "status": "deprecated",
                        "superseded_by": superseded_by
                    }
                )
                return
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Weaviate update failed (attempt {attempt + 1}): {e}")
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
                self.client.data_object.delete(
                    uuid=memory_id,
                    class_name=self.class_name
                )
                return
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Weaviate delete failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            schema = self.client.schema.get(self.class_name)
            return {
                "class": self.class_name,
                "properties": len(schema.get("properties", [])),
                "vectorizer": schema.get("vectorizer", "none"),
                "moduleConfig": schema.get("moduleConfig", {})
            }
        except Exception as e:
            logger.error(f"Failed to get Weaviate stats: {e}")
            return {}
    
    async def hybrid_search(self, query: str, query_vector: List[float], 
                           alpha: float = 0.5, top_k: int = 5) -> List[MemoryChunk]:
        """
        Perform hybrid search combining keyword and vector search.
        
        Args:
            query: Text query for keyword search
            query_vector: Vector for similarity search
            alpha: Weight between keyword (0) and vector (1) search
            top_k: Number of results to return
            
        Returns:
            List of hybrid search results
        """
        # Build hybrid query
        hybrid_query = (
            self.client.query
            .get(self.class_name, [
                "content",
                "agent_id",
                "task_id",
                "file_path",
                "timestamp",
                "utility_score",
                "status",
                "superseded_by",
                "_additional {id score}"
            ])
            .with_hybrid(
                query=query,
                vector=query_vector,
                alpha=alpha
            )
            .with_limit(top_k)
        )
        
        # Execute with retry logic
        for attempt in range(self.max_retries):
            try:
                result = hybrid_query.do()
                break
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Weaviate hybrid search failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        # Convert results to MemoryChunk objects
        memories = []
        if result and "data" in result and "Get" in result["data"]:
            for item in result["data"]["Get"][self.class_name]:
                memory = MemoryChunk(
                    id=item["_additional"]["id"],
                    content=item["content"],
                    agent_id=item["agent_id"],
                    task_id=item.get("task_id") or None,
                    file_path=item.get("file_path") or None,
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    utility_score=item["utility_score"],
                    vector=query_vector,  # Store query vector for reference
                    status=item["status"],
                    superseded_by=item.get("superseded_by") or None
                )
                memories.append(memory)
        
        return memories


def create_weaviate_store(config: Dict[str, Any]) -> WeaviateVectorStore:
    """
    Create a Weaviate vector store instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        WeaviateVectorStore instance
    """
    return WeaviateVectorStore(config)


__all__ = [
    "WeaviateVectorStore",
    "create_weaviate_store",
]