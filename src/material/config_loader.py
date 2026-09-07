from pathlib import Path
from typing import Any

import yaml

from src.models.material.attribute_definition import AttributeDefinition
from src.models.material.keyword import MaterialKeyword
from src.models.material.keyword_level import KeywordLevel
from src.models.material.material_template import MaterialTemplate


class MaterialConfigLoader:
    def __init__(self, registry_path: Path) -> None:
        self._registry_path = registry_path
        self._config_root = registry_path.parent.parent

    def load_all(self) -> dict[str, MaterialTemplate]:
        registry_data = self._load_yaml(self._registry_path)

        materials = registry_data.get("materials")

        if not isinstance(materials, dict):
            raise TypeError(
                "Invalid materials registry: "
                f"expected 'materials' to be dict, "
                f"got {type(materials).__name__}"
            )

        templates: dict[str, MaterialTemplate] = {}

        for material_type, template_path in materials.items():
            if not isinstance(material_type, str):
                raise TypeError(
                    "Invalid material type in registry: "
                    f"expected str, got {type(material_type).__name__}"
                )

            if not isinstance(template_path, str):
                raise TypeError(
                    f"Invalid template path for '{material_type}': "
                    f"expected str, got {type(template_path).__name__}"
                )

            path = self._config_root / template_path

            templates[material_type] = self._load_template(path)

        return templates

    def _load_template(self, path: Path) -> MaterialTemplate:
        data = self._load_yaml(path)

        material_type = data.get("material_type")
        if not isinstance(material_type, str):
            raise TypeError(
                f"Invalid material_type in {path}: "
                f"expected str, got {type(material_type).__name__}"
            )

        keywords = self._load_keywords(
            data.get("keywords", []),
            path,
        )

        material_dir = path.parent
        core_attributes = self._load_attributes(
            material_dir / "core_attributes",
            data.get("core_attributes", []),
        )

        supplementary_attributes = self._load_attributes(
            material_dir / "supplementary_attributes",
            data.get("supplementary_attributes", []),
        )

        return MaterialTemplate(
            material_type=material_type,
            keywords=keywords,
            core_attributes=core_attributes,
            supplementary_attributes=supplementary_attributes,
        )

    def _load_keywords(
        self,
        keyword_data: list[Any],
        template_path: Path,
    ) -> tuple[MaterialKeyword, ...]:
        if not isinstance(keyword_data, list):
            raise TypeError(
                f"Invalid keywords config in {template_path}: "
                f"expected list, got {type(keyword_data).__name__}"
            )

        keywords: list[MaterialKeyword] = []

        for item in keyword_data:
            if not isinstance(item, dict):
                raise TypeError(
                    f"Invalid keyword config in {template_path}: "
                    f"expected dict, got {type(item).__name__}"
                )

            value = item.get("value")
            level = item.get("level")

            if not isinstance(value, str):
                raise TypeError(
                    f"Invalid keyword value in {template_path}: "
                    f"expected str, got {type(value).__name__}"
                )

            if not isinstance(level, str):
                raise TypeError(
                    f"Invalid keyword level in {template_path}: "
                    f"expected str, got {type(level).__name__}"
                )

            try:
                keyword_level = KeywordLevel[level.upper()]
            except KeyError as exc:
                raise ValueError(
                    f"Invalid keyword level '{level}' in {template_path}"
                ) from exc

            keywords.append(
                MaterialKeyword(
                    value=value,
                    level=keyword_level,
                )
            )

        return tuple(keywords)

    def _load_attributes(
        self,
        directory: Path,
        attribute_names: list[str],
    ) -> dict[str, AttributeDefinition]:
        if not isinstance(attribute_names, list):
            raise TypeError(
                f"Invalid attribute list for {directory}: "
                f"expected list, got {type(attribute_names).__name__}"
            )

        attributes: dict[str, AttributeDefinition] = {}

        for attribute_name in attribute_names:
            if not isinstance(attribute_name, str):
                raise TypeError(
                    f"Invalid attribute name in {directory}: "
                    f"expected str, got {type(attribute_name).__name__}"
                )

            path = directory / f"{attribute_name}.yaml"
            data = self._load_yaml(path)

            configured_name = data["name"]
            if not isinstance(configured_name, str):
                raise TypeError(
                    f"Invalid attribute name in {path}: "
                    f"expected str, got {type(configured_name).__name__}"
                )

            if configured_name != attribute_name:
                raise ValueError(
                    "Attribute name mismatch: "
                    f"template expects '{attribute_name}', "
                    f"but {path} defines '{configured_name}'"
                )

            values = data.get("values", [])
            if not isinstance(values, list):
                raise TypeError(
                    f"Invalid values in {path}: "
                    f"expected list, got {type(values).__name__}"
                )

            groups = data.get("groups", {})
            if not isinstance(groups, dict):
                raise TypeError(
                    f"Invalid groups in {path}: "
                    f"expected dict, got {type(groups).__name__}"
                )

            attributes[attribute_name] = AttributeDefinition(
                name=configured_name,
                value_type=data["type"],
                values=tuple(values),
                unit=data.get("unit"),
                groups=groups,
            )

        return attributes

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            raise TypeError(f"Invalid YAML config: {path}")

        return data
