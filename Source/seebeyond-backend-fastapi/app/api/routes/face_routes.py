import cv2
import numpy as np

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
)

from app.api.dependencies import (
    get_aligner,
    get_db,
    get_detector,
    get_facenet,
    get_registration_service,
    get_recognition_service,
)

from ...schemas.registration import RegisterResponse

from ...schemas.recognition import (
    AnalyzeResponse,
    FaceRecognitionResponse,
    BoundingBoxResponse,
)

router = APIRouter()
@router.post(
    "/register",
    response_model=RegisterResponse
)
async def register_face(
    name: str,
    image: UploadFile = File(...),
    db=Depends(get_db)
):

    service = get_registration_service(
        db
    )

    contents = await image.read()

    np_image = np.frombuffer(
        contents,
        np.uint8
    )

    frame = cv2.imdecode(
        np_image,
        cv2.IMREAD_COLOR
    )

    try:

        person = service.register(
            name,
            frame
        )

        embeddings = (
            service.embedding_repo
            .get_person_embeddings(
                person.id
            )
        )

        return RegisterResponse(
            person_id=str(person.id),
            person_name=person.name,
            total_embeddings=len(
                embeddings
            ),
            message="Face registered successfully"
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.post(
    "/analyze",
    response_model=AnalyzeResponse
)
async def analyze(
    image: UploadFile = File(...),
    db=Depends(get_db),
    detector=Depends(get_detector),
    aligner=Depends(get_aligner),
    facenet=Depends(get_facenet)
):

    contents = await image.read()

    np_image = np.frombuffer(
        contents,
        np.uint8
    )

    frame = cv2.imdecode(
        np_image,
        cv2.IMREAD_COLOR
    )

    recognizer = get_recognition_service(
        db
    )

    faces = detector.detect_faces(
        frame
    )

    aligned_faces = aligner.align_faces(
        frame,
        faces
    )

    embeddings = facenet.generate_embeddings(
        aligned_faces
    )

    results = []
    recognized_count = 0

    for face, embedding in zip(
        faces,
        embeddings
    ):

        result = recognizer.recognize(
            embedding
        )

        if result.status == "recognized":
            recognized_count += 1

        results.append(
            FaceRecognitionResponse(
                person_name=result.person_name,
                confidence=result.confidence,
                distance=result.distance,
                status=result.status,
                bounding_box=BoundingBoxResponse(
                    x=face.bounding_box.x,
                    y=face.bounding_box.y,
                    width=face.bounding_box.width,
                    height=face.bounding_box.height
                )
            )
        )

    return AnalyzeResponse(
        faces=results,
        total_faces_detected=len(faces),
        total_faces_recognized=recognized_count
    )

