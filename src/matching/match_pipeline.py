import logging
from collections import defaultdict

import torch

from src.matching.text_builder import TextBuilder
from src.matching.vector_matcher import VectorMatcher
from src.models.embedding_model import EmbeddingModel
from src.models.lv_position import LVPosition
from src.models.match_result import MatchStatus, PositionMatchResult
from src.models.price_candidate import PriceCandidate

logger = logging.getLogger(__name__)


class MatchPipeline:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        lv_positions: list[LVPosition],
        candidates: list[PriceCandidate],
    ):
        self._embedding_model = embedding_model
        self._lv_positions = lv_positions
        self._candidates = candidates
        self._top_k = 5
        self._min_score = 0.6
        self._min_gap = 0.1

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
            "Create embeddings for %d price candidates",
            len(candidate_texts),
        )

        candidate_embeddings = self._embedding_model.model.encode(
            inputs=candidate_texts,
            batch_size=16,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        candidates_by_unit = defaultdict(list)
        for candidate, embedding in zip(
            self._candidates,
            candidate_embeddings,
            strict=True,
        ):
            candidates_by_unit[candidate.unit].append((candidate, embedding))

        logger.info(
            "Candidates grouped into %d units",
            len(candidates_by_unit),
        )

        match_results: list[PositionMatchResult] = []
        for lv_position in self._lv_positions:
            unit_candidates = candidates_by_unit.get(
                lv_position.unit,
                [],
            )

            if not unit_candidates:
                logger.warning(
                    "%s | no candidates for unit '%s'",
                    lv_position.oz,
                    lv_position.unit,
                )

                match_results.append(
                    PositionMatchResult(
                        lv_position=lv_position,
                        match_status=MatchStatus.UNMATCHED,
                        matched_candidates=[],
                    )
                )
                continue

            selected_candidates = [candidate for candidate, _ in unit_candidates]

            selected_embeddings = torch.stack(
                [torch.as_tensor(embedding) for _, embedding in unit_candidates]
            )

            lv_text = TextBuilder.create_lv_position_text(lv_position)
            lv_embedding = self._embedding_model.model.encode(lv_text)

            matched_candidates = VectorMatcher.match(
                lv_embedding, selected_embeddings, selected_candidates, self._top_k
            )
            matched_status, matched_candidates = self._post_process_match_results(
                matched_candidates
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
        matched_candidates: list[PriceCandidate],
    ) -> tuple[MatchStatus, list[PriceCandidate]]:
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

        return MatchStatus.REVIEW_REQUIRED, matched_candidates[:3]
