from .models import (
    DetectedObject,
    ObjectRegion
)


class WarningEngine:

    CRITICAL_DISTANCE = 1.5

    def generate_warnings(
        self,
        detections: list[DetectedObject]
    ) -> list[str]:

        warnings = []

        for detection in detections:

            warning = self._generate_warning(
                detection
            )

            if warning:
                warnings.append(
                    warning
                )

        return warnings

    def _generate_warning(
        self,
        detection: DetectedObject
    ):

        if (
            detection.region ==
            ObjectRegion.CENTER
            and
            detection.distance <=
            self.CRITICAL_DISTANCE
        ):

            return (
                f"Warning. "
                f"{detection.label} "
                f"ahead."
            )

        return None