from pathlib import Path

from src.database.connector import DBConnector
from src.database.repository import DBRepository
from src.importing.importer import ArticleImporter
from src.importing.xml_parser import ArticleXmlParser


def main() -> None:
    xml_path = Path("./data/database/Artikel.xml")

    parser = ArticleXmlParser()
    data = parser.parse(xml_path)

    connector = DBConnector()
    connection = connector.connect()
    repository = DBRepository(connector, connection)

    importer = ArticleImporter(repository)

    try:
        importer.import_data(data)
        connection.commit()

        print("Article import completed successfully.")
        print(f"Product groups:   {len(data.product_groups)}")
        print(f"Commodity groups: {len(data.commodity_groups)}")
        print(f"Commodities:      {len(data.commodities)}")
        print(
            "Commodity prices:",
            sum(len(c.prices) for c in data.commodities),
        )
        print(
            "Estimate prices:",
            sum(len(c.estimate_prices) for c in data.commodities),
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()
