import torch

from src.models.lv_position import LVPosition
from src.models.price_candidate import PriceCandidate


class Matcher:
    @staticmethod
    def match(
        lv_embedding: torch.Tensor,
        candidate_embeddings: torch.Tensor,
        candidates: list[PriceCandidate],
        top_k: int = 5,
    ) -> list[PriceCandidate]:
        if len(candidates) != len(candidate_embeddings):
            raise ValueError(
                "Number of candidates must match number of candidate embeddings."
            )

        scores = candidate_embeddings @ lv_embedding

        top_k = min(top_k, len(candidates))
        top_indices = scores.argsort()[::-1][:top_k]

        results: list[PriceCandidate] = []
        for index in top_indices:
            candidate = candidates[index]
            candidate.score = float(scores[index])
            results.append(candidate)

        return results

    @staticmethod
    def filter_by_unit(
        lv_position: LVPosition, candidates: list[PriceCandidate]
    ) -> list[PriceCandidate]:

        return [
            candidate for candidate in candidates if candidate.unit == lv_position.unit
        ]
