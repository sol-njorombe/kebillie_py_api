from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddingService(ABC):
    """
    Abstract base class for embedding services.
    Ensures all models implement the same interface.
    """
    @abstractmethod
    def get_content_vector(self, text: str) -> List[float]:
        """Generate a vector for document/bill content storage."""
        pass

    @abstractmethod
    def get_search_vector(self, text: str) -> List[float]:
        """Generate a vector for search queries."""
        pass

class JinaEmbeddingService(BaseEmbeddingService):
    """
    Jina Embeddings v5 Service.
    Loads the model once when the class is instantiated.
    """
    def __init__(self):
        import logging
        logging.getLogger().setLevel(logging.INFO)
        logging.info("Loading Jina Embedding Model... (this may take a moment)")
        
        from sentence_transformers import SentenceTransformer
        # We use trust_remote_code=True as Jina models often require custom code execution
        self.model = SentenceTransformer('jinaai/jina-embeddings-v5-text-small', trust_remote_code=True)
        logging.info("Jina Embedding Model loaded successfully!")

    def get_content_vector(self, text: str) -> List[float]:
        # Jina v5 expects the general "retrieval" task and manual string prefixes
        prefixed_text = f"Document: {text}"
        vector = self.model.encode(prefixed_text, task="retrieval")
        return vector.tolist()

    def get_search_vector(self, text: str) -> List[float]:
        # Prefixing the text as a query
        prefixed_text = f"Query: {text}"
        vector = self.model.encode(prefixed_text, task="retrieval")
        return vector.tolist()

# Singleton-like instance to avoid reloading the model if imported multiple times
_embedding_service_instance = None

def get_embedding_service() -> BaseEmbeddingService:
    """
    Factory function to get the currently active embedding service.
    """
    global _embedding_service_instance
    
    if _embedding_service_instance is not None:
        return _embedding_service_instance

    from app.core.config import settings
    
    model_choice = settings.ACTIVE_EMBEDDING_MODEL.lower()
    
    if model_choice == "jina":
        _embedding_service_instance = JinaEmbeddingService()
    elif model_choice == "gemma":
        raise NotImplementedError("EmbeddingGemma 3 is not implemented yet.")
    else:
        raise ValueError(f"Unknown ACTIVE_EMBEDDING_MODEL: {model_choice}")
        
    return _embedding_service_instance
