import io

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from PIL import Image

import numpy as np

from app.core.container import (
    container
)

router = APIRouter()


@router.post("/detect")

async def detect_objects(
    image: UploadFile = File(...)
):
    if container.object_detector is None:
        raise HTTPException(
            status_code=503,
            detail="Object detector is not initialized. Check app startup logs."
        )

    contents = await image.read()

    pil_image = (
        Image.open(
            io.BytesIO(contents)
        ).convert("RGB")
    )

    np_image = np.array(
        pil_image
    )

    detections = (
        container.object_detector.analyze_image(
            np_image
        )
    )

    return {
        "objects": [
            {
                "label": d.label,
                "confidence": d.confidence,
                "region": d.region
            }
            for d in detections
        ]
    }
