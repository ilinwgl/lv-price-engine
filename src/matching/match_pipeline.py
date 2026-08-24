import logging

import torch

from src.matching.bm25_matcher import BM25Matcher
from src.matching.hybrid_matcher import HybridMatcher
from src.matching.text_builder import TextBuilder
from src.matching.vector_matcher import VectorMatcher
from src.models.commodity_candidate import CommodityCandidate
from src.models.embedding_model import EmbeddingModel
from src.models.lv_position import LVPosition
from src.models.match_result import MatchCandidate, MatchStatus, PositionMatchResult

logger = logging.getLogger(__name__)


class MatchPipeline:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        lv_positions: list[LVPosition],
        candidates: list[CommodityCandidate],
    ):
        self._embedding_model = embedding_model
        self._lv_positions = lv_positions
        self._candidates = candidates
        self._retrieval_top_k = 20
        self._top_k = 5
        self._min_score = 0.6
        self._min_rrf_gap = 0.001

    def run(self) -> list[PositionMatchResult]:
        logger.info(
            "Start matching pipeline with model '%s'",
            self._embedding_model.name,
        )

        candidate_texts = [
            TextBuilder.create_candidate_text(candidate)
            for candidate in self._candidates
        ]

        logger.info(
            "Create embeddings for %d commodity candidates",
            len(candidate_texts),
        )

        candidate_embeddings = self._embedding_model.model.encode(
            inputs=candidate_texts,
            batch_size=16,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        candidate_embeddings = torch.as_tensor(candidate_embeddings)

        match_results: list[PositionMatchResult] = []

        for lv_position in self._lv_positions:
            lv_text = TextBuilder.create_lv_position_text(lv_position)

            lv_embedding = self._embedding_model.model.encode(
                inputs=lv_text,
                normalize_embeddings=True,
            )

            lv_embedding = torch.as_tensor(lv_embedding)

            vector_matched_candidates = VectorMatcher.match(
                lv_embedding=lv_embedding,
                candidate_embeddings=candidate_embeddings,
                candidates=self._candidates,
                top_k=self._retrieval_top_k,
            )

            bm25_matched_candidates = BM25Matcher.match(
                lv_text=lv_text,
                candidate_texts=candidate_texts,
                candidates=self._candidates,
                top_k=self._top_k,
            )

            hybrid_matched_candidates = HybridMatcher.fuse(
                vector_candidates=vector_matched_candidates,
                bm25_candidates=bm25_matched_candidates,
                top_k=self._top_k,
            )

            matched_status, matched_candidates = self._post_process_match_results(
                vector_candidates=vector_matched_candidates,
                bm25_candidates=bm25_matched_candidates,
                fused_candidates=hybrid_matched_candidates,
            )

            logger.info(
                "%s | %s | %d result(s)",
                lv_position.oz,
                matched_status.value,
                len(matched_candidates),
            )

            match_results.append(
                PositionMatchResult(
                    lv_position=lv_position,
                    match_status=matched_status,
                    matched_candidates=matched_candidates,
                )
            )

        logger.info(
            "Matching pipeline finished: %d positions processed",
            len(match_results),
        )

        return match_results

    def _post_process_match_results(
        self,
        vector_candidates: list[MatchCandidate],
        bm25_candidates: list[MatchCandidate],
        fused_candidates: list[MatchCandidate],
    ) -> tuple[MatchStatus, list[MatchCandidate]]:
        if not vector_candidates or not bm25_candidates or not fused_candidates:
            return MatchStatus.UNMATCHED, []

        vector_top1 = vector_candidates[0]
        bm25_top1 = bm25_candidates[0]
        fused_top1 = fused_candidates[0]

        if vector_top1.score < self._min_score:
            return MatchStatus.UNMATCHED, []

        same_top1 = vector_top1.candidate.id == bm25_top1.candidate.id

        # Both matchers agree on the same best candidate.
        if same_top1:
            if len(fused_candidates) == 1:
                return MatchStatus.AUTO_MATCHED, [fused_top1]

            score_gap = fused_top1.score - fused_candidates[1].score

            if score_gap >= self._min_rrf_gap:
                return MatchStatus.AUTO_MATCHED, [fused_top1]

            return (
                MatchStatus.REVIEW_REQUIRED,
                fused_candidates[:3],
            )

        # The two matchers disagree.
        # If even the vector similarity is weak, treat it as unmatched.
        if vector_top1.score < self._min_score:
            return MatchStatus.UNMATCHED, []

        return (
            MatchStatus.REVIEW_REQUIRED,
            fused_candidates[:3],
        )
