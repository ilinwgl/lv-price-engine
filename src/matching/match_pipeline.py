import logging

from src.fusion.rrf_fusion import RRFFusion
from src.models.commodity_candidate import CommodityCandidate
from src.models.embedding_model import EmbeddingModel
from src.models.lv_position import LVPosition
from src.models.match_result import (
    MatchCandidate,
    MatchStatus,
    PositionMatchResult,
)
from src.models.reranker_model import RerankerModel
from src.ranking.cross_encoder_reranker import BGEReranker
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.vector_retriever import VectorRetriever
from src.text_processing.text_builder import TextBuilder

logger = logging.getLogger(__name__)


class MatchPipeline:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        reranker_model: RerankerModel,
        lv_positions: list[LVPosition],
        candidates: list[CommodityCandidate],
    ) -> None:
        self._lv_positions = lv_positions
        self._candidates = candidates

        self._retrieval_top_k = 20
        self._reranker_top_k = 10
        self._top_k = 5

        # Temporary demo thresholds.
        # These should be calibrated after inspecting reranker scores.
        self._min_score = 0.6
        self._min_gap = 0.02

        self._candidate_texts = [
            TextBuilder.create_candidate_text(candidate) for candidate in candidates
        ]

        self._candidate_texts_by_id = {
            candidate.id: text
            for candidate, text in zip(
                candidates,
                self._candidate_texts,
                strict=True,
            )
        }

        self._vector_retriever = VectorRetriever(
            embedding_model=embedding_model,
            candidates=candidates,
            candidate_texts=self._candidate_texts,
        )

        self._bm25_retriever = BM25Retriever(
            candidates=candidates,
            candidate_texts=self._candidate_texts,
        )

        self._reranker = BGEReranker(
            reranker_model=reranker_model,
        )

    def run(self) -> list[PositionMatchResult]:
        logger.info(
            "Start matching pipeline for %d LV positions",
            len(self._lv_positions),
        )

        match_results: list[PositionMatchResult] = []

        for lv_position in self._lv_positions:
            query_text = TextBuilder.create_lv_position_text(lv_position)

            vector_candidates = self._vector_retriever.retrieve(
                query_text=query_text,
                top_k=self._retrieval_top_k,
            )

            bm25_candidates = self._bm25_retriever.retrieve(
                query_text=query_text,
                top_k=self._retrieval_top_k,
            )

            fused_candidates = RRFFusion.fuse(
                candidate_lists=[
                    vector_candidates,
                    bm25_candidates,
                ],
                top_k=self._reranker_top_k,
            )

            reranker_candidate_texts = [
                self._candidate_texts_by_id[match_candidate.candidate.id]
                for match_candidate in fused_candidates
            ]

            reranked_candidates = self._reranker.rerank(
                query_text=query_text,
                candidate_texts=reranker_candidate_texts,
                candidates=fused_candidates,
                top_k=self._top_k,
            )

            matched_status, matched_candidates = self._post_process_match_results(
                reranked_candidates
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
        matched_candidates: list[MatchCandidate],
    ) -> tuple[MatchStatus, list[MatchCandidate]]:
        if not matched_candidates:
            return MatchStatus.UNMATCHED, []

        top1 = matched_candidates[0]

        if top1.score < self._min_score:
            return MatchStatus.UNMATCHED, []

        if len(matched_candidates) == 1:
            return MatchStatus.AUTO_MATCHED, [top1]

        score_gap = top1.score - matched_candidates[1].score

        if score_gap >= self._min_gap:
            return MatchStatus.AUTO_MATCHED, [top1]

        return (
            MatchStatus.REVIEW_REQUIRED,
            matched_candidates[:3],
        )
