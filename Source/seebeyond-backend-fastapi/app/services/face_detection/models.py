from dataclasses import dataclass


@dataclass
class BoundingBox:
    x: int
    y: int
    width: int
    height: int


@dataclass
class FaceLandmarks:
    left_eye: tuple[int, int]
    right_eye: tuple[int, int]
    nose: tuple[int, int]
    mouth_left: tuple[int, int]
    mouth_right: tuple[int, int]


@dataclass
class DetectedFace:
    bounding_box: BoundingBox
    landmarks: FaceLandmarks
    confidence: float