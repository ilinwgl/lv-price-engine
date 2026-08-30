from dataclasses import dataclass
from enum import Enum

from src.models.commodity_candidate import CommodityCandidate
from src.models.lv_position import LVPosition


class MatchStatus(str, Enum):
    UNMATCHED = "unmatched"
    AUTO_MATCHED = "auto_matched"
    REVIEW_REQUIRED = "review_required"


@dataclass
class MatchCandidate:
    candidate: CommodityCandidate
    score: float


@dataclass
class PositionMatchResult:
    lv_position: LVPosition
    match_status: MatchStatus
    matched_candidates: list[MatchCandidate]
