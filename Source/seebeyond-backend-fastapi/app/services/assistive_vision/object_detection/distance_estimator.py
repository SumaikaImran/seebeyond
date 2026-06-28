from .models import (
    DetectedObject
)


class DistanceEstimator:

    def __init__(self):

        self.reference_height = 300

        self.reference_distance = 1.0

    def estimate_distance(
        self,
        bbox_height: float
    ) -> float:

        if bbox_height <= 0:
            return 999.0

        return (
            self.reference_height
            * self.reference_distance
        ) / bbox_height

    def process(
        self,
        detections: list[DetectedObject]
    ):

        for detection in detections:

            bbox_height = (
                detection.bbox.y2
                - detection.bbox.y1
            )

            detection.distance = (
                self.estimate_distance(
                    bbox_height
                )
            )

        return detections