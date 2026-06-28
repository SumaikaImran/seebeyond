from .constants import (
    CONFIDENCE_THRESHOLD
)

from .detector import (
    YOLODetector
)

from .postprocessing import (
    DetectionPostProcessor
)
from .distance_estimator import (
    DistanceEstimator
)
from .priority_filter import (
    PriorityFilter
)

class ObjectDetectionService:

    def __init__(
        self,
        model_path: str
    ):

        self._detector = (
            YOLODetector(
                model_path
            )
        )

        self._postprocessor = (
            DetectionPostProcessor()
        )
        self._distance_estimator = (
            DistanceEstimator()
        )
        self._priority_filter = (
            PriorityFilter()
        )
    def analyze_image(
        self,
        image
    ):

        detections = (
            self._detector.detect(
                image
            )
        )

        detections = (
            self._postprocessor
            .filter_detections(
                detections,
                CONFIDENCE_THRESHOLD
            )
        )

        image_width = image.shape[1]

        detections = (
            self._postprocessor
            .assign_regions(
                detections,
                image_width
            )
        )
        detections = (
            self._distance_estimator.process(
                detections
            )
        )
        detections = (
            self._priority_filter.filter(
                detections
            )
        )

        return detections