from dataclasses import dataclass

from src.models.material.keyword_level import KeywordLevel


@dataclass(frozen=True)
class MaterialKeyword:
    value: str
    level: KeywordLevel
