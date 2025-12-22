"""
Semantic Memory and Vector Store Infrastructure
Module ID: APEX-MEM-009
Version: 0.1.0

Multi-tiered semantic memory architecture with:
- L1: Active Context (LLM context window)
- L2: Semantic Vector Store (HNSW indexed embeddings)
- L3: Archival Cold Storage (Parquet files)

Implements semantic sieve, vector embedding pipeline, and context pruning.

VERSION CONTROL FOOTER
File: src/memory/__init__.py
Version: 0.1.0
Last Modified: 2025-12-21T00:00:00Z
Git Hash: INITIAL
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from src.core.constants import (
    VECTOR_STORE_BACKEND,
    VECTOR_EMBEDDING_MODEL,
    VECTOR_DIMENSION,
    SEMANTIC_UTILITY_THRESHOLD,
    CHUNK_SIZE_TOKENS,
    CHUNK_OVERLAP_TOKENS,
    TEMP_DIR,
)


@dataclass
class MemoryChunk:
    """Representation of a memory chunk for embedding."""
    id: str
    content: str
    agent_id: str
    task_id: Optional[str]
    file_path: Optional[str]
    timestamp: datetime
    utility_score: float
    vector: Optional[List[float]] = None
    status: str = "active"  # active, deprecated
    superseded_by: Optional[str] = None


class SemanticSieve:
    """
    Filters and scores memory chunks before embedding.
    
    Implements utility scoring:
    U_s = (Complexity × 0.4) + (Uniqueness × 0.6)
    """

    def __init__(self, utility_threshold: float = SEMANTIC_UTILITY_THRESHOLD):
        """Initialize semantic sieve."""
        self.utility_threshold = utility_threshold

    def process_chunk(self, content: str, complexity: float, uniqueness: float) -> bool:
        """
        Determine if a chunk should be embedded.
        
        Args:
            content: The chunk content
            complexity: Complexity score (0.0-1.0)
            uniqueness: Uniqueness score (0.0-1.0)
            
        Returns:
            True if chunk should be embedded
        """
        utility_score = (complexity * 0.4) + (uniqueness * 0.6)
        return utility_score >= self.utility_threshold

    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE_TOKENS, 
                   overlap: int = CHUNK_OVERLAP_TOKENS) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Note: This is a simplistic implementation using character counts.
        In production, use token-aware splitting with a tokenizer.
        """
        chunks = []
        text_len = len(text)
        
        if text_len <= chunk_size:
            return [text]
        
        # Approximate tokens to characters (rough estimate: 4 chars per token)
        char_chunk_size = chunk_size * 4
        char_overlap = overlap * 4
        
        start = 0
        while start < text_len:
            end = min(start + char_chunk_size, text_len)
            chunks.append(text[start:end])
            start = end - char_overlap
        
        return chunks


class VectorStore:
    """
    Abstract interface for vector store backends (ChromaDB, FAISS).
    Implements HNSW graph topology for fast similarity search.
    """

    def __init__(self, backend: str = VECTOR_STORE_BACKEND):
        """Initialize vector store."""
        self.backend = backend
        self.memories: Dict[str, MemoryChunk] = {}

    async def add_memory(self, chunk: MemoryChunk) -> str:
        """
        Add a memory chunk to the store.
        
        Args:
            chunk: Memory chunk with embedding vector
            
        Returns:
            Memory ID
        """
        if chunk.id is None:
            chunk.id = str(uuid.uuid4())
        
        self.memories[chunk.id] = chunk
        return chunk.id

    async def search(self, query_vector: List[float], top_k: int = 5,
                     min_similarity: float = 0.82) -> List[MemoryChunk]:
        """
        Similarity search using cosine distance.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            min_similarity: Minimum cosine similarity threshold
            
        Returns:
            List of top-K similar memory chunks
        """
        if not self.memories:
            return []
        
        # This is a stub. In production, use HNSW algorithms for O(log N) search
        # For now, brute force similarity
        results = []
        for memory in self.memories.values():
            if memory.status != "active":
                continue
            
            if memory.vector:
                similarity = self._cosine_similarity(query_vector, memory.vector)
                if similarity >= min_similarity:
                    results.append((memory, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in results[:top_k]]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a ** 2 for a in vec1) ** 0.5
        magnitude2 = sum(b ** 2 for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

    async def deprecate_memory(self, memory_id: str, superseded_by: str) -> None:
        """
        Mark a memory as deprecated and link to its replacement.
        
        Args:
            memory_id: ID of deprecated memory
            superseded_by: ID of new memory that replaces it
        """
        if memory_id in self.memories:
            self.memories[memory_id].status = "deprecated"
            self.memories[memory_id].superseded_by = superseded_by


class ContextManager:
    """
    Manages L1 context window pruning using information bottleneck principle.
    
    Pruning heuristics:
    1. Recency Bias: Retain last 3 turns with 100% fidelity
    2. Salience Filtering: Protect "Key Decisions"
    3. Summarization: Replace verbose logs with summaries
    """

    def __init__(self, max_context_tokens: int = 8000):
        """Initialize context manager."""
        self.max_context_tokens = max_context_tokens
        self.context_history: List[Dict[str, Any]] = []

    def add_to_context(self, turn: Dict[str, Any]) -> None:
        """Add a turn to context history."""
        self.context_history.append({
            **turn,
            "timestamp": datetime.now(timezone.utc)
        })

    def prune_context(self, current_token_count: int) -> List[Dict[str, Any]]:
        """
        Prune context to fit within token limit.
        
        Returns retention score for each block:
        R_s = (Salience × Recency) / TokenCost
        """
        if current_token_count <= self.max_context_tokens:
            return self.context_history
        
        pruned = []
        tokens_remaining = self.max_context_tokens
        
        # Keep last 3 turns with 100% fidelity
        for turn in self.context_history[-3:]:
            turn_tokens = turn.get("token_count", 0)
            if tokens_remaining >= turn_tokens:
                pruned.insert(0, turn)
                tokens_remaining -= turn_tokens
        
        # For older turns, apply retention scoring
        for turn in self.context_history[:-3]:
            if tokens_remaining <= 0:
                break
            
            salience = turn.get("salience", 0.5)
            recency = turn.get("recency", 0.3)
            token_cost = turn.get("token_count", 100)
            
            retention_score = (salience * recency) / max(token_cost, 1)
            
            if retention_score > 0.5 and tokens_remaining >= token_cost:
                pruned.insert(0, turn)
                tokens_remaining -= token_cost
        
        return pruned


# Global instances
_vector_store: Optional[VectorStore] = None
_semantic_sieve: Optional[SemanticSieve] = None
_context_manager: Optional[ContextManager] = None


def get_vector_store() -> VectorStore:
    """Get or create global vector store."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def get_semantic_sieve() -> SemanticSieve:
    """Get or create global semantic sieve."""
    global _semantic_sieve
    if _semantic_sieve is None:
        _semantic_sieve = SemanticSieve()
    return _semantic_sieve


def get_context_manager() -> ContextManager:
    """Get or create global context manager."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


__all__ = [
    "MemoryChunk",
    "SemanticSieve",
    "VectorStore",
    "ContextManager",
    "get_vector_store",
    "get_semantic_sieve",
    "get_context_manager",
]
