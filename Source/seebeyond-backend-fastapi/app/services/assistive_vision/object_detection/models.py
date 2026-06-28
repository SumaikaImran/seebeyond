from dataclasses import dataclass
from enum import Enum


class ObjectRegion(str, Enum):

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


@dataclass
class BoundingBox:

    x1: float
    y1: float
    x2: float
    y2: float




@dataclass
class DetectedObject:

    class_id: int

    label: str

    confidence: float

    bbox: BoundingBox

    region: ObjectRegion

    distance: float | None = None