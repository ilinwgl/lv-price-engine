import logging
from pathlib import Path

from src.config.model_config_load import load_models_config
from src.database.connector import DBConnector
from src.database.repository import DBRepository
from src.exporter.result_exporter import ResultExporter
from src.ingestion.gaeb_lv_loader import GAEBLVLoader
from src.logging.logger_config import LoggerConfig
from src.matching.match_pipeline import MatchPipeline
from src.models.model_loader import ModelLoader

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

    embedder_config, reranker_config = load_models_config()

    embedding_model = ModelLoader.load_embedder(embedder_config)
    logger.info(
        "Embedder Model: %s",
        embedding_model.name,
    )

    reranker_model = ModelLoader.load_reranker(reranker_config)
    logger.info(
        "Reranker Model: %s",
        reranker_model.name,
    )

    match_pipeline = MatchPipeline(
        embedding_model=embedding_model,
        reranker_model=reranker_model,
        lv_positions=lv_positions,
        candidates=all_candidates,
    )

    match_results = match_pipeline.run()

    ResultExporter.write_match_results(
        match_results,
        Path(
            f"./output/match_results_retrieval_{embedding_model.name}_bm25_rerank_{reranker_model.name}.txt"
        ),
    )


if __name__ == "__main__":
    main()
