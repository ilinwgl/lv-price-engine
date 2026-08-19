import xml.etree.ElementTree as ET
from pathlib import Path


def parse_group(group, category_path=None, depth=1):
    if category_path is None:
        category_path = []

    group_data = group.find("CommodityGroupData")

    group_id = None
    group_description = None

    if group_data is not None:
        group_id = group_data.findtext("CommodityGroupID")
        group_description = group_data.findtext("CommodityGroupDescription")

    current_path = category_path + [
        {
            "id": group_id,
            "description": group_description,
        }
    ]

    child_groups = group.findall("CommodityGroup")

    leaf_groups = []
    commodity_count = 0

    if child_groups:
        for child_group in child_groups:
            child_leaf_groups, child_commodity_count = parse_group(
                child_group,
                current_path,
                depth + 1,
            )

            leaf_groups.extend(child_leaf_groups)
            commodity_count += child_commodity_count

    else:
        commodities = group.findall("Commodity")
        commodity_count = len(commodities)

        commodity_results = []

        for commodity in commodities:
            commodity_data = commodity.find("CommodityData")

            if commodity_data is None:
                continue

            commodity_id = commodity_data.findtext("CommodityID")
            description = commodity_data.findtext("CommodityDescription")
            change_rest_date = commodity_data.findtext("ChangeRestDate")
            change_rest_user = commodity_data.findtext("ChangeRestUser")
            uom = commodity_data.findtext("UoM")

            commodity_prices = commodity.find("CommodityPrices")

            prices = []

            if commodity_prices is not None:
                for commodity_price in commodity_prices.findall("CommodityPrice"):
                    pr_unit = commodity_price.findtext("PrUnit")
                    cur = commodity_price.findtext("CUR")

                    prices.append(
                        {
                            "pr_unit": pr_unit,
                            "cur": cur,
                        }
                    )

            commodity_results.append(
                {
                    "commodity_id": commodity_id,
                    "description": description,
                    "change_rest_date": change_rest_date,
                    "change_rest_user": change_rest_user,
                    "uom": uom,
                    "prices": prices,
                }
            )

        leaf_groups.append(
            {
                "depth": depth,
                "category_path": current_path,
                "commodity_count": commodity_count,
                "commodities": commodity_results,
            }
        )

    return leaf_groups, commodity_count


data_xml_path = Path("./data/database/Artikel.xml")

tree = ET.parse(data_xml_path)
root = tree.getroot()

top_groups = root.findall("CommodityGroup")

all_leaf_groups = []
total_commodity_count = 0

for group in top_groups:
    leaf_groups, commodity_count = parse_group(group)

    all_leaf_groups.extend(leaf_groups)
    total_commodity_count += commodity_count


output_path = Path("./data/output/article_inspection.txt")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as file:
    file.write("========== GROUP RESULTS ==========\n\n")

    for index, group_result in enumerate(all_leaf_groups, start=1):
        file.write(f"Group #{index}\n")
        file.write(f"Depth: {group_result['depth']}\n")

        file.write("Category path:\n")

        for level, category in enumerate(
            group_result["category_path"],
            start=1,
        ):
            file.write(
                f"  Level {level}: {category['id']} - {category['description']}\n"
            )

        file.write(f"Commodity count: {group_result['commodity_count']}\n")

        file.write("\nCommodities:\n")

        for commodity in group_result["commodities"]:
            file.write(
                f"  ID: {commodity['commodity_id']}\n"
                f"  Description: {commodity['description']}\n"
                f"  UoM: {commodity['uom']}\n"
                f"  ChangeRestDate: {commodity['change_rest_date']}\n"
                f"  ChangeRestUser: {commodity['change_rest_user']}\n"
            )

            for price in commodity["prices"]:
                file.write(f"  Price: {price['pr_unit']} {price['cur']}\n")

            file.write("  ------------------------\n")

        file.write("\n")

    file.write("========== SUMMARY ==========\n")
    file.write(f"Top-level groups: {len(top_groups)}\n")
    file.write(f"Leaf groups: {len(all_leaf_groups)}\n")
    file.write(f"Total commodities: {total_commodity_count}\n")

print(f"Result written to: {output_path}")
