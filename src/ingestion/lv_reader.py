import csv
import os
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

from src.models import LVPosition

load_dotenv()


class LVReader:
    @staticmethod
    def read_csv_file(file_path: Path) -> list[LVPosition]:
        positions: list[LVPosition] = []

        encoding = os.getenv("LV_CSV_ENCODING", "utf-8-sig")
        delimiter = os.getenv("LV_CSV_DELIMITER", ";")

        with file_path.open(mode="r", encoding=encoding, newline="") as file:
            reader = csv.DictReader(file, delimiter=delimiter)

            for row in reader:
                position = LVPosition(
                    oz=row["OZ"].strip(),
                    short_text=row["Kurztext"].strip(),
                    long_text=row["Longtext"].strip(),
                    quantity=Decimal(row["Menge"]),
                    unit=row["Einheit"].strip(),
                )

                positions.append(position)

        return positions
