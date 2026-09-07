import logging
from pathlib import Path

from src.ingestion.gaeb_lv_loader import GAEBLVLoader
from src.logging.logger_config import LoggerConfig
from src.material.attribute_extractor import AttributeExtractor
from src.material.classifier import MaterialClassifier
from src.material.config_loader import MaterialConfigLoader
from src.material.material_extractor import MaterialExtractor
from src.material.registry import MaterialRegistry
from src.models.lv_position.lv_position import LVPosition

logger = logging.getLogger(__name__)

MATERIALS_CONFIG_PATH = Path("./config/materials/materials_registry.yaml")

OUTPUT_PATH = Path("./output/material_extraction_results.txt")


def build_material_extractor() -> MaterialExtractor:
    loader = MaterialConfigLoader(MATERIALS_CONFIG_PATH)
    templates = loader.load_all()

    registry = MaterialRegistry(templates)
    classifier = MaterialClassifier(registry)
    attribute_extractor = AttributeExtractor()

    return MaterialExtractor(
        registry=registry,
        classifier=classifier,
        attribute_extractor=attribute_extractor,
    )


def write_extraction_results(
    lv_positions: list[LVPosition],
) -> None:
    extractor = build_material_extractor()

    output_lines: list[str] = []

    for position in lv_positions:
        text = f"{position.short_text}\n{position.long_text}"

        result = extractor.extract(text)

        output_lines.append("=" * 80)
        output_lines.append(f"OZ: {position.oz}")
        output_lines.append(f"Kurztext: {position.short_text}")
        output_lines.append(f"Langtext: {position.long_text}")
        output_lines.append(f"Menge: {position.quantity} {position.unit}")
        output_lines.append("")

        if result is None:
            output_lines.append("Material: UNMATCHED")
            output_lines.append("")
            continue

        output_lines.append(f"Material: {result.material_type}")

        output_lines.append("Core attributes:")
        if result.core_attributes:
            for name, value in result.core_attributes.items():
                output_lines.append(f"  {name}: {value}")
        else:
            output_lines.append("  -")

        output_lines.append("Supplementary attributes:")
        if result.supplementary_attributes:
            for name, value in result.supplementary_attributes.items():
                output_lines.append(f"  {name}: {value}")
        else:
            output_lines.append("  -")

        output_lines.append("")

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        "\n".join(output_lines),
        encoding="utf-8",
    )


def main() -> None:
    LoggerConfig.setup_logging()

    lv_positions = GAEBLVLoader.load()
    if not lv_positions:
        logger.error("No LV positions found.")
        return

    write_extraction_results(lv_positions=lv_positions)


if __name__ == "__main__":
    main()
