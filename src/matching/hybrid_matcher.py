from collections import defaultdict

from src.models.match_result import MatchCandidate


class HybridMatcher:
    @staticmethod
    def fuse(
        vector_candidates: list[MatchCandidate],
        bm25_candidates: list[MatchCandidate],
        top_k: int = 5,
        rrf_k: int = 60,
    ) -> list[MatchCandidate]:
        scores: dict[int, float] = defaultdict(float)
        candidates_by_id = {}

        for rank, match in enumerate(vector_candidates, start=1):
            candidate_id = match.candidate.id

            scores[candidate_id] += 1 / (rrf_k + rank)
            candidates_by_id[candidate_id] = match.candidate

        for rank, match in enumerate(bm25_candidates, start=1):
            candidate_id = match.candidate.id

            scores[candidate_id] += 1 / (rrf_k + rank)
            candidates_by_id[candidate_id] = match.candidate

        sorted_candidates = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            MatchCandidate(
                candidate=candidates_by_id[candidate_id],
                score=score,
            )
            for candidate_id, score in sorted_candidates[:top_k]
        ]
