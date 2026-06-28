from app.services.assistive_vision.object_detection.models import (
    DetectedObject,
    ObjectRegion
)


class SpeechFormatter:

    def format(
        self,
        detections: list[DetectedObject]
    ) -> str:

        if not detections:

            return "No objects detected."

        messages = []

        for detection in detections:

            distance = round(
                detection.distance
            )

            region_text = (
                self._region_text(
                    detection.region
                )
            )

            messages.append(
                f"{detection.label} "
                f"{region_text}, "
                f"{distance} meters away."
            )

        return " ".join(messages)

    def _region_text(
        self,
        region: ObjectRegion
    ):

        if region == ObjectRegion.LEFT:
            return "on your left"

        if region == ObjectRegion.RIGHT:
            return "on your right"

        return "ahead"
