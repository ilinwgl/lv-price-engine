import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.database.connector import DBConnector
from src.database.repository import DBRepository

CSV_PATH = Path("data/database/supplier_prices_virtual_222.csv")


def main() -> None:
    connector = DBConnector()
    repository = DBRepository(connector)

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")

        count = 0

        for row in reader:
            print(row)
            repository.insert(
                category=row["category"],
                name=row["name"],
                description=row["description"],
                unit=row["unit"],
                unit_price=Decimal(row["unit_price"]),
                supplier=row["supplier"] or None,
                supplier_location=row["supplier_location"] or None,
                valid_from=(
                    date.fromisoformat(row["valid_from"]) if row["valid_from"] else None
                ),
                valid_to=(
                    date.fromisoformat(row["valid_to"]) if row["valid_to"] else None
                ),
            )
            count += 1

        print(f"Imported {count} supplier price records.")


if __name__ == "__main__":
    main()
