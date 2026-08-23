from pathlib import Path

from src.models.commodity_candidate import CommodityCandidate
from src.models.lv_position import LVPosition
from src.models.match_result import PositionMatchResult


class ResultExporter:
    @staticmethod
    def write_commodity_candidates(
        candidates: list[CommodityCandidate],
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open(
            mode="w",
            encoding="utf-8",
        ) as file:
            for candidate in candidates:
                file.write("-" * 80 + "\n")
                file.write(f"ID:            {candidate.id}\n")
                file.write(f"Code:          {candidate.code}\n")
                file.write(f"Description:   {candidate.description}\n")
                file.write(f"Unit:          {candidate.unit}\n")
                file.write(f"Category Path: {candidate.category_path}\n")

                file.write("\nCommodity Prices:\n")

                if candidate.commodity_prices:
                    for price in candidate.commodity_prices:
                        file.write(
                            f"  ID: {price.id}, "
                            f"Price: {price.unit_price} {price.currency}, "
                            f"Discount: {price.discount}, "
                            f"Freight: {price.freight_costs}, "
                            f"Misc: {price.miscellaneous}, "
                            f"Wastage: {price.wastage}\n"
                        )
                else:
                    file.write("  None\n")

                file.write("\nEstimate Prices:\n")

                if candidate.estimate_prices:
                    for price in candidate.estimate_prices:
                        file.write(
                            f"  ID: {price.id}, "
                            f"Type: {price.price_type}, "
                            f"Price: {price.price} {price.currency}, "
                            f"Factor: {price.factor}, "
                            f"Fixed: {price.fixed_price}\n"
                        )
                else:
                    file.write("  None\n")

                file.write("-" * 80 + "\n\n")

    @staticmethod
    def write_lv_positions(
        positions: list[LVPosition],
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open(
            mode="w",
            encoding="utf-8",
        ) as file:
            for position in positions:
                file.write("-" * 80 + "\n")
                file.write(f"GAEB ID:  {position.gaeb_id}\n")
                file.write(f"OZ:       {position.oz}\n")
                file.write(f"Quantity: {position.quantity}\n")
                file.write(f"Unit:     {position.unit}\n")

                file.write("\nShort Text:\n")
                file.write(f"{position.short_text}\n")

                file.write("\nLong Text:\n")
                file.write(f"{position.long_text}\n")

                file.write("-" * 80 + "\n\n")

    @staticmethod
    def write_match_results(
        match_results: list[PositionMatchResult],
        file_path: str | Path,
    ) -> None:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w", encoding="utf-8") as file:
            for result in match_results:
                position = result.lv_position

                file.write("=" * 80 + "\n")
                file.write(f"OZ:          {position.oz}\n")
                file.write(f"GAEB ID:     {position.gaeb_id}\n")
                file.write(f"Quantity:    {position.quantity}\n")
                file.write(f"Unit:        {position.unit}\n")
                file.write(f"Short Text:  {position.short_text}\n")
                file.write(f"Long Text:   {position.long_text}\n")
                file.write(f"Match Status: {result.match_status.value}\n")

                if not result.matched_candidates:
                    file.write("Candidates:   None\n")
                    file.write("\n")
                    continue

                file.write("\nMatched Candidates:\n")

                for index, match_candidate in enumerate(
                    result.matched_candidates,
                    start=1,
                ):
                    candidate = match_candidate.candidate

                    file.write("-" * 40 + "\n")
                    file.write(f"Rank:          {index}\n")
                    file.write(f"Score:         {match_candidate.score:.4f}\n")
                    file.write(f"ID:            {candidate.id}\n")
                    file.write(f"Code:          {candidate.code}\n")
                    file.write(f"Category Path: {candidate.category_path}\n")
                    file.write(f"Description:   {candidate.description}\n")
                    file.write(f"Unit:          {candidate.unit}\n")

                    file.write("\nCommodity Prices:\n")
                    if candidate.commodity_prices:
                        for price in candidate.commodity_prices:
                            file.write(
                                f"  ID: {price.id}, "
                                f"Price: {price.unit_price} {price.currency}, "
                                f"Discount: {price.discount}, "
                                f"Freight: {price.freight_costs}, "
                                f"Misc: {price.miscellaneous}, "
                                f"Wastage: {price.wastage}\n"
                            )
                    else:
                        file.write("  None\n")

                    file.write("\nEstimate Prices:\n")
                    if candidate.estimate_prices:
                        for price in candidate.estimate_prices:
                            file.write(
                                f"  ID: {price.id}, "
                                f"Type: {price.price_type}, "
                                f"Price: {price.price} {price.currency}, "
                                f"Factor: {price.factor}, "
                                f"Fixed: {price.fixed_price}\n"
                            )
                    else:
                        file.write("  None\n")

                file.write("\n")

            file.write("=" * 80 + "\n")
