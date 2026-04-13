from dataclasses import dataclass
from pathlib import Path
import os
from typing import Optional


@dataclass(frozen=True)
class PipelineConfig:
    dataset_dir: Path = Path("data/public_lev_1")
    output_file: Path = Path("outputs/public_lev_1_predictions.txt")
    model_dir: Path = Path("artifacts/models")
    model_path: Path = Path("artifacts/models/isolation_forest.pkl")
    session_id: str = "sandbox-public-lev-1"
    random_state: int = 42
    contamination: float = 0.2


@dataclass(frozen=True)
class LangfuseConfig:
    enabled: bool
    public_key: Optional[str]
    secret_key: Optional[str]
    host: str


@dataclass(frozen=True)
class OpenRouterConfig:
    enabled: bool
    api_key: Optional[str]
    model: str
    site_url: Optional[str]
    site_name: Optional[str]


def load_langfuse_config() -> LangfuseConfig:
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST")
    enabled = bool(public_key and secret_key)
    return LangfuseConfig(
        enabled=enabled,
        public_key=public_key,
        secret_key=secret_key,
        host=host,
    )


def load_openrouter_config() -> OpenRouterConfig:
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "google/gemma-3-12b-it:free")
    site_url = os.getenv("OPENROUTER_SITE_URL")
    site_name = os.getenv("OPENROUTER_SITE_NAME")
    enabled = bool(api_key)
    return OpenRouterConfig(
        enabled=enabled,
        api_key=api_key,
        model=model,
        site_url=site_url,
        site_name=site_name,
    )
