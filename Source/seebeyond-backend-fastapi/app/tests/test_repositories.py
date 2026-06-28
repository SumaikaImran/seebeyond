
# import os

# import cv2
# import numpy as np

# from app.database.session import (
#     SessionLocal
# )
# # Force SQLAlchemy to register both tables in memory
# from app.models.known_person import KnownPerson  # Adjust file paths if named differently
# from app.models.face_embedding import FaceEmbedding
# from app.repositories.embedding_repository import (
#     EmbeddingRepository
# )

# from app.services.face_detection.retinaface_detector import (
#     RetinaFaceDetector
# )

# from app.services.face_alignment.aligner import (
#     FaceAligner
# )

# from app.services.face_embedding.facenet_service import (
#     FaceNetService
# )

# from app.services.face_recognition.recognition_service import (
#     RecognitionService
# )
# import os
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# # 2. Safely join it with your image filename
# IMAGE_PATH = os.path.join(SCRIPT_DIR, "steve.jpg")

# # 3. Read the image using the absolute path
# image = cv2.imread(IMAGE_PATH)

# # Check if the image loaded properly before passing it to the detector
# if image is None:
#     raise FileNotFoundError(f"Could not find or read image at: {IMAGE_PATH}")

# db = SessionLocal()



# detector = RetinaFaceDetector()

# faces = detector.detect_faces(
#     image
# )

# aligner = FaceAligner()

# aligned_faces = (
#     aligner.align_faces(
#         image,
#         faces
#     )
# )

# facenet = FaceNetService(
#     "facenet.tflite"
# )

# embedding = (
#     facenet.generate_embedding(
#         aligned_faces[0]
#     )
# )
# print(embedding.shape)
# print(np.linalg.norm(embedding))
# # print(np.linalg.norm(np.array(candidate.embedding)))
# recognizer = RecognitionService(
#     EmbeddingRepository(db)
# )

# result = recognizer.recognize(
#     embedding
# )

# print(result)


# import cv2

# from app.database.session import SessionLocal

# from app.repositories.person_repository import (
#     PersonRepository
# )

# from app.repositories.embedding_repository import (
#     EmbeddingRepository
# )

# from app.services.face_detection.retinaface_detector import (
#     RetinaFaceDetector
# )

# from app.services.face_alignment.aligner import (
#     FaceAligner
# )

# from app.services.face_embedding.facenet_service import (
#     FaceNetService
# )

# from app.services.registration.registration_service import (
#     RegistrationService
# )

# db = SessionLocal()

# service = RegistrationService(
#     detector=RetinaFaceDetector(),
#     aligner=FaceAligner(),
#     facenet=FaceNetService(
#         "facenet.tflite"
#     ),
#     person_repo=PersonRepository(db),
#     embedding_repo=EmbeddingRepository(db)
# )
# import os
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# # 2. Safely join it with your image filename
# IMAGE_PATH = os.path.join(SCRIPT_DIR, "steve.jpg")

# image = cv2.imread(
#     IMAGE_PATH
# )

# service.register(
#     "steve",
#     image
# )

# print(
#     "Registration complete"
# )

# import os
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# import cv2

# from app.services.object_detection.detector import (
#     YOLODetector
# )
# import cv2

# from ultralytics import YOLO

# MODEL_PATH = "C:/src/backend/app/assets/models/blind_assist_best.pt"

# IMAGE_PATH = "C:/src/backend/app/tests/test2.jpeg"


# # def main():

# #     detector = YOLODetector(
# #         MODEL_PATH
# #     )

# #     image = cv2.imread(
# #         IMAGE_PATH
# #     )

# #     detections = detector.detect(
# #         image
# #     )

# #     print(
# #         f"\nDetected {len(detections)} objects\n"
# #     )

# #     for detection in detections:

# #         print(
# #             f"{detection.label:<20}"
# #             f"{detection.confidence:.2f}"
# #         )


# # if __name__ == "__main__":
# #     main()


# model = YOLO(
#     MODEL_PATH
# )

# results = model.predict(
#     IMAGE_PATH
# )

# annotated = results[0].plot()

# cv2.imshow(
#     "Detections",
#     annotated
# )

# cv2.waitKey(0)
# cv2.destroyAllWindows()


# from app.services.object_detection.models import (
#     BoundingBox,
#     DetectedObject
# )

# from app.services.object_detection.postprocessing import (
#     DetectionPostProcessor
# )

# processor = (
#     DetectionPostProcessor()
# )

# detections = [

#     DetectedObject(
#         class_id=0,
#         label="person",
#         confidence=0.95,
#         bbox=BoundingBox(
#             10, 10,
#             100, 200
#         ),
#         region=None
#     ),

#     DetectedObject(
#         class_id=1,
#         label="chair",
#         confidence=0.90,
#         bbox=BoundingBox(
#             300, 10,
#             450, 200
#         ),
#         region=None
#     ),

#     DetectedObject(
#         class_id=2,
#         label="door",
#         confidence=0.85,
#         bbox=BoundingBox(
#             700, 10,
#             900, 200
#         ),
#         region=None
#     )
# ]

# results = (
#     processor.assign_regions(
#         detections,
#         image_width=1000
#     )
# )

# for obj in results:

#     print(
#         obj.label,
#         obj.region
#     )


# import cv2

# from app.services.object_detection.object_detection_service import (
#     ObjectDetectionService
# )

# MODEL_PATH = "C:/src/backend/app/assets/models/blind_assist_best.pt"

# IMAGE_PATH = "C:/src/backend/app/tests/test5.jpg"


# service = (
#     ObjectDetectionService(
#         MODEL_PATH
#     )
# )

# image = cv2.imread(
#     IMAGE_PATH
# )

# detections = (
#     service.analyze_image(
#         image
#     )
# )

# print("\nFINAL OUTPUT\n")

# for detection in detections:

#     print(
#         detection.label,
#         detection.confidence,
#         detection.region
#     )


import requests

url = (
    "http://127.0.0.1:8000/api/object/detect"
)

with open(
    "C:/src/backend/app/tests/test5.jpg",
    "rb"
) as image:

    response = requests.post(
        url,
        files={
            "image": image
        }
    )

print(
    response.json()
)

# import cv2

# from app.services.object_detection.tracker import (
#     TrackedObject
# )
# from app.services.object_detection.bytetrack_service import ObjectTracker

# tracker = ObjectTracker(
#   "C:/src/backend/app/assets/models/blind_assist_best.pt"

# )

# cap = cv2.VideoCapture(0)

# while True:

#     ret, frame = cap.read()

#     results = tracker.track(
#         frame
#     )

#     annotated = results[0].plot()

#     cv2.imshow(
#         "Tracking",
#         annotated
#     )

#     if cv2.waitKey(1) == 27:
#         break


# import cv2

# from app.services.object_detection.object_detection_service import (
#     ObjectDetectionService
# )

# service = (
#     ObjectDetectionService(
#         "C:/src/backend/app/assets/models/blind_assist_best.pt"

#     )
# )

# image = cv2.imread(
#     "C:/src/backend/app/tests/test5.jpg"
# )

# detections = (
#     service.analyze_image(
#         image
#     )
# )

# for detection in detections:

#     print(
#         f"{detection.label} | "
#         f"{detection.region} | "
#         f"{detection.distance:.2f}m"
#     )



# import cv2

# from app.services.object_detection.object_detection_service import (
#     ObjectDetectionService
# )

# from app.services.object_detection.speech_formatter import (
#     SpeechFormatter
# )


# service = (
#     ObjectDetectionService(
#          "C:/src/backend/app/assets/models/blind_assist_best.pt"
#     )
# )

# formatter = (
#     SpeechFormatter()
# )

# image = cv2.imread(
#     "C:/src/backend/app/tests/test5.jpg"
# )

# detections = (
#     service.analyze_image(
#         image
#     )
# )

# message = (
#     formatter.format(
#         detections
#     )
# )

# print(message)



# import cv2

# from app.services.object_detection.object_detection_service import (
#     ObjectDetectionService
# )

# from app.services.object_detection.warning_engine import (
#     WarningEngine
# )

# service = ObjectDetectionService(
#       "C:/src/backend/app/assets/models/blind_assist_best.pt"
# )

# engine = WarningEngine()

# image = cv2.imread(
#      "C:/src/backend/app/tests/test5.jpg"
# )

# detections = (
#     service.analyze_image(
#         image
#     )
# )

# warnings = (
#     engine.generate_warnings(
#         detections
#     )
# )

# for warning in warnings:

#     print(warning)