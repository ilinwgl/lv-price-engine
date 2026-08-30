from src.models.inference_model.reranker_model import RerankerModel
from src.models.results.match_result import MatchCandidate
from src.ranking.base_reranker import BaseReranker


class BGEReranker(BaseReranker):
    def __init__(
        self,
        reranker_model: RerankerModel,
    ) -> None:
        self._reranker_model = reranker_model

    def rerank(
        self,
        query_text: str,
        candidate_texts: list[str],
        candidates: list[MatchCandidate],
        top_k: int,
    ) -> list[MatchCandidate]:
        if len(candidates) != len(candidate_texts):
            raise ValueError(
                "Number of candidates must match number of candidate texts."
            )

        if not candidates:
            return []

        pairs = [[query_text, candidate_text] for candidate_text in candidate_texts]

        scores = self._reranker_model.model.predict(pairs)

        results: list[MatchCandidate] = []

        for match_candidate, score in zip(
            candidates,
            scores,
            strict=True,
        ):
            results.append(
                MatchCandidate(
                    candidate=match_candidate.candidate,
                    score=float(score),
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]
