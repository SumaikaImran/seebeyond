import cv2
import numpy as np

from app.services.face_detection.models import (
    DetectedFace
)

from app.services.face_alignment.models import (
    AlignedFace
)


class FaceAligner:

    def __init__(
        self,
        output_size=(160, 160),
        margin=20
    ):
        self.output_size = output_size
        self.margin = margin

    def align_face(
        self,
        image: np.ndarray,
        face: DetectedFace
    ) -> AlignedFace:

        left_eye = face.landmarks.left_eye
        right_eye = face.landmarks.right_eye

        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]

        angle = np.degrees(
            np.arctan2(dy, dx)
        )

        eye_center = (
            (
                left_eye[0] + right_eye[0]
            ) / 2,
            (
                left_eye[1] + right_eye[1]
            ) / 2,
        )

        rotation_matrix = cv2.getRotationMatrix2D(
            eye_center,
            angle,
            1.0,
        )

        rotated = cv2.warpAffine(
            image,
            rotation_matrix,
            (
                image.shape[1],
                image.shape[0],
            ),
            flags=cv2.INTER_CUBIC,
        )

        bbox = face.bounding_box

        x1 = max(
            bbox.x - self.margin,
            0
        )

        y1 = max(
            bbox.y - self.margin,
            0
        )

        x2 = min(
            bbox.x + bbox.width + self.margin,
            image.shape[1]
        )

        y2 = min(
            bbox.y + bbox.height + self.margin,
            image.shape[0]
        )

        cropped = rotated[
            y1:y2,
            x1:x2
        ]

        aligned = cv2.resize(
            cropped,
            self.output_size
        )

        return AlignedFace(
            image=aligned,
            rotation_angle=float(angle)
        )
    def align_faces(
    self,
    image: np.ndarray,
    faces: list[DetectedFace]
) -> list[AlignedFace]:

        results = []

        for face in faces:
            results.append(
                self.align_face(
                    image,
                    face
                )
            )

        return results