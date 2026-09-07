from dataclasses import dataclass
from decimal import Decimal


@dataclass
class LVPosition:
    gaeb_id: str
    oz: str
    short_text: str
    long_text: str
    quantity: Decimal
    unit: str
