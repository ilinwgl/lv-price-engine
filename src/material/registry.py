from src.models.material.material_template import MaterialTemplate


class MaterialRegistry:
    def __init__(
        self,
        templates: dict[str, MaterialTemplate],
    ) -> None:
        self._validate_templates(templates)
        self._templates = templates

    def get(self, material_type: str) -> MaterialTemplate:
        return self._templates[material_type]

    def get_all(self) -> tuple[MaterialTemplate, ...]:
        return tuple(self._templates.values())

    def get_material_types(self) -> tuple[str, ...]:
        return tuple(self._templates.keys())

    @staticmethod
    def _validate_templates(
        templates: dict[str, MaterialTemplate],
    ) -> None:
        for material_type, template in templates.items():
            if not material_type:
                raise ValueError("Material type must not be empty")

            if material_type != template.material_type:
                raise ValueError(
                    "Material type mismatch: "
                    f"registry key='{material_type}', "
                    f"template.material_type='{template.material_type}'"
                )
