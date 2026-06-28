from pydantic import BaseModel


class ObjectDetectionResponse(
    BaseModel
):

    label: str

    confidence: float

    region: str