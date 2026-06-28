from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

import cv2
import numpy as np

from app.core.container import (
    container
)

router = APIRouter()

@router.post("/read")
async def read_text(
    file: UploadFile = File(...)
):

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Empty image"
        )

    image = cv2.imdecode(
        np.frombuffer(
            contents,
            np.uint8
        ),
        cv2.IMREAD_COLOR
    )

    try:
        if container.ocr is None:
            raise RuntimeError(
                "OCR service is not initialized. Check app startup logs."
            )

        result = (
            container.ocr
            .analyze_image(image)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OCR inference failed: {exc}"
        )

    return {
        "text": result.text,
        "word_count": result.word_count,
        "detections": [
            {
                "text": d.text,
                "confidence": d.confidence
            }
            for d in result.detections
        ]
    }

