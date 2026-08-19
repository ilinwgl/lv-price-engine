from pathlib import Path

from src.importing.xml_parser import ArticleXmlParser


def main():
    xml_path = Path("./data/database/Artikel.xml")

    parser = ArticleXmlParser()
    data = parser.parse(xml_path)

    commodity_price_count = sum(len(commodity.prices) for commodity in data.commodities)

    estimate_price_count = sum(
        len(commodity.estimate_prices) for commodity in data.commodities
    )

    print("========== PARSER RESULT ==========")
    print(f"Product groups:   {len(data.product_groups)}")
    print(f"Commodity groups: {len(data.commodity_groups)}")
    print(f"Commodities:      {len(data.commodities)}")
    print(f"Commodity prices: {commodity_price_count}")
    print(f"Estimate prices:  {estimate_price_count}")

    print("\n========== SAMPLE COMMODITY ==========")

    if data.commodities:
        commodity = data.commodities[0]

        print(f"Code:          {commodity.code}")
        print(f"Description:   {commodity.description}")
        print(f"Group code:    {commodity.commodity_group_code}")
        print(f"Product group: {commodity.product_group_code}")
        print(f"Unit:          {commodity.unit}")

        print("\nPrices:")
        for price in commodity.prices:
            print(f"  {price.unit_price} {price.currency}")

        print("\nEstimate prices:")
        for price in commodity.estimate_prices:
            print(f"  {price.price_type}: {price.price} {price.currency}")

    print(
        "Unique commodity codes:",
        len({c.code for c in data.commodities}),
    )

    print(
        "Unique group codes:",
        len({g.code for g in data.commodity_groups}),
    )

    print(
        "Unique product group codes:",
        len({p.code for p in data.product_groups}),
    )


if __name__ == "__main__":
    main()
