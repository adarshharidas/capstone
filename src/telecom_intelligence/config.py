 
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional
 
try:
    from dotenv import load_dotenv
 
    load_dotenv()
except ImportError:  # pragma: no cover - optional during lightweight tests
    pass
 
 
ROOT_DIR = Path(__file__).resolve().parents[2]
PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"
DOCUMENTS_DIR = PACKAGE_DIR / "documents" / "runbooks"
OUTPUTS_DIR = ROOT_DIR / "outputs"
 
 
@dataclass(frozen=True)
class Settings:
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_embedding_model: str = os.getenv(
        "GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"
    )
    data_dir: Path = DATA_DIR
    documents_dir: Path = DOCUMENTS_DIR
    outputs_dir: Path = OUTPUTS_DIR
 
 
def get_settings() -> Settings:
    return Settings()
 
 
 
