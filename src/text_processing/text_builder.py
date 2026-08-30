from src.models.database_candidate.commodity_candidate import CommodityCandidate
from src.models.lv_position.lv_position import LVPosition


class TextBuilder:
    @staticmethod
    def create_lv_position_text(lv_position: LVPosition) -> str:
        return TextBuilder._join_text_parts(
            lv_position.short_text, lv_position.long_text, f"Unit: {lv_position.unit}"
        )

    @staticmethod
    def create_candidate_text(candidate: CommodityCandidate) -> str:
        return TextBuilder._join_text_parts(
            candidate.category_path,
            candidate.code,
            candidate.description,
            f"Unit: {candidate.unit}",
        )

    @staticmethod
    def _join_text_parts(*parts: str | None) -> str:
        return " | ".join(part.strip() for part in parts if part and part.strip())
