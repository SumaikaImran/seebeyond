from pydantic import BaseModel


class BoundingBox(BaseModel):

    x1: float
    y1: float
    x2: float
    y2: float


class CurrencyDetection(BaseModel):

    class_id: int
    class_name: str
    value: int
    confidence: float
    bbox: BoundingBox