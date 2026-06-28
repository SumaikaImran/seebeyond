from typing import List

from ultralytics import YOLO
from PIL import Image

from app.services.assistive_vision.currency_detection.models import (
    CurrencyDetection,
    BoundingBox
)

from app.services.assistive_vision.currency_detection.constants import (
    CLASS_TO_VALUE
)


class CurrencyDetectionService:

    def __init__(
        self,
        model_path: str
    ):

        self.model = YOLO(model_path)

    def analyze_image(
        self,
        image: Image.Image,
        confidence: float = 0.25
    ) -> List[CurrencyDetection]:

        results = self.model.predict(
            image,
            conf=confidence,
            verbose=False
        )

        detections = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(
                    box.cls.item()
                )

                class_name = (
                    self.model.names[class_id]
                )

                conf = float(
                    box.conf.item()
                )

                x1, y1, x2, y2 = (
                    box.xyxy[0].tolist()
                )

                detections.append(

                    CurrencyDetection(

                        class_id=class_id,
                        class_name=class_name,
                        value=CLASS_TO_VALUE.get(
                            class_name,
                            0
                        ),
                        confidence=round(
                            conf,
                            4
                        ),
                        bbox=BoundingBox(
                            x1=x1,
                            y1=y1,
                            x2=x2,
                            y2=y2
                        )
                    )
                )

        return detections
