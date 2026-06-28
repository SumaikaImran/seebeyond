from pydantic import BaseModel


class BoundingBoxResponse(BaseModel):
    x: int
    y: int
    width: int
    height: int


class FaceRecognitionResponse(BaseModel):
    person_name: str | None
    confidence: float
    distance: float
    status: str
    bounding_box: BoundingBoxResponse


class AnalyzeResponse(BaseModel):
    faces: list[FaceRecognitionResponse]
    total_faces_detected: int
    total_faces_recognized: int