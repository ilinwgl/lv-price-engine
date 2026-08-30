from dataclasses import dataclass

from sentence_transformers import SentenceTransformer


@dataclass
class EmbeddingModel:
    name: str
    model: SentenceTransformer
