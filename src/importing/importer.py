from src.database.repository import DBRepository
from src.importing.models import ParsedArticleData


class ArticleImporter:
    def __init__(self, repository: DBRepository):
        self._repository = repository

    def import_data(self, data: ParsedArticleData) -> None:
        product_group_id_map = self._import_product_groups(data)
        commodity_group_id_map = self._import_commodity_groups(
            data,
            product_group_id_map,
        )
        commodity_id_map = self._import_commodities(
            data,
            product_group_id_map,
            commodity_group_id_map,
        )

        self._import_prices(
            data,
            commodity_id_map,
        )

    def _import_product_groups(
        self,
        data: ParsedArticleData,
    ) -> dict[str, int]:
        id_map: dict[str, int] = {}

        for product_group in data.product_groups:
            db_id = self._repository.insert_product_group(product_group)

            id_map[product_group.code] = db_id

        return id_map

    def _import_commodity_groups(
        self,
        data: ParsedArticleData,
        product_group_id_map: dict[str, int],
    ) -> dict[str, int]:
        id_map: dict[str, int] = {}

        for group in data.commodity_groups:
            parent_id = None

            if group.parent_code is not None:
                parent_id = id_map.get(group.parent_code)

                if parent_id is None:
                    raise ValueError(
                        f"Parent commodity group not found: {group.parent_code}"
                    )

            product_group_id = None

            if group.product_group_code is not None:
                product_group_id = product_group_id_map.get(group.product_group_code)

            db_id = self._repository.insert_commodity_group(
                group=group,
                parent_id=parent_id,
                product_group_id=product_group_id,
            )

            id_map[group.code] = db_id

        return id_map

    def _import_commodities(
        self,
        data: ParsedArticleData,
        product_group_id_map: dict[str, int],
        commodity_group_id_map: dict[str, int],
    ) -> dict[str, int]:
        id_map: dict[str, int] = {}

        for commodity in data.commodities:
            commodity_group_id = commodity_group_id_map.get(
                commodity.commodity_group_code
            )

            if commodity_group_id is None:
                raise ValueError(
                    "Commodity group not found for commodity "
                    f"{commodity.code}: "
                    f"{commodity.commodity_group_code}"
                )

            product_group_id = None

            if commodity.product_group_code is not None:
                product_group_id = product_group_id_map.get(
                    commodity.product_group_code
                )

            db_id = self._repository.insert_commodity(
                commodity=commodity,
                commodity_group_id=commodity_group_id,
                product_group_id=product_group_id,
            )

            id_map[commodity.code] = db_id

        return id_map

    def _import_prices(
        self,
        data: ParsedArticleData,
        commodity_id_map: dict[str, int],
    ) -> None:
        for commodity in data.commodities:
            commodity_id = commodity_id_map.get(commodity.code)

            if commodity_id is None:
                raise ValueError(f"Commodity not found after insert: {commodity.code}")

            for price in commodity.prices:
                self._repository.insert_commodity_price(
                    price=price,
                    commodity_id=commodity_id,
                )

            for estimate_price in commodity.estimate_prices:
                self._repository.insert_estimate_price(
                    price=estimate_price,
                    commodity_id=commodity_id,
                )
