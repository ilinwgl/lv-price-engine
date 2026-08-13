from datetime import date
from decimal import Decimal

from src.database.connector import DBConnector
from src.models.price_candidate import PriceCandidate


class DBRepository:
    def __init__(self, connector: DBConnector) -> None:
        self._connector = connector

    def count(self) -> int:
        with self._connector.connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT COUNT(*)
                    FROM public.supplier_prices;
                    """
            )

            result = cursor.fetchone()

            return result[0]  # type: ignore

    def read_all_data(self) -> list[PriceCandidate]:
        all_data: list[PriceCandidate] = []
        with self._connector.connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT 
                        id,
                        category,
                        name,
                        description,
                        unit,
                        unit_price,
                        supplier,
                        supplier_location
                    FROM public.supplier_prices;
                    """
            )
            result = cursor.fetchall()

        all_data = [
            PriceCandidate(
                price_id=res[0],
                category=res[1],
                name=res[2],
                description=res[3],
                unit=res[4],
                unit_price=res[5],
                supplier=res[6],
                supplier_location=res[7],
            )
            for res in result
        ]
        return all_data

    def insert(
        self,
        category: str,
        name: str,
        description: str,
        unit: str,
        unit_price: Decimal,
        supplier: str | None = None,
        supplier_location: str | None = None,
        valid_from: date | None = None,
        valid_to: date | None = None,
    ) -> None:
        with self._connector.connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO public.supplier_prices (
                    category,
                    name,
                    description,
                    unit,
                    unit_price,
                    supplier,
                    supplier_location,
                    valid_from,
                    valid_to
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                );
                """,
                (
                    category,
                    name,
                    description,
                    unit,
                    unit_price,
                    supplier,
                    supplier_location,
                    valid_from,
                    valid_to,
                ),
            )
