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


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...)
):
    if container.blind_assist is None:
        raise HTTPException(
            status_code=503,
            detail="Blind assist service is not initialized. Check app startup logs."
        )

    contents = await file.read()

    image = cv2.imdecode(
        np.frombuffer(contents, np.uint8),
        cv2.IMREAD_COLOR
    )

    result = (
        container.blind_assist
        .analyze_image(image)
    )

    return {
        "summary": result.summary,
        "text": result.text,
        "faces": result.faces,
        "objects": result.objects
    }
