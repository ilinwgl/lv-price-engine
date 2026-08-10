from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from src.database.repository import DBRepository


class TestDBRepository:
    def test_count(self) -> None:
        connector = MagicMock()
        connection = MagicMock()
        cursor = MagicMock()

        connector.connect.return_value.__enter__.return_value = connection
        connection.cursor.return_value.__enter__.return_value = cursor

        cursor.fetchone.return_value = (5,)

        repository = DBRepository(connector)

        result = repository.count()

        assert result == 5
        cursor.execute.assert_called_once()

    def test_insert(self) -> None:
        connector = MagicMock()
        connection = MagicMock()
        cursor = MagicMock()

        connector.connect.return_value.__enter__.return_value = connection
        connection.cursor.return_value.__enter__.return_value = cursor

        repository = DBRepository(connector)

        repository.insert(
            category="Beton",
            name="Transportbeton C30/37",
            description=(
                "Transportbeton C30/37, Expositionsklasse XC4, Konsistenzklasse F3."
            ),
            unit="m³",
            unit_price=Decimal("128.50"),
            supplier="Muster Beton GmbH",
            supplier_location="Frankfurt am Main",
            valid_from=date(2026, 1, 1),
            valid_to=date(2026, 12, 31),
        )

        cursor.execute.assert_called_once()

        _, parameters = cursor.execute.call_args.args

        assert parameters == (
            "Beton",
            "Transportbeton C30/37",
            ("Transportbeton C30/37, Expositionsklasse XC4, Konsistenzklasse F3."),
            "m³",
            Decimal("128.50"),
            "Muster Beton GmbH",
            "Frankfurt am Main",
            date(2026, 1, 1),
            date(2026, 12, 31),
        )
