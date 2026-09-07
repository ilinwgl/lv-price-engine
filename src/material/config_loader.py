from pathlib import Path
from typing import Any

import yaml

from src.models.material.attribute_definition import AttributeDefinition
from src.models.material.material_template import MaterialTemplate


class MaterialConfigLoader:
    def __init__(self, registry_path: Path) -> None:
        self._registry_path = registry_path
        self._config_root = registry_path.parent.parent

    def load_all(self) -> dict[str, MaterialTemplate]:
        registry_data = self._load_yaml(self._registry_path)

        materials = registry_data["materials"]

        templates: dict[str, MaterialTemplate] = {}

        for material_type, template_path in materials.items():
            path = self._config_root / template_path

            templates[material_type] = self._load_template(path)

        return templates

    def _load_template(self, path: Path) -> MaterialTemplate:
        data = self._load_yaml(path)

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
            material_type=data["material_type"],
            keywords=tuple(data.get("keywords", [])),
            core_attributes=core_attributes,
            supplementary_attributes=supplementary_attributes,
        )

    def _load_attributes(
        self,
        directory: Path,
        attribute_names: list[str],
    ) -> dict[str, AttributeDefinition]:
        attributes: dict[str, AttributeDefinition] = {}

        for attribute_name in attribute_names:
            path = directory / f"{attribute_name}.yaml"
            data = self._load_yaml(path)

            attributes[attribute_name] = AttributeDefinition(
                name=data["name"],
                value_type=data["type"],
                values=tuple(data.get("values", [])),
                unit=data.get("unit"),
                groups=data.get("groups", {}),
            )

        return attributes

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            raise TypeError(f"Invalid YAML config: {path}")

        return data
