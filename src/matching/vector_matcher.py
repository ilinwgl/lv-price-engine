import logging

import torch

from src.models.commodity_candidate import CommodityCandidate
from src.models.match_result import MatchCandidate

logger = logging.getLogger(__name__)


class VectorMatcher:
    @staticmethod
    def match(
        lv_embedding: torch.Tensor,
        candidate_embeddings: torch.Tensor,
        candidates: list[CommodityCandidate],
        top_k: int = 5,
    ) -> list[MatchCandidate]:
        if len(candidates) != len(candidate_embeddings):
            raise ValueError(
                "Number of candidates must match number of candidate embeddings."
            )

        scores = candidate_embeddings @ lv_embedding

        top_k = min(top_k, len(candidates))
        top_indices = scores.argsort(descending=True)[:top_k]

        results: list[MatchCandidate] = []
        for index in top_indices:
            results.append(
                MatchCandidate(candidate=candidates[index], score=float(scores[index]))
            )

        return results
