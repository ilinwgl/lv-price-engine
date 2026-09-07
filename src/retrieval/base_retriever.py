from abc import ABC, abstractmethod

from src.models.results.match_result import MatchCandidate


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(
        self,
        query_text: str,
        top_k: int,
    ) -> list[MatchCandidate]:
        pass
