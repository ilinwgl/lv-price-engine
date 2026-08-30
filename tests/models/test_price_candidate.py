from decimal import Decimal

from src.models import PriceCandidate


def test_create_price_candidate():
    candidate = PriceCandidate(
        price_id=1,
        category="Beton",
        name="Transportbeton C30/37 XC4",
        description="Transportbeton für Stahlbetonbauteile",
        unit="m³",
        unit_price=Decimal("152.00"),
        supplier="Muster Baustoffe GmbH",
        supplier_location="Frankfurt am Main",
        score=0.9,
    )

    assert candidate.price_id == 1
    assert candidate.unit_price == Decimal("152.00")
    assert candidate.score == 0.9
