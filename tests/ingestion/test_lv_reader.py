from decimal import Decimal
from pathlib import Path

from src.ingestion.lv_reader import LVReader


def test_read_csv():
    file_path = Path("./data/lv_positions/virtuelles_LV_Testprojekt.csv")

    positions = LVReader.read_csv_file(file_path)

    assert len(positions) == 72

    assert positions[0].oz == "01.01.0010"
    assert positions[0].short_text == "Oberboden abtragen"
    assert positions[0].quantity == Decimal(850)
    assert positions[0].unit == "m²"
