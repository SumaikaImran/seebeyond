from pathlib import Path

from pydantic_settings import (
    BaseSettings
)

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(
    BaseSettings
):

    FACENET_MODEL_PATH: str = str(
        BASE_DIR / "assets" / "models" / "facenet.tflite"
    )

    CURRENCY_MODEL_PATH: str = str(
        BASE_DIR / "assets" / "models" / "currency_best.pt"
    )

    OBJECT_DETECTION_MODEL_PATH: str = str(
        BASE_DIR / "assets" / "models" / "blind_assist_v1.tflite"
    )

    RECOGNITION_THRESHOLD: float = (
        0.8
    )


settings = Settings()
