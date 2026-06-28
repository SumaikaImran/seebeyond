from app.repositories.person_repository import (
    PersonRepository
)

from app.repositories.embedding_repository import (
    EmbeddingRepository
)

from app.services.face_detection.retinaface_detector import (
    RetinaFaceDetector
)

from app.services.face_alignment.aligner import (
    FaceAligner
)

from app.services.face_embedding.facenet_service import (
    FaceNetService
)


class RegistrationService:

    def __init__(
        self,
        detector: RetinaFaceDetector,
        aligner: FaceAligner,
        facenet: FaceNetService,
        person_repo: PersonRepository,
        embedding_repo: EmbeddingRepository
    ):
        self.detector = detector
        self.aligner = aligner
        self.facenet = facenet
        self.person_repo = person_repo
        self.embedding_repo = embedding_repo

    def register(
        self,
        name: str,
        image
    ):

        faces = self.detector.detect_faces(
            image
        )

        if len(faces) == 0:
            raise Exception(
                "No face detected"
            )

        if len(faces) > 1:
            raise Exception(
                "Multiple faces detected"
            )

        person = (
            self.person_repo.get_or_create(
                name
            )
        )

        aligned_face = (
            self.aligner.align_face(
                image,
                faces[0]
            )
        )

        embedding = (
            self.facenet.generate_embedding(
                aligned_face
            )
        )

        self.embedding_repo.create(
            person_id=person.id,
            embedding=embedding.tolist()
        )

        return person