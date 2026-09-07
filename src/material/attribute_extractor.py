import re
from typing import Any

from src.models.material.attribute_definition import AttributeDefinition
from src.models.material.extracted_material import ExtractedMaterial
from src.models.material.material_template import MaterialTemplate


class AttributeExtractor:
    def extract(
        self,
        text: str,
        template: MaterialTemplate,
    ) -> ExtractedMaterial:
        core_attributes = self._extract_attributes(
            text=text,
            attributes=template.core_attributes,
        )

        supplementary_attributes = self._extract_attributes(
            text=text,
            attributes=template.supplementary_attributes,
        )

        return ExtractedMaterial(
            material_type=template.material_type,
            core_attributes=core_attributes,
            supplementary_attributes=supplementary_attributes,
        )

    def _extract_attributes(
        self,
        text: str,
        attributes: dict[str, AttributeDefinition],
    ) -> dict[str, Any]:
        extracted: dict[str, Any] = {}

        for attribute_name, definition in attributes.items():
            value = self._extract_attribute(
                text=text,
                definition=definition,
            )

            if value is not None:
                extracted[attribute_name] = value

        return extracted

    def _extract_attribute(
        self,
        text: str,
        definition: AttributeDefinition,
    ) -> Any | None:
        match definition.value_type:
            case "single":
                return self._extract_single(text, definition)

            case "multiple":
                return self._extract_multiple(text, definition)

            case "grouped":
                return self._extract_grouped(text, definition)

            case _:
                return None

    @staticmethod
    def _extract_single(
        text: str,
        definition: AttributeDefinition,
    ) -> Any | None:
        matches = [
            value
            for value in definition.values
            if isinstance(value, str)
            and AttributeExtractor._contains_value(text, value)
        ]

        if not matches:
            return None

        if len(matches) > 1:
            matches.sort(key=len, reverse=True)

        return matches[0]

    @staticmethod
    def _extract_multiple(
        text: str,
        definition: AttributeDefinition,
    ) -> tuple[Any, ...] | None:
        matches = tuple(
            value
            for value in definition.values
            if isinstance(value, str)
            and AttributeExtractor._contains_value(text, value)
        )

        if not matches:
            return None

        return matches

    @staticmethod
    def _extract_grouped(
        text: str,
        definition: AttributeDefinition,
    ) -> dict[str, Any] | None:
        extracted_groups: dict[str, Any] = {}

        for group_name, group_data in definition.groups.items():
            if not isinstance(group_data, dict):
                continue

            values = group_data.get("values", [])

            if not isinstance(values, list):
                continue

            matches = [
                value
                for value in values
                if isinstance(value, str)
                and AttributeExtractor._contains_value(text, value)
            ]

            if not matches:
                continue

            if len(matches) > 1:
                matches.sort(key=len, reverse=True)

            extracted_groups[group_name] = matches[0]

        if not extracted_groups:
            return None

        return extracted_groups

    @staticmethod
    def _contains_value(text: str, value: str) -> bool:
        pattern = rf"(?<!\w){re.escape(value)}(?!\w)"
        return re.search(pattern, text) is not None
