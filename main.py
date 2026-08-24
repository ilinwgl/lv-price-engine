import logging
from pathlib import Path

from sentence_transformers import SentenceTransformer

from src.config.model_config_load import load_models_config
from src.database.connector import DBConnector
from src.database.repository import DBRepository
from src.exporter.result_exporter import ResultExporter
from src.ingestion.gaeb_lv_loader import GAEBLVLoader
from src.logging.logger_config import LoggerConfig
from src.matching.match_pipeline import MatchPipeline
from src.models.embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)


def main() -> None:
    LoggerConfig.setup_logging()

    connector = DBConnector()
    repository = DBRepository(connector)

    all_candidates = repository.read_all_commodity_candidates()
    if not all_candidates:
        logger.error("No supplier prices found.")
        return
    logger.info(f"Number of Candidates: {len(all_candidates)}")
    ResultExporter.write_commodity_candidates(
        all_candidates,
        Path("./output/commodity_candidates.txt"),
    )

    lv_positions = GAEBLVLoader.load()
    if not lv_positions:
        logger.error("No LV positions found.")
        return
    logger.info(f"Number of LV Positions: {len(lv_positions)}")
    ResultExporter.write_lv_positions(
        lv_positions,
        Path("./output/lv_positions.txt"),
    )

    model_config = load_models_config()
    if model_config is None:
        logger.warning("Not get model config")
        return

    model_config = model_config.get("model", {})
    if not model_config:
        logger.warning("Not get model config")
        return

    model_name = model_config.get("name", "")
    model_path = model_config.get("path", "")
    if not model_name or not model_path:
        logger.warning("Not get model config")
        return

    logger.info(f"Model Name: {model_name}")

    model = SentenceTransformer(
        model_name_or_path=model_path,
        device=model_config.get("device", "cpu"),
        trust_remote_code=model_config.get("trust_remote_code", False),
    )

    embedding_model = EmbeddingModel(name=model_name, model=model)
    match_pipeline = MatchPipeline(embedding_model, lv_positions, all_candidates)
    match_results = match_pipeline.run()
    ResultExporter.write_match_results(
        match_results, Path(f"./output/match_results_{model_name}.txt")
    )


if __name__ == "__main__":
    main()
