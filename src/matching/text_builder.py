from src.models.lv_position import LVPosition
from src.models.price_candidate import PriceCandidate


class TextBuilder:
    @staticmethod
    def create_lv_position_text(lv_position: LVPosition) -> str:
        return f"{lv_position.short_text}. {lv_position.long_text}"

    @staticmethod
    def create_candidate_text(candidate: PriceCandidate) -> str:
        return f"{candidate.name}. {candidate.description}"
