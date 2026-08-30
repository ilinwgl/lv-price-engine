import re

from rank_bm25 import BM25Okapi

from src.models.database_candidate.commodity_candidate import CommodityCandidate
from src.models.results.match_result import MatchCandidate
from src.retrieval.base_retriever import BaseRetriever


class BM25Retriever(BaseRetriever):
    def __init__(
        self,
        candidates: list[CommodityCandidate],
        candidate_texts: list[str],
    ) -> None:
        if len(candidates) != len(candidate_texts):
            raise ValueError(
                "Number of candidates must match number of candidate texts."
            )

        self._candidates = candidates

        tokenized_candidates = [self._tokenize(text) for text in candidate_texts]

        self._bm25 = BM25Okapi(tokenized_candidates)

    def retrieve(
        self,
        query_text: str,
        top_k: int,
    ) -> list[MatchCandidate]:
        if not self._candidates:
            return []

        tokenized_query = self._tokenize(query_text)

        scores = self._bm25.get_scores(tokenized_query)

        top_k = min(
            top_k,
            len(self._candidates),
        )

        top_indices = scores.argsort()[::-1][:top_k]

        results: list[MatchCandidate] = []

        for index in top_indices:
            results.append(
                MatchCandidate(
                    candidate=self._candidates[index],
                    score=float(scores[index]),
                )
            )

        return results

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(
            r"[A-Za-zÄÖÜäöüß0-9]+(?:[/.-][A-Za-zÄÖÜäöüß0-9]+)*",
            text.lower(),
        )
