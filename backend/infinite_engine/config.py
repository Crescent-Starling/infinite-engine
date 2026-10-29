"""Local configuration; importing the application does not create or transmit data."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IE_", env_file=".env", extra="ignore")

    data_dir: Path = Path(".local/infinite-engine")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
