from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass
class CommodityPrice:
    id: int
    unit_price: Decimal
    currency: str

    discount: Decimal | None = None
    freight_costs: Decimal | None = None
    miscellaneous: Decimal | None = None
    wastage: Decimal | None = None

    modified_date: date | None = None
    modified_user: str | None = None


@dataclass
class EstimatePrice:
    id: int
    price_type: str
    price: Decimal
    currency: str

    factor: Decimal | None = None
    modified_date: date | None = None
    modified_user: str | None = None
    fixed_price: bool | None = None


@dataclass
class CommodityCandidate:
    id: int
    code: str
    description: str | None
    unit: str | None
    category_path: str

    commodity_prices: list[CommodityPrice] = field(default_factory=list)
    estimate_prices: list[EstimatePrice] = field(default_factory=list)
