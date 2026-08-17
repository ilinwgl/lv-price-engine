import logging
from pathlib import Path

from sentence_transformers import SentenceTransformer

from src.database.connector import DBConnector
from src.database.repository import DBRepository
from src.ingestion.lv_reader import LVReader
from src.logging.logger_config import LoggerConfig
from src.matching.vector_matcher import VectorMatcher

logger = logging.getLogger(__name__)


def main() -> None:
    LoggerConfig.setup_logging()

    # ---------------------------------------------------------
    # Load embedding model
    # ---------------------------------------------------------
    model_path = "./models/embedding/bge-m3"

    logger.info("Loading embedding model: %s", model_path)
    model = SentenceTransformer(model_path)
    logger.info("Embedding model loaded")

    # ---------------------------------------------------------
    # Select one position to test
    # ---------------------------------------------------------
    # Read LV positions
    lv_positions_path = "./data/lv_positions/virtuelles_LV_embedding_test.csv"
    logger.info(
        "Loading LV positions from %s",
        lv_positions_path,
    )

    lv_positions = LVReader.read_csv_file(Path(lv_positions_path))
    if not lv_positions:
        logger.error("No LV positions found.")
        return
    lv_position = lv_positions[0]
    lv_text = f"{lv_position.short_text}. {lv_position.long_text}"
    lv_embedding = model.encode(lv_text, normalize_embeddings=True)
    logger.info(
        "LV embedding created with shape %s",
        lv_embedding.shape,
    )

    # ---------------------------------------------------------
    # Load supplier prices and create embeddings
    # ---------------------------------------------------------
    logger.info("Loading supplier prices from database")

    # Read supplier prices from database
    connector = DBConnector()
    repository = DBRepository(connector)
    all_candidates = repository.read_all_data()
    if not all_candidates:
        logger.error("No supplier prices found.")
        return
    logger.info(
        "Loaded %d supplier prices",
        len(all_candidates),
    )

    # Select usefull text from candidate
    selected_candidates = VectorMatcher.filter_by_unit(lv_position, all_candidates)
    candidate_texts = [
        f"{candidate.name}. {candidate.description}"
        for candidate in selected_candidates
    ]

    logger.info(
        "Creating embeddings for %d supplier prices",
        len(candidate_texts),
    )
    # Encode all supplier price descriptions
    candidate_embeddings = model.encode(
        candidate_texts,
        batch_size=16,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    logger.info(
        "Supplier price embeddings created with shape %s",
        candidate_embeddings.shape,
    )

    # ---------------------------------------------------------
    # Match results
    # ---------------------------------------------------------
    top_k = 5

    logger.info(
        "Matching LV position %s against %d supplier prices",
        lv_position.oz,
        len(selected_candidates),
    )

    matched_candidates = VectorMatcher.match(
        lv_embedding, candidate_embeddings, selected_candidates, top_k
    )

    logger.info(
        "Matching completed, returning top %d candidates",
        len(matched_candidates),
    )

    logger.info(
        "LV postion info: OZ: %s, Kurztext: %s, Longtext %s",
        lv_position.oz,
        lv_position.short_text,
        lv_position.long_text,
    )

    for rank, candidate in enumerate(matched_candidates, start=1):
        logger.info(f"\n#{rank}")
        logger.info(f"Score:       {candidate.score:.4f}")
        logger.info(f"ID:          {candidate.price_id}")
        logger.info(f"Category:    {candidate.category}")
        logger.info(f"Name:        {candidate.name}")
        logger.info(f"Description: {candidate.description}")
        logger.info(f"Unit:        {candidate.unit}")
        logger.info(f"Unit Price:  {candidate.unit_price}")


if __name__ == "__main__":
    main()
