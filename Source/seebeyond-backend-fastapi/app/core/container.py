from app.core.settings import settings
from app.services.assistive_vision.blind_assist.blind_assist_service import (
    BlindAssistService
)
from app.services.assistive_vision.currency_detection.currency_detection_service import (
    CurrencyDetectionService
)
from app.services.assistive_vision.object_detection.object_detection_service import (
    ObjectDetectionService
)
from app.services.assistive_vision.ocr.ocr_service import (
    OCRService
)
from app.services.face_alignment.aligner import (
    FaceAligner
)
from app.services.face_detection.retinaface_detector import (
    RetinaFaceDetector
)
from app.services.face_embedding.facenet_service import (
    FaceNetService
)


class AppContainer:

    def __init__(self):
        self.ocr = None
        self.detector = None
        self.currency_detector = None
        self.aligner = None
        self.facenet = None
        self.blind_assist = None
        self.object_detector = None
        self.face_recognition = None

    def initialize(self):
        print("Loading Face Detector...")
        self.detector = RetinaFaceDetector()

        print("Loading Face Aligner...")
        self.aligner = FaceAligner()

        print("Loading FaceNet...")
        self.facenet = FaceNetService(
            settings.FACENET_MODEL_PATH
        )

        print("Loading OCR...")
        self.ocr = OCRService()

        print("Loading Object Detection...")
        self.object_detector = ObjectDetectionService(
            settings.OBJECT_DETECTION_MODEL_PATH
        )

        print("Loading Blind Assist...")
        self.blind_assist = BlindAssistService()

        print("Loading Currency Detector...")
        self.currency_detector = CurrencyDetectionService(
            settings.CURRENCY_MODEL_PATH
        )

        print("Models loaded successfully")


container = AppContainer()
