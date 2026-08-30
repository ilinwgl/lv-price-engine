from dataclasses import dataclass

from sentence_transformers import CrossEncoder


@dataclass
class RerankerModel:
    name: str
    model: CrossEncoder
