import numpy as np
import threading
from pathlib import Path
from tensorflow.lite.python.interpreter import (
    Interpreter
)

from app.services.face_alignment.models import (
    AlignedFace
)


class FaceNetService:

    def __init__(
        
        self,
        model_path: str
        
    ):
        model_path_obj = Path(model_path)
        if not model_path_obj.exists():
            raise FileNotFoundError(
                f"FaceNet model not found at '{model_path}'. "
                f"Please ensure facenet.tflite is placed in the app/assets/models/ directory."
            )
        
        print(f"Loading FaceNet model from {model_path}")
        self.interpreter = Interpreter(
            model_path=model_path
        )

        self.interpreter.allocate_tensors()

        self.input_details = (
            self.interpreter.get_input_details()
        )

        self.output_details = (
            self.interpreter.get_output_details()
        )
        self.lock = threading.Lock()

    def _preprocess(
        self,
        image: np.ndarray
    ) -> np.ndarray:

        image = image.astype(
            np.float32
        )

        image = (
            image / 127.5
        ) - 1.0

        return np.expand_dims(
            image,
            axis=0
        )

    def generate_embedding(
    self,
    face: AlignedFace
) -> np.ndarray:

        input_tensor = (
            self._preprocess(
                face.image
            )
        )

        with self.lock:

            self.interpreter.set_tensor(
                self.input_details[0]["index"],
                input_tensor
            )

            self.interpreter.invoke()

            embedding = (
                self.interpreter.get_tensor(
                    self.output_details[0]["index"]
                )[0]
            )

        embedding = (
            embedding
            / np.linalg.norm(
                embedding
            )
        )

        return embedding
    def generate_embeddings(
        self,
        faces: list[AlignedFace]
    ) -> list[np.ndarray]:

        embeddings = []

        for face in faces:

            embeddings.append(
                self.generate_embedding(
                    face
                )
            )

        return embeddings