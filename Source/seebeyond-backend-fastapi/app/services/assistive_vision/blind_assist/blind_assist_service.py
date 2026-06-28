# from app.core.container import container

from .models import (
    BlindAssistResult
)

from .scene_summary_builder import (
    SceneSummaryBuilder
)


class BlindAssistService:

    def analyze_image(
        self,
        image
    ):

        faces = []

        objects = []

        text = ""

        # Face Recognition
        from app.core.container import container

        if container.face_recognition is not None:
            faces = (
                container.face_recognition
                .recognize(image)
            )

        # Object Detection

        if container.object_detector is not None:
            objects = (
                container.object_detector
                .analyze_image(image)
            )

        # OCR

        if container.ocr is not None:
            ocr_result = (
                container.ocr
                .analyze_image(image)
            )

            text = ocr_result.text

        summary = (
            SceneSummaryBuilder.build(
                faces,
                objects,
                text
            )
        )

        return BlindAssistResult(
            faces=faces,
            objects=objects,
            text=text,
            summary=summary
        )
