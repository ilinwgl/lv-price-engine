import os
import re
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

from src.models import LVPosition

load_dotenv()


class GAEBLVLoader:
    @classmethod
    def load(cls) -> list[LVPosition]:
        file_path = os.getenv("LV_FILE_PATH", "")

        tree = ET.parse(Path(file_path))
        root = tree.getroot()

        namespace = cls._get_namespace(root)

        award = root.find(
            "gaeb:Award",
            namespace,
        )
        if award is None:
            return []

        boq = award.find(
            "gaeb:BoQ",
            namespace,
        )
        if boq is None:
            return []

        boq_info = boq.find(
            "gaeb:BoQInfo",
            namespace,
        )
        if boq_info is None:
            return []

        category_lengths, item_length = cls._read_oz_structure(namespace, boq_info)

        boq_body = boq.find(
            "gaeb:BoQBody",
            namespace,
        )
        if boq_body is None:
            return []

        positions: list[LVPosition] = []

        cls._read_boq_body(
            namespace,
            boq_body=boq_body,
            category_parts=[],
            category_lengths=category_lengths,
            item_length=item_length,
            positions=positions,
        )

        return positions

    @staticmethod
    def _get_namespace(root: ET.Element) -> dict[str, str]:
        if root.tag.startswith("{"):
            namespace_uri = root.tag.split("}")[0][1:]
            return {"gaeb": namespace_uri}

        return {}

    @classmethod
    def _read_oz_structure(
        cls,
        namespace: dict[str, str],
        boq_info: ET.Element,
    ) -> tuple[list[int], int]:
        category_lengths: list[int] = []
        item_length = 0

        breakdowns = boq_info.findall(
            "gaeb:BoQBkdn",
            namespace,
        )

        for breakdown in breakdowns:
            breakdown_type = breakdown.findtext(
                "gaeb:Type",
                namespaces=namespace,
            )

            length_text = breakdown.findtext(
                "gaeb:Length",
                namespaces=namespace,
            )

            if length_text is None:
                continue

            length = int(length_text)

            if breakdown_type == "BoQLevel":
                category_lengths.append(length)

            elif breakdown_type == "Item":
                item_length = length

        return category_lengths, item_length

    @classmethod
    def _read_boq_body(
        cls,
        namespace: dict[str, str],
        boq_body: ET.Element,
        category_parts: list[str],
        category_lengths: list[int],
        item_length: int,
        positions: list[LVPosition],
    ) -> None:
        categories = boq_body.findall(
            "gaeb:BoQCtgy",
            namespace,
        )

        for category in categories:
            category_r_no_part = category.get("RNoPart")

            if category_r_no_part is None:
                continue

            current_category_parts = [
                *category_parts,
                category_r_no_part,
            ]

            category_body = category.find(
                "gaeb:BoQBody",
                namespace,
            )
            if category_body is None:
                continue

            item_list = category_body.find(
                "gaeb:Itemlist",
                namespace,
            )

            if item_list is not None:
                items = item_list.findall(
                    "gaeb:Item",
                    namespace,
                )

                for item in items:
                    position = cls._read_item(
                        namespace,
                        item=item,
                        category_parts=current_category_parts,
                        category_lengths=category_lengths,
                        item_length=item_length,
                    )

                    positions.append(position)

            cls._read_boq_body(
                namespace,
                boq_body=category_body,
                category_parts=current_category_parts,
                category_lengths=category_lengths,
                item_length=item_length,
                positions=positions,
            )

    @classmethod
    def _read_item(
        cls,
        namespace: dict[str, str],
        item: ET.Element,
        category_parts: list[str],
        category_lengths: list[int],
        item_length: int,
    ) -> LVPosition:
        gaeb_id = item.get("ID", "")
        item_r_no_part = item.get("RNoPart", "")

        oz = cls._build_oz(
            category_parts=category_parts,
            category_lengths=category_lengths,
            item_r_no_part=item_r_no_part,
            item_length=item_length,
        )

        quantity_text = item.findtext(
            "gaeb:Qty",
            default="0",
            namespaces=namespace,
        )

        unit = item.findtext(
            "gaeb:QU",
            default="",
            namespaces=namespace,
        )

        short_text_element = item.find(
            "./gaeb:Description/gaeb:CompleteText/gaeb:OutlineText",
            namespace,
        )

        long_text_element = item.find(
            "./gaeb:Description/gaeb:CompleteText/gaeb:DetailTxt",
            namespace,
        )

        short_text = cls._clean_text(short_text_element)

        long_text = cls._clean_text(
            long_text_element,
            clean_gaeb_markers=True,
        )

        return LVPosition(
            gaeb_id=gaeb_id,
            oz=oz,
            short_text=short_text,
            long_text=long_text,
            quantity=Decimal(quantity_text),
            unit=unit.strip(),
        )

    @staticmethod
    def _build_oz(
        category_parts: list[str],
        category_lengths: list[int],
        item_r_no_part: str,
        item_length: int,
    ) -> str:
        oz_parts: list[str] = []

        for part, length in zip(
            category_parts,
            category_lengths,
        ):
            oz_parts.append(part.zfill(length))

        oz_parts.append(item_r_no_part.zfill(item_length))

        return ".".join(oz_parts)

    @staticmethod
    def _clean_text(
        element: ET.Element | None,
        clean_gaeb_markers: bool = False,
    ) -> str:
        if element is None:
            return ""

        texts: list[str] = []

        for text in element.itertext():
            text = re.sub(r"\s+", " ", text).strip()

            if not text:
                continue

            if clean_gaeb_markers:
                text = re.sub(
                    r"^'\(>(.*?)<\)\s*'\s*$",
                    r"\1",
                    text,
                )

            texts.append(text)

        return " ".join(texts)
