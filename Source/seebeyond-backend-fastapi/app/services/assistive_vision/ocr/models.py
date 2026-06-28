from dataclasses import dataclass

@dataclass
class OCRDetection:
    text: str
    confidence: float
    bbox: list

@dataclass
class OCRResult:
    text: str
    detections: list[OCRDetection]
    word_count: int