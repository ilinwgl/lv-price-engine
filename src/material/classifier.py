from collections import defaultdict
from dataclasses import dataclass

from src.material.registry import MaterialRegistry
from src.models.material.keyword import MaterialKeyword


@dataclass(frozen=True)
class KeywordMatch:
    material_type: str
    keyword: MaterialKeyword
    start: int
    end: int


class MaterialClassifier:
    def __init__(self, registry: MaterialRegistry) -> None:
        self._registry = registry

    def classify(self, text: str) -> str | None:
        scores = self.score(text)

        if not scores:
            return None

        max_score = max(scores.values())

        best_materials = [
            material_type
            for material_type, score in scores.items()
            if score == max_score
        ]

        if len(best_materials) != 1:
            return None

        return best_materials[0]

    def score(self, text: str) -> dict[str, int]:
        matches = self._find_matches(text)
        filtered_matches = self._remove_contained_matches(matches)

        scores: dict[str, int] = defaultdict(int)

        for match in filtered_matches:
            scores[match.material_type] += int(match.keyword.level)

        return dict(scores)

    def _find_matches(self, text: str) -> list[KeywordMatch]:
        matches: list[KeywordMatch] = []

        normalized_text = text.casefold()

        for template in self._registry.get_all():
            for keyword in template.keywords:
                normalized_keyword = keyword.value.casefold()

                start = 0

                while True:
                    index = normalized_text.find(
                        normalized_keyword,
                        start,
                    )

                    if index == -1:
                        break

                    matches.append(
                        KeywordMatch(
                            material_type=template.material_type,
                            keyword=keyword,
                            start=index,
                            end=index + len(normalized_keyword),
                        )
                    )

                    start = index + len(normalized_keyword)

        return matches

    @staticmethod
    def _remove_contained_matches(
        matches: list[KeywordMatch],
    ) -> list[KeywordMatch]:
        filtered_matches: list[KeywordMatch] = []

        for match in matches:
            is_contained = any(
                other.start <= match.start
                and other.end >= match.end
                and (other.start < match.start or other.end > match.end)
                for other in matches
            )

            if not is_contained:
                filtered_matches.append(match)

        return filtered_matches
