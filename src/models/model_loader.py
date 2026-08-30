from sentence_transformers import CrossEncoder, SentenceTransformer

from src.models.embedding_model import EmbeddingModel
from src.models.reranker_model import RerankerModel


class ModelLoader:
    @staticmethod
    def load_embedder(config: dict) -> EmbeddingModel:
        model_name = config.get("name", "")
        model_path = config.get("path", "")

        if not model_name or not model_path:
            raise ValueError("Embedder model name and path must be provided.")

        model = SentenceTransformer(
            model_name_or_path=model_path,
            device=config.get("device", "cpu"),
            trust_remote_code=config.get(
                "trust_remote_code",
                False,
            ),
        )

        return EmbeddingModel(
            name=model_name,
            model=model,
        )

    @staticmethod
    def load_reranker(config: dict) -> RerankerModel:
        model_name = config.get("name", "")
        model_path = config.get("path", "")

        if not model_name or not model_path:
            raise ValueError("Reranker model name and path must be provided.")

        model = CrossEncoder(
            model_name_or_path=model_path,
            device=config.get("device", "cpu"),
            trust_remote_code=config.get(
                "trust_remote_code",
                False,
            ),
        )

        return RerankerModel(
            name=model_name,
            model=model,
        )
