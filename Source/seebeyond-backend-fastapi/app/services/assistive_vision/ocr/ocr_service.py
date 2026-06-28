from .models import (
    OCRResult,
    OCRDetection
)

from .image_preprocessor import (
    OCRImagePreprocessor
)

from .text_builder import (
    OCRTextBuilder
)

class OCRService:

    def __init__(self):
        from app.services.assistive_vision.ocr.ocr_instance import (
            ocr_model
        )

        print("Initializing PaddleOCR service wrapper...")
        self.ocr = ocr_model
    def analyze_image(
    self,
    image
) -> OCRResult:

        processed = (
            OCRImagePreprocessor
            .preprocess(image)
        )

        result = self.ocr.predict(
            processed
        )

        if not result:
            return OCRResult(
                text="",
                detections=[],
                word_count=0
            )

        page = result[0]

        texts = page.get(
            "rec_texts",
            []
        )

        scores = page.get(
            "rec_scores",
            []
        )

        boxes = page.get(
            "rec_polys",
            []
        )

        detections = []

        for text, score, box in zip(
            texts,
            scores,
            boxes
        ):

            if score < 0.5:
                continue

            detections.append(
                OCRDetection(
                    text=text,
                    confidence=float(score),
                    bbox=box.tolist()
                    if hasattr(box, "tolist")
                    else box
                )
            )

        full_text = " ".join(
            d.text
            for d in detections
        )

        return OCRResult(
            text=full_text,
            detections=detections,
            word_count=len(
                full_text.split()
            )
        )