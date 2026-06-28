from .models import (
    ObjectRegion,
    DetectedObject
)


class DetectionPostProcessor:

    def filter_detections(
        self,
        detections: list[DetectedObject],
        threshold: float
    ):

        return [
            detection
            for detection in detections
            if detection.confidence >= threshold
        ]

    def assign_regions(
        self,
        detections: list[DetectedObject],
        image_width: int
    ):

        for detection in detections:

            center_x = (
                detection.bbox.x1 +
                detection.bbox.x2
            ) / 2

            if center_x < image_width * 0.33:

                detection.region = (
                    ObjectRegion.LEFT
                )

            elif center_x < image_width * 0.66:

                detection.region = (
                    ObjectRegion.CENTER
                )

            else:

                detection.region = (
                    ObjectRegion.RIGHT
                )

        return detections