from dataclasses import dataclass


@dataclass
class RecognitionResult:
    person_name: str | None
    confidence: float
    distance: float
    status: str