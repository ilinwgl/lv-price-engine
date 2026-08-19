import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.importing.models import (
    ParsedArticleData,
    ParsedCommodity,
    ParsedCommodityGroup,
    ParsedCommodityPrice,
    ParsedEstimatePrice,
    ParsedProductGroup,
)


class ArticleXmlParser:
    def parse(self, xml_path: Path) -> ParsedArticleData:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        result = ParsedArticleData()

        product_groups: dict[str, ParsedProductGroup] = {}

        for group in root.findall("CommodityGroup"):
            self._parse_group(
                group=group,
                result=result,
                product_groups=product_groups,
                parent_code=None,
            )

        result.product_groups = list(product_groups.values())

        return result

    def _parse_group(
        self,
        group: ET.Element,
        result: ParsedArticleData,
        product_groups: dict[str, ParsedProductGroup],
        parent_code: str | None,
    ) -> None:
        group_data = group.find("CommodityGroupData")

        if group_data is None:
            return

        group_code = self._text(group_data, "CommodityGroupID")

        if group_code is None:
            raise ValueError("CommodityGroup without CommodityGroupID")

        product_group_code = self._register_product_group(
            group_data,
            product_groups,
        )

        parsed_group = ParsedCommodityGroup(
            code=group_code,
            description=self._text(
                group_data,
                "CommodityGroupDescription",
            ),
            parent_code=parent_code,
            product_group_code=product_group_code,
            source_ref=self._attribute(group_data, "Xref"),
            cost_code=self._text(group_data, "CostCode"),
            unit=self._text(group_data, "UoM"),
            discount=self._decimal(group_data, "Discount"),
            wastage=self._decimal(group_data, "Wastage"),
            estimation_factor=self._decimal(
                group_data,
                "EstimationFactor",
            ),
            regie_factor=self._decimal(
                group_data,
                "RegieFaktor",
            ),
            addition_1=self._text(group_data, "Addition1"),
            addition_2=self._text(group_data, "Addition2"),
            addition_3=self._text(group_data, "Addition3"),
            addition_4=self._text(group_data, "Addition4"),
            remarks=self._text(group_data, "Remarks"),
            fixed_hours=self._bool(group_data, "FixedHours"),
        )

        result.commodity_groups.append(parsed_group)

        # Parse Commodities directly belonging to this group
        for commodity in group.findall("Commodity"):
            parsed_commodity = self._parse_commodity(
                commodity=commodity,
                group_code=group_code,
                inherited_product_group_code=product_group_code,
                product_groups=product_groups,
            )

            if parsed_commodity is not None:
                result.commodities.append(parsed_commodity)

        # Parse child groups recursively
        for child_group in group.findall("CommodityGroup"):
            self._parse_group(
                group=child_group,
                result=result,
                product_groups=product_groups,
                parent_code=group_code,
            )

    def _parse_commodity(
        self,
        commodity: ET.Element,
        group_code: str,
        inherited_product_group_code: str | None,
        product_groups: dict[str, ParsedProductGroup],
    ) -> ParsedCommodity | None:
        commodity_data = commodity.find("CommodityData")

        if commodity_data is None:
            return None

        commodity_code = self._text(
            commodity_data,
            "CommodityID",
        )

        if commodity_code is None:
            raise ValueError("Commodity without CommodityID")

        product_group_code = self._register_product_group(
            commodity_data,
            product_groups,
        )

        if product_group_code is None:
            product_group_code = inherited_product_group_code

        prices = self._parse_commodity_prices(commodity)
        estimate_prices = self._parse_estimate_prices(commodity)

        return ParsedCommodity(
            code=commodity_code,
            description=self._text(
                commodity_data,
                "CommodityDescription",
            ),
            commodity_group_code=group_code,
            product_group_code=product_group_code,
            source_ref=self._attribute(
                commodity_data,
                "Xref",
            ),
            unit=self._text(commodity_data, "UoM"),
            cost_code=self._text(
                commodity_data,
                "CostCode",
            ),
            cost_code_unit=self._text(
                commodity_data,
                "CostCodeUoM",
            ),
            weight=self._decimal(
                commodity_data,
                "Weight",
            ),
            weight_unit=self._text(
                commodity_data,
                "WeightUoM",
            ),
            volume=self._decimal(
                commodity_data,
                "Volume",
            ),
            volume_unit=self._text(
                commodity_data,
                "VolumeUoM",
            ),
            addition_1=self._text(
                commodity_data,
                "Addition1",
            ),
            addition_2=self._text(
                commodity_data,
                "Addition2",
            ),
            addition_3=self._text(
                commodity_data,
                "Addition3",
            ),
            addition_4=self._text(
                commodity_data,
                "Addition4",
            ),
            remarks=self._text(
                commodity_data,
                "Remarks",
            ),
            external_price_update=self._bool(
                commodity_data,
                "ExternalPriceUpdate",
            ),
            selected=self._bool(
                commodity_data,
                "SelectedCommodity",
            ),
            fixed_hours=self._bool(
                commodity_data,
                "FixedHours",
            ),
            change_date=self._date(
                commodity_data,
                "ChangeRestDate",
            ),
            change_user=self._text(
                commodity_data,
                "ChangeRestUser",
            ),
            prices=prices,
            estimate_prices=estimate_prices,
        )

    def _parse_commodity_prices(
        self,
        commodity: ET.Element,
    ) -> list[ParsedCommodityPrice]:
        result = []

        commodity_prices = commodity.find("CommodityPrices")

        if commodity_prices is None:
            return result

        for price in commodity_prices.findall("CommodityPrice"):
            unit_price = self._decimal(price, "PrUnit")
            currency = self._text(price, "CUR")

            if unit_price is None or currency is None:
                continue

            result.append(
                ParsedCommodityPrice(
                    unit_price=unit_price,
                    currency=currency,
                    discount=self._decimal(
                        price,
                        "Discount",
                    ),
                    freight_costs=self._decimal(
                        price,
                        "FreightCosts",
                    ),
                    miscellaneous=self._decimal(
                        price,
                        "Miscellaneous",
                    ),
                    wastage=self._decimal(
                        price,
                        "Wastage",
                    ),
                    modified_date=self._date(
                        price,
                        "DateOfLastModification",
                    ),
                    modified_user=self._text(
                        price,
                        "UserOfLastModification",
                    ),
                )
            )

        return result

    def _parse_estimate_prices(
        self,
        commodity: ET.Element,
    ) -> list[ParsedEstimatePrice]:
        result = []

        estimate_prices = commodity.find("EstimatePrices")

        if estimate_prices is None:
            return result

        for price in estimate_prices.findall("EstimatePrice"):
            price_type = self._attribute(price, "Typ")
            price_value = self._decimal(price, "Price")
            currency = self._text(price, "PriceCUR")

            if price_type is None or price_value is None or currency is None:
                continue

            result.append(
                ParsedEstimatePrice(
                    price_type=price_type,
                    factor=self._decimal(
                        price,
                        "Factor",
                    ),
                    price=price_value,
                    currency=currency,
                    modified_date=self._date(
                        price,
                        "DateOfPriceModification",
                    ),
                    modified_user=self._text(
                        price,
                        "UserOfPriceModification",
                    ),
                    fixed_price=self._bool(
                        price,
                        "FixedPriceFlag",
                    ),
                )
            )

        return result

    def _register_product_group(
        self,
        data: ET.Element,
        product_groups: dict[str, ParsedProductGroup],
    ) -> str | None:
        ccg = data.find("CCG")

        if ccg is None:
            return None

        code = self._attribute(ccg, "Id")

        if code is None:
            return None

        name = self._text(data, "ProductGroup") or self._attribute(ccg, "Desc")

        if name is None:
            return None

        if code not in product_groups:
            product_groups[code] = ParsedProductGroup(
                code=code,
                name=name,
            )

        return code

    @staticmethod
    def _text(
        element: ET.Element,
        tag: str,
    ) -> str | None:
        value = element.findtext(tag)

        if value is None:
            return None

        value = value.strip()

        return value or None

    @staticmethod
    def _attribute(
        element: ET.Element,
        name: str,
    ) -> str | None:
        value = element.get(name)

        if value is None:
            return None

        value = value.strip()

        return value or None

    @classmethod
    def _decimal(
        cls,
        element: ET.Element,
        tag: str,
    ) -> Decimal | None:
        value = cls._text(element, tag)

        if value is None:
            return None

        return Decimal(value)

    @classmethod
    def _date(
        cls,
        element: ET.Element,
        tag: str,
    ) -> date | None:
        value = cls._text(element, tag)

        if value is None:
            return None

        return date.fromisoformat(value)

    @classmethod
    def _bool(
        cls,
        element: ET.Element,
        tag: str,
    ) -> bool | None:
        value = cls._text(element, tag)

        if value is None:
            return None

        normalized = value.lower()

        if normalized == "true":
            return True

        if normalized == "false":
            return False

        raise ValueError(f"Invalid boolean value for {tag}: {value}")
