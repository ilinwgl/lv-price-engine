from collections import defaultdict

from src.models.match_result import MatchCandidate


class RRFFusion:
    @staticmethod
    def fuse(
        candidate_lists: list[list[MatchCandidate]],
        top_k: int = 5,
        rrf_k: int = 60,
    ) -> list[MatchCandidate]:
        scores: dict[int, float] = defaultdict(float)
        candidates_by_id = {}

        for candidates in candidate_lists:
            for rank, match_candidate in enumerate(
                candidates,
                start=1,
            ):
                candidate_id = match_candidate.candidate.id

                scores[candidate_id] += 1 / (rrf_k + rank)

                candidates_by_id[candidate_id] = match_candidate.candidate

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
