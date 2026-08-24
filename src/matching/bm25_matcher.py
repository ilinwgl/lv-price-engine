import logging
import re

from rank_bm25 import BM25Okapi

from src.models.commodity_candidate import CommodityCandidate
from src.models.match_result import MatchCandidate

logger = logging.getLogger(__name__)


class BM25Matcher:
    @staticmethod
    def match(
        lv_text: str,
        candidate_texts: list[str],
        candidates: list[CommodityCandidate],
        top_k: int = 5,
    ) -> list[MatchCandidate]:
        if len(candidates) != len(candidate_texts):
            raise ValueError(
                "Number of candidates must match number of candidate texts."
            )

        tokenized_candidates = [BM25Matcher._tokenize(text) for text in candidate_texts]

        tokenized_lv_text = BM25Matcher._tokenize(lv_text)

        bm25 = BM25Okapi(tokenized_candidates)

        scores = bm25.get_scores(tokenized_lv_text)

        top_k = min(top_k, len(candidates))
        top_indices = scores.argsort()[::-1][:top_k]

        results: list[MatchCandidate] = []

        for index in top_indices:
            results.append(
                MatchCandidate(
                    candidate=candidates[index],
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
