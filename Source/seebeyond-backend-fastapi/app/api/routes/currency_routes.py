import io

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from PIL import Image

from app.core.container import (
    container
)

router = APIRouter(
    tags=["Currency Detection"]
)


@router.post("/analyze")
async def analyze_currency(
    file: UploadFile = File(...)
):
    if container.currency_detector is None:
        raise HTTPException(
            status_code=503,
            detail="Currency detector is not initialized. Check app startup logs."
        )

    image_bytes = await file.read()

    image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    detections = (
        container.currency_detector.analyze_image(
            image
        )
    )

    total_amount = sum(
        d.value
        for d in detections
    )

    return {

        "count": len(detections),

        "total_amount": total_amount,

        "detections": [
            detection.model_dump()
            for detection in detections
        ]
    }

