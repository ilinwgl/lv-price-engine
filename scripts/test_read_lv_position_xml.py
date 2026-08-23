import re
import xml.etree.ElementTree as ET
from pathlib import Path

NAMESPACE = {"gaeb": "http://www.gaeb.de/GAEB_DA_XML/200407"}


def clean_long_text(element):
    texts = []

    for text in element.itertext():
        text = text.strip()

        if not text:
            continue

        # GAEB TextComplement:
        # '(>SB 2<)' -> SB 2
        # '(>Text<) ' -> Text
        text = re.sub(
            r"^'\(>(.*?)<\)\s*'\s*$",
            r"\1",
            text,
        )

        texts.append(text)

    return " ".join(texts)


def format_r_no_part(value, length):
    if value is None:
        return ""

    return value.zfill(length)


def read_item(
    item,
    category_parts,
    category_lengths,
    item_length,
):
    item_id = item.get("ID")
    item_r_no_part = item.get("RNoPart")

    # -------------------------------------------------------------------------
    # OZ
    # -------------------------------------------------------------------------

    oz_parts = []

    for category_part, length in zip(
        category_parts,
        category_lengths,
    ):
        oz_parts.append(format_r_no_part(category_part, length))

    oz_parts.append(
        format_r_no_part(
            item_r_no_part,
            item_length,
        )
    )

    oz = ".".join(oz_parts)

    # -------------------------------------------------------------------------
    # Quantity
    # -------------------------------------------------------------------------

    item_quantity = item.find(
        "gaeb:Qty",
        NAMESPACE,
    )

    if item_quantity is not None:
        item_quantity = item_quantity.text

    # -------------------------------------------------------------------------
    # Unit
    # -------------------------------------------------------------------------

    item_unit = item.find(
        "gaeb:QU",
        NAMESPACE,
    )

    if item_unit is not None:
        item_unit = item_unit.text

    # -------------------------------------------------------------------------
    # Lump Sum
    # -------------------------------------------------------------------------

    item_lump_sum = item.find(
        "gaeb:LumpSumItem",
        NAMESPACE,
    )

    if item_lump_sum is not None:
        item_lump_sum = item_lump_sum.text

    # -------------------------------------------------------------------------
    # Unit Price Breakdown
    # -------------------------------------------------------------------------

    item_up_breakdown = item.find(
        "gaeb:UPBkdn",
        NAMESPACE,
    )

    if item_up_breakdown is not None:
        item_up_breakdown = item_up_breakdown.text

    # -------------------------------------------------------------------------
    # Short Text
    # -------------------------------------------------------------------------

    item_short_text = item.find(
        "./gaeb:Description/gaeb:CompleteText/gaeb:OutlineText",
        NAMESPACE,
    )

    if item_short_text is not None:
        item_short_text = " ".join(
            text.strip() for text in item_short_text.itertext() if text.strip()
        )

    # -------------------------------------------------------------------------
    # Long Text
    # -------------------------------------------------------------------------

    item_long_text = item.find(
        "./gaeb:Description/gaeb:CompleteText/gaeb:DetailTxt",
        NAMESPACE,
    )

    if item_long_text is not None:
        item_long_text = clean_long_text(item_long_text)

    # -------------------------------------------------------------------------
    # Output
    # -------------------------------------------------------------------------

    print("-" * 80)
    print(f"Item ID:       {item_id}")
    print(f"OZ:            {oz}")
    print(f"RNoPart:       {item_r_no_part}")
    print(f"Quantity:      {item_quantity}")
    print(f"Unit:          {item_unit}")
    print(f"Lump Sum Item: {item_lump_sum}")
    print(f"UP Breakdown:  {item_up_breakdown}")

    print("\nShort Text:")
    print(item_short_text)

    print("\nLong Text:")
    print(item_long_text)

    print("-" * 80)
    print()


def read_boq_body(
    boq_body,
    category_parts,
    category_lengths,
    item_length,
):
    categories = boq_body.findall(
        "gaeb:BoQCtgy",
        NAMESPACE,
    )

    for category in categories:
        category_r_no_part = category.get("RNoPart")

        category_label = category.find(
            "gaeb:LblTx",
            NAMESPACE,
        )

        if category_label is not None:
            category_label_text = " ".join(
                text.strip() for text in category_label.itertext() if text.strip()
            )
        else:
            category_label_text = None

        current_category_parts = category_parts + [category_r_no_part]

        print("=" * 80)
        print(
            "Category Path:",
            " -> ".join(part for part in current_category_parts if part is not None),
        )
        print(f"Category: {category_label_text}")
        print("=" * 80)
        print()

        category_body = category.find(
            "gaeb:BoQBody",
            NAMESPACE,
        )

        if category_body is None:
            continue

        # ---------------------------------------------------------------------
        # Items directly inside this category
        # ---------------------------------------------------------------------

        item_list = category_body.find(
            "gaeb:Itemlist",
            NAMESPACE,
        )

        if item_list is not None:
            items = item_list.findall(
                "gaeb:Item",
                NAMESPACE,
            )

            for item in items:
                read_item(
                    item=item,
                    category_parts=current_category_parts,
                    category_lengths=category_lengths,
                    item_length=item_length,
                )

        # ---------------------------------------------------------------------
        # Nested Categories
        # ---------------------------------------------------------------------

        read_boq_body(
            boq_body=category_body,
            category_parts=current_category_parts,
            category_lengths=category_lengths,
            item_length=item_length,
        )


def main():
    data_xml_path = Path("./data/lv_positions/LV_Test.X83")

    tree = ET.parse(data_xml_path)
    root = tree.getroot()

    print(f"Root Tag: {root.tag}")
    print()

    # -------------------------------------------------------------------------
    # Project Info
    # -------------------------------------------------------------------------

    project_info = root.find(
        "gaeb:PrjInfo",
        NAMESPACE,
    )

    if project_info is None:
        print("PrjInfo not found.")
        return

    project_name = project_info.find(
        "gaeb:NamePrj",
        NAMESPACE,
    )

    if project_name is not None:
        project_name = project_name.text

    project_label = project_info.find(
        "gaeb:LblPrj",
        NAMESPACE,
    )

    if project_label is not None:
        project_label = project_label.text

    print(f"Project Info: {project_name} - {project_label}")
    print()

    # -------------------------------------------------------------------------
    # Award
    # -------------------------------------------------------------------------

    award = root.find(
        "gaeb:Award",
        NAMESPACE,
    )

    if award is None:
        print("Award not found.")
        return

    # -------------------------------------------------------------------------
    # BoQ
    # -------------------------------------------------------------------------

    boq_element = award.find(
        "gaeb:BoQ",
        NAMESPACE,
    )

    if boq_element is None:
        print("BoQ not found.")
        return

    boq_info = boq_element.find(
        "gaeb:BoQInfo",
        NAMESPACE,
    )

    if boq_info is None:
        print("BoQInfo not found.")
        return

    boq_label = boq_info.find(
        "gaeb:LblBoQ",
        NAMESPACE,
    )

    if boq_label is not None:
        boq_label = boq_label.text

    boq_date = boq_info.find(
        "gaeb:Date",
        NAMESPACE,
    )

    if boq_date is not None:
        boq_date = boq_date.text

    print(f"BoQ Info: {boq_label} - {boq_date}")
    print()

    # -------------------------------------------------------------------------
    # Read OZ structure
    # -------------------------------------------------------------------------

    boq_breakdowns = boq_info.findall(
        "gaeb:BoQBkdn",
        NAMESPACE,
    )

    category_lengths = []
    item_length = None

    print("OZ Structure:")

    for breakdown in boq_breakdowns:
        breakdown_type = breakdown.findtext(
            "gaeb:Type",
            namespaces=NAMESPACE,
        )

        breakdown_label = breakdown.findtext(
            "gaeb:LblBoQBkdn",
            namespaces=NAMESPACE,
        )

        breakdown_length_text = breakdown.findtext(
            "gaeb:Length",
            namespaces=NAMESPACE,
        )

        if breakdown_length_text is None:
            continue

        breakdown_length = int(breakdown_length_text)

        print(
            f"  Type: {breakdown_type}, "
            f"Label: {breakdown_label}, "
            f"Length: {breakdown_length}"
        )

        if breakdown_type == "BoQLevel":
            category_lengths.append(breakdown_length)

        elif breakdown_type == "Item":
            item_length = breakdown_length

    print()

    if item_length is None:
        print("No Item length defined in BoQBkdn.")
        return

    print(f"Category lengths: {category_lengths}")
    print(f"Item length:       {item_length}")
    print()

    # -------------------------------------------------------------------------
    # BoQ Body
    # -------------------------------------------------------------------------

    boq_body = boq_element.find(
        "gaeb:BoQBody",
        NAMESPACE,
    )

    if boq_body is None:
        print("BoQBody not found.")
        return

    all_items = boq_body.findall(
        ".//gaeb:Item",
        NAMESPACE,
    )

    print(f"Total number of Items: {len(all_items)}")
    print()

    # -------------------------------------------------------------------------
    # Recursive Category + Item Reading
    # -------------------------------------------------------------------------

    read_boq_body(
        boq_body=boq_body,
        category_parts=[],
        category_lengths=category_lengths,
        item_length=item_length,
    )


if __name__ == "__main__":
    main()
