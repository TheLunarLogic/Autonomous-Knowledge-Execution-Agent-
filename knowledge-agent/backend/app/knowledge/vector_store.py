"""
ChromaDB vector store — setup and retrieval.
"""

from pathlib import Path

import chromadb

from app.core.config import settings
from app.core.logging import logger

# Module-level singleton
_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None

COLLECTION_NAME = "knowledge_base"


def _get_client() -> chromadb.ClientAPI:
    """Get or create the ChromaDB persistent client."""
    global _client
    if _client is None:
        persist_dir = Path(settings.CHROMA_PATH)
        persist_dir.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(persist_dir))
        logger.info("ChromaDB client initialized at %s", persist_dir)
    return _client


def _get_collection() -> chromadb.Collection:
    """Get or create the knowledge_base collection."""
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Knowledge base embeddings"},
        )
        logger.info(
            "ChromaDB collection '%s' ready (%d documents)",
            COLLECTION_NAME,
            _collection.count(),
        )
    return _collection


class VectorStore:
    """Simple wrapper around a ChromaDB collection for add/retrieve ops."""

    def __init__(self) -> None:
        self.collection = _get_collection()

    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict] | None = None,
        ids: list[str] | None = None,
    ) -> None:
        """Add documents to the vector store (ChromaDB generates embeddings)."""
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve the top-k most relevant documents for a query.

        Returns a list of dicts with keys: content, metadata, distance.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count() or 1),
        )

        docs = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                entry = {
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                }
                docs.append(entry)

        logger.info("Retrieved %d documents for query: '%s'", len(docs), query[:80])
        return docs

    @property
    def count(self) -> int:
        return self.collection.count()


def get_vector_store() -> VectorStore:
    """Factory function for the vector store singleton."""
    return VectorStore()
