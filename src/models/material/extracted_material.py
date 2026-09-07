from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExtractedMaterial:
    material_type: str
    core_attributes: dict[str, Any] = field(default_factory=dict)
    supplementary_attributes: dict[str, Any] = field(default_factory=dict)
