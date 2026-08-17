import logging

from sentence_transformers import SentenceTransformer

from database.connector import DBConnector
from database.repository import DBRepository
from ingestion.lv_reader import LVReader
from models.embedding_model import EmbeddingModel
from src.config.model_config_load import load_models_config
from src.logging.logger_config import LoggerConfig

logger = logging.getLogger(__name__)


def main() -> None:
    LoggerConfig.setup_logging()

    connector = DBConnector()
    repository = DBRepository(connector)

    all_candidates = repository.read_all_data()
    if not all_candidates:
        logger.error("No supplier prices found.")
        return

    lv_positions = LVReader.read_csv_file()
    if not lv_positions:
        logger.error("No LV positions found.")
        return

    models_config = load_models_config()

    for model_config in models_config:
        model_name = model_config.get("name", "")
        model_path = model_config.get("path", "")

        if not model_name or not model_path:
            logger.warning("Not get model config")
            continue

        model = SentenceTransformer(
            model_name_or_path=model_path,
            device=model_config.get("device", "cpu"),
            trust_remote_code=model_config.get("trust_remote_code", False),
        )

        embedding_model = EmbeddingModel(name=model_name, model=model)
        match_pipeline = (embedding_model, all_candidates)
        match_pipeline.run()


if __name__ == "__main__":
    main()
