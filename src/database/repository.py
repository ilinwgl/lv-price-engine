from psycopg import Connection

from src.database.connector import DBConnector
from src.importing.models import (
    ParsedCommodity,
    ParsedCommodityGroup,
    ParsedCommodityPrice,
    ParsedEstimatePrice,
    ParsedProductGroup,
)


class DBRepository:
    def __init__(
        self,
        connector: DBConnector,
        connection: Connection | None = None,
    ) -> None:
        self._connector = connector
        self._connection = connection

    def _get_import_connection(self) -> Connection:
        if self._connection is None:
            raise RuntimeError("Database connection is required for import operations.")

        return self._connection

    def count(self) -> int:
        with self._connector.connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT COUNT(*)
                    FROM public.supplier_prices;
                """
            )

            result = cursor.fetchone()

            if result is None:
                return 0

            return int(result[0])

    def insert_product_group(
        self,
        product_group: ParsedProductGroup,
    ) -> int:
        query = """
            INSERT INTO product_groups (
                code,
                name
            )
            VALUES (%s, %s)
            RETURNING id;
        """

        values = (
            product_group.code,
            product_group.name,
        )

        connection = self._get_import_connection()

        with connection.cursor() as cursor:
            cursor.execute(query, params=values)

            result = cursor.fetchone()

            if result is None:
                raise RuntimeError(f"Insert product group failed: {product_group.code}")

            return int(result[0])

    def insert_commodity_group(
        self,
        group: ParsedCommodityGroup,
        parent_id: int | None,
        product_group_id: int | None,
    ) -> int:
        query = """
            INSERT INTO commodity_groups (
                code,
                description,
                parent_id,
                source_ref,
                cost_code,
                unit,
                discount,
                wastage,
                estimation_factor,
                regie_factor,
                addition_1,
                addition_2,
                addition_3,
                addition_4,
                remarks,
                product_group_id,
                fixed_hours
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s
            )
            RETURNING id;
        """

        values = (
            group.code,
            group.description,
            parent_id,
            group.source_ref,
            group.cost_code,
            group.unit,
            group.discount,
            group.wastage,
            group.estimation_factor,
            group.regie_factor,
            group.addition_1,
            group.addition_2,
            group.addition_3,
            group.addition_4,
            group.remarks,
            product_group_id,
            group.fixed_hours,
        )

        connection = self._get_import_connection()

        with connection.cursor() as cursor:
            cursor.execute(query, params=values)

            result = cursor.fetchone()

            if result is None:
                raise RuntimeError(f"Insert commodity group failed: {group.code}")

            return int(result[0])

    def insert_commodity(
        self,
        commodity: ParsedCommodity,
        commodity_group_id: int,
        product_group_id: int | None,
    ) -> int:
        query = """
            INSERT INTO commodities (
                code,
                description,
                commodity_group_id,
                product_group_id,
                source_ref,
                unit,
                cost_code,
                cost_code_unit,
                weight,
                weight_unit,
                volume,
                volume_unit,
                addition_1,
                addition_2,
                addition_3,
                addition_4,
                remarks,
                external_price_update,
                selected,
                fixed_hours,
                change_date,
                change_user
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s
            )
            RETURNING id;
        """

        values = (
            commodity.code,
            commodity.description,
            commodity_group_id,
            product_group_id,
            commodity.source_ref,
            commodity.unit,
            commodity.cost_code,
            commodity.cost_code_unit,
            commodity.weight,
            commodity.weight_unit,
            commodity.volume,
            commodity.volume_unit,
            commodity.addition_1,
            commodity.addition_2,
            commodity.addition_3,
            commodity.addition_4,
            commodity.remarks,
            commodity.external_price_update,
            commodity.selected,
            commodity.fixed_hours,
            commodity.change_date,
            commodity.change_user,
        )

        connection = self._get_import_connection()

        with connection.cursor() as cursor:
            cursor.execute(query, params=values)

            result = cursor.fetchone()

            if result is None:
                raise RuntimeError(f"Insert commodity failed: {commodity.code}")

            return int(result[0])

    def insert_commodity_price(
        self,
        price: ParsedCommodityPrice,
        commodity_id: int,
    ) -> int:
        query = """
            INSERT INTO commodity_prices (
                commodity_id,
                unit_price,
                currency,
                discount,
                freight_costs,
                miscellaneous,
                wastage,
                modified_date,
                modified_user
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            RETURNING id;
        """

        values = (
            commodity_id,
            price.unit_price,
            price.currency,
            price.discount,
            price.freight_costs,
            price.miscellaneous,
            price.wastage,
            price.modified_date,
            price.modified_user,
        )

        connection = self._get_import_connection()

        with connection.cursor() as cursor:
            cursor.execute(query, params=values)

            result = cursor.fetchone()

            if result is None:
                raise RuntimeError(
                    f"Insert commodity price failed for commodity id: {commodity_id}"
                )

            return int(result[0])

    def insert_estimate_price(
        self,
        price: ParsedEstimatePrice,
        commodity_id: int,
    ) -> int:
        query = """
            INSERT INTO estimate_prices (
                commodity_id,
                price_type,
                factor,
                price,
                currency,
                modified_date,
                modified_user,
                fixed_price
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            RETURNING id;
        """

        values = (
            commodity_id,
            price.price_type,
            price.factor,
            price.price,
            price.currency,
            price.modified_date,
            price.modified_user,
            price.fixed_price,
        )

        connection = self._get_import_connection()

        with connection.cursor() as cursor:
            cursor.execute(query, params=values)

            result = cursor.fetchone()

            if result is None:
                raise RuntimeError(
                    f"Insert estimate price failed for commodity id: {commodity_id}"
                )

            return int(result[0])
