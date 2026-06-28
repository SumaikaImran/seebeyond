from insightface.app import FaceAnalysis

from app.services.face_detection.models import (
    BoundingBox,
    FaceLandmarks,
    DetectedFace,
)


class RetinaFaceDetector:

    def __init__(self):
        print("RetinaFace initialized")
        self.app = FaceAnalysis(
            providers=["CPUExecutionProvider"]
        )

        self.app.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

    def detect_faces(self, image):

        faces = self.app.get(image)

        results = []

        for face in faces:

            bbox = face.bbox.astype(int)

            landmarks = face.kps.astype(int)

            results.append(
                DetectedFace(
                    bounding_box=BoundingBox(
                        x=int(bbox[0]),
                        y=int(bbox[1]),
                        width=int(
                            bbox[2] - bbox[0]
                        ),
                        height=int(
                            bbox[3] - bbox[1]
                        ),
                    ),
                    landmarks=FaceLandmarks(
                        left_eye=tuple(
                            landmarks[0]
                        ),
                        right_eye=tuple(
                            landmarks[1]
                        ),
                        nose=tuple(
                            landmarks[2]
                        ),
                        mouth_left=tuple(
                            landmarks[3]
                        ),
                        mouth_right=tuple(
                            landmarks[4]
                        ),
                    ),
                    confidence=float(
                        face.det_score
                    ),
                )
            )

        return results