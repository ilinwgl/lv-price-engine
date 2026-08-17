import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()


def load_models_config() -> list[dict]:
    config_path = os.getenv("CONFIG_PATH")

    if not config_path:
        raise ValueError("CONFIG_PATH is not set")

    config_path = Path(config_path)

    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        models_config = yaml.safe_load(file)

    if not isinstance(models_config, list):
        raise TypeError("Config file must contain a YAML list")

    return models_config
