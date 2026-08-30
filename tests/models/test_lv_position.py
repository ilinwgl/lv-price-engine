from decimal import Decimal

from src.models import LVPosition


def test_create_lv_position():
    position = LVPosition(
        gaeb_id="AAAAAAAAAAA",
        oz="01.02.0030",
        short_text="Stahlbetonwand C30/37",
        long_text="Beton C30/37 XC4",
        quantity=Decimal("120.00"),
        unit="m³",
    )

    assert position.oz == "01.02.0030"
    assert position.quantity == Decimal("120.00")
    assert position.unit == "m³"
