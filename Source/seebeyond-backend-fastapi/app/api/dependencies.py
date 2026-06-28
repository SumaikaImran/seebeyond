from app.database.session import SessionLocal

from app.repositories.person_repository import (
    PersonRepository
)

from app.repositories.embedding_repository import (
    EmbeddingRepository
)

from app.services.registration.registration_service import (
    RegistrationService
)

from app.services.face_recognition.recognition_service import (
    RecognitionService
)

from app.core.container import (
    container
)


def _get_initialized_service(name: str):
    service = getattr(container, name)

    if service is None:
        raise RuntimeError(
            f"{name} service is not initialized. Check app startup logs."
        )

    return service


def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_registration_service(db):

    return RegistrationService(
        detector=get_detector(),
        aligner=get_aligner(),
        facenet=get_facenet(),
        person_repo=PersonRepository(db),
        embedding_repo=EmbeddingRepository(db)
    )

def get_detector():
    return _get_initialized_service("detector")


def get_aligner():
    return _get_initialized_service("aligner")


def get_facenet():
    return _get_initialized_service("facenet")

def get_recognition_service(db):

    return RecognitionService(
        EmbeddingRepository(db)
    )

