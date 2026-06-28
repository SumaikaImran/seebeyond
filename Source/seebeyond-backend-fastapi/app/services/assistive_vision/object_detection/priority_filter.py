PRIORITY_WEIGHTS = {

    # Critical
    "person": 10,
    "stairs": 10,
    "door": 10,

    "car": 10,
    "Car": 10,
    "truck": 10,
    "bus": 10,
    "train": 10,

    "motorcycle": 9,
    "bicycle": 9,
    "auto rikshaw": 9,

    "traffic light": 9,
    "stop sign": 9,

    "wall": 8,
    "window": 8,

    # Obstacles
    "chair": 7,
    "bench": 7,
    "dining table": 7,
    "couch": 7,
    "bed": 6,

    # Animals
    "dog": 8,
    "cat": 6,
    "horse": 8,
    "cow": 7,
    "bear": 10,

    # Useful
    "cell phone": 3,
    "Cell-Phone": 3,
    "laptop": 3,
    "book": 2,

    # Miscellaneous
    "bottle": 2,
    "cup": 1,
    "apple": 1,
    "banana": 1
}
from .models import DetectedObject

MAX_ANNOUNCEMENTS = 3


class PriorityFilter:

    def filter(
        self,
        detections: list[DetectedObject]
    ) -> list[DetectedObject]:

        def score(
            detection: DetectedObject
        ):

            priority = PRIORITY_WEIGHTS.get(
                detection.label,
                1
            )

            distance = max(
                detection.distance,
                0.5
            )

            return priority / distance

        detections.sort(
            key=score,
            reverse=True
        )

        return detections[
            :MAX_ANNOUNCEMENTS
        ]