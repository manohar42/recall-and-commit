import json
from pathlib import Path

from app.schemas.imports import SampleImportPayload

BACKEND_DIR = Path(__file__).resolve().parents[2]

SAMPLE_FILE_PATH = (
    BACKEND_DIR / "Sample-data" / "conversations.json"
)


def load_sample_payload() -> SampleImportPayload:
    if not SAMPLE_FILE_PATH.exists():
        raise FileNotFoundError(
            f"Sample data file not found at: {SAMPLE_FILE_PATH}"
        )

    with SAMPLE_FILE_PATH.open(encoding="utf-8") as file:
        raw = json.load(file)

    return SampleImportPayload.model_validate(raw)