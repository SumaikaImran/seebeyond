from ultralytics import YOLO

from .models import (
    BoundingBox,
    DetectedObject
)

from .custom_classes import (
    CLASS_NAMES
)


class YOLODetector:

    def __init__(
        self,
        model_path: str
    ):
        self._model = YOLO(model_path)

    def detect(
        self,
        image
    ) -> list[DetectedObject]:

        results = self._model.predict(
            source=image,
            verbose=False
        )

        detections = []

        result = results[0]

        for box in result.boxes:

            cls_id = int(box.cls)

            bbox = BoundingBox(
                x1=float(box.xyxy[0][0]),
                y1=float(box.xyxy[0][1]),
                x2=float(box.xyxy[0][2]),
                y2=float(box.xyxy[0][3]),
            )

            detections.append(
                DetectedObject(
                    class_id=cls_id,
                    label=CLASS_NAMES[cls_id],
                    confidence=float(box.conf),
                    bbox=bbox,
                    region=None
                )
            )

        return detections