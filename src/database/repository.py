from psycopg import Connection

from src.database.connector import DBConnector
from src.db_article_importing.db_article_models import (
    ParsedCommodity,
    ParsedCommodityGroup,
    ParsedCommodityPrice,
    ParsedEstimatePrice,
    ParsedProductGroup,
)
from src.models.database_candidate.commodity_candidate import (
    CommodityCandidate,
    CommodityPrice,
    EstimatePrice,
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

    def read_all_commodity_candidates(self) -> list[CommodityCandidate]:
        candidates: dict[int, CommodityCandidate] = {}

        with self._connector.connect() as conn, conn.cursor() as cursor:
            # ---------------------------------------------------------------------
            # Commodities + complete commodity group hierarchy
            # ---------------------------------------------------------------------

            cursor.execute(
                """
                WITH RECURSIVE group_paths AS (
                    SELECT
                        id,
                        parent_id,
                        description,
                        COALESCE(description, '') AS category_path
                    FROM commodity_groups
                    WHERE parent_id IS NULL

                    UNION ALL

                    SELECT
                        child.id,
                        child.parent_id,
                        child.description,
                        CONCAT_WS(
                            ' | ',
                            NULLIF(parent.category_path, ''),
                            child.description
                        ) AS category_path
                    FROM commodity_groups AS child
                    INNER JOIN group_paths AS parent
                        ON child.parent_id = parent.id
                )
                SELECT
                    commodity.id,
                    commodity.code,
                    commodity.description,
                    commodity.unit,
                    TRIM(
                        CONCAT_WS(
                            ' | ',
                            NULLIF(group_paths.category_path, ''),
                            commodity.description
                        )
                    ) AS matching_text
                FROM commodities AS commodity
                LEFT JOIN group_paths
                    ON group_paths.id = commodity.commodity_group_id
                ORDER BY commodity.id;
                """
            )

            rows = cursor.fetchall()

            for row in rows:
                commodity_id = int(row[0])

                candidates[commodity_id] = CommodityCandidate(
                    id=commodity_id,
                    code=row[1],
                    description=row[2],
                    unit=row[3],
                    category_path=row[4] or "",
                )

            # ---------------------------------------------------------------------
            # Commodity Prices
            # ---------------------------------------------------------------------

            cursor.execute(
                """
                SELECT
                    id,
                    commodity_id,
                    unit_price,
                    currency,
                    discount,
                    freight_costs,
                    miscellaneous,
                    wastage,
                    modified_date,
                    modified_user
                FROM commodity_prices
                ORDER BY commodity_id, id;
                """
            )

            rows = cursor.fetchall()

            for row in rows:
                commodity_id = int(row[1])

                candidate = candidates.get(commodity_id)
                if candidate is None:
                    continue

                price = CommodityPrice(
                    id=int(row[0]),
                    unit_price=row[2],
                    currency=row[3],
                    discount=row[4],
                    freight_costs=row[5],
                    miscellaneous=row[6],
                    wastage=row[7],
                    modified_date=row[8],
                    modified_user=row[9],
                )

                candidate.commodity_prices.append(price)

            # ---------------------------------------------------------------------
            # Estimate Prices
            # ---------------------------------------------------------------------

            cursor.execute(
                """
                SELECT
                    id,
                    commodity_id,
                    price_type,
                    factor,
                    price,
                    currency,
                    modified_date,
                    modified_user,
                    fixed_price
                FROM estimate_prices
                ORDER BY commodity_id, id;
                """
            )

            rows = cursor.fetchall()

            for row in rows:
                commodity_id = int(row[1])

                candidate = candidates.get(commodity_id)
                if candidate is None:
                    continue

                price = EstimatePrice(
                    id=int(row[0]),
                    price_type=row[2],
                    factor=row[3],
                    price=row[4],
                    currency=row[5],
                    modified_date=row[6],
                    modified_user=row[7],
                    fixed_price=row[8],
                )

                candidate.estimate_prices.append(price)

        return list(candidates.values())
