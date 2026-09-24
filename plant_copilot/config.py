from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    chroma_path: str = os.getenv("CHROMA_PATH", "./chroma_db")
    collection: str = os.getenv("CHROMA_COLLECTION", "plant_knowledge_v1")
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "120"))
    threshold: float = float(os.getenv("RELEVANCE_THRESHOLD", "0.50"))
    top_k: int = int(os.getenv("TOP_K", "5"))
    groq_model: str = os.getenv("GROQ_MODEL", "")

    def validate(self) -> None:
        if self.chunk_size < 100:
            raise ValueError("CHUNK_SIZE must be at least 100 characters")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE")
        if not 0 <= self.threshold <= 1:
            raise ValueError("RELEVANCE_THRESHOLD must be between 0 and 1")
