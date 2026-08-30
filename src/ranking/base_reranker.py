from abc import ABC, abstractmethod

from src.models.results.match_result import MatchCandidate


class BaseReranker(ABC):
    @abstractmethod
    def rerank(
        self,
        query_text: str,
        candidate_texts: list[str],
        candidates: list[MatchCandidate],
        top_k: int,
    ) -> list[MatchCandidate]:
        pass
