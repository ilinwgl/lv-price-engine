from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AttributeDefinition:
    name: str
    value_type: str
    values: tuple[Any, ...] = field(default_factory=tuple)
    unit: str | None = None
    groups: dict[str, Any] = field(default_factory=dict)
