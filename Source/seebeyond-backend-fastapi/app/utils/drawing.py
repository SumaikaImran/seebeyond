import cv2

from app.services.face_detection.models import (
    FaceDetection
)


def draw_faces(
    image,
    faces: list[FaceDetection]
):

    for face in faces:

        box = face.bounding_box

        cv2.rectangle(
            image,
            (box.x, box.y),
            (
                box.x + box.width,
                box.y + box.height
            ),
            (0, 255, 0),
            2
        )

    return image