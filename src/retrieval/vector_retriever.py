import torch

from src.models.database_candidate.commodity_candidate import CommodityCandidate
from src.models.inference_model.embedding_model import EmbeddingModel
from src.models.results.match_result import MatchCandidate
from src.retrieval.base_retriever import BaseRetriever


class VectorRetriever(BaseRetriever):
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        candidates: list[CommodityCandidate],
        candidate_texts: list[str],
    ) -> None:
        if len(candidates) != len(candidate_texts):
            raise ValueError(
                "Number of candidates must match number of candidate texts."
            )

        self._embedding_model = embedding_model
        self._candidates = candidates

        candidate_embeddings = self._embedding_model.model.encode(
            inputs=candidate_texts,
            batch_size=16,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        self._candidate_embeddings = torch.as_tensor(candidate_embeddings)

    def retrieve(
        self,
        query_text: str,
        top_k: int,
    ) -> list[MatchCandidate]:
        if not self._candidates:
            return []

        query_embedding = self._embedding_model.model.encode(
            inputs=query_text,
            normalize_embeddings=True,
        )

        query_embedding = torch.as_tensor(query_embedding)

        scores = self._candidate_embeddings @ query_embedding

        top_k = min(
            top_k,
            len(self._candidates),
        )

        top_indices = scores.argsort(descending=True)[:top_k]

        results: list[MatchCandidate] = []

        for index in top_indices:
            results.append(
                MatchCandidate(
                    candidate=self._candidates[index],
                    score=float(scores[index]),
                )
            )

        return results
