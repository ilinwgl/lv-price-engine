import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()


def load_models_config() -> tuple[dict[str, Any], dict[str, Any]]:
    config_path = os.getenv("CONFIG_PATH")

    if not config_path:
        raise ValueError("CONFIG_PATH is not set.")

    config_path = Path(config_path)

    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        models_config = yaml.safe_load(file)

    if not isinstance(models_config, dict):
        raise TypeError("Config file must contain a YAML mapping.")

    embedder_config = models_config.get("embedder", {})
    if not isinstance(embedder_config, dict) or not embedder_config:
        raise ValueError("Embedder config is missing, empty, or invalid.")

    reranker_config = models_config.get("reranker", {})
    if not isinstance(reranker_config, dict) or not reranker_config:
        raise ValueError("Reranker config is missing, empty, or invalid.")

    return embedder_config, reranker_config
