from collections import defaultdict
import numpy as np

from app.repositories.embedding_repository import (
    EmbeddingRepository
)

from app.services.face_recognition.models import (
    RecognitionResult
)


class RecognitionService:


    def __init__(
        self,
        embedding_repository,
        threshold: float = 0.80
    ):
        self.embedding_repository = embedding_repository
        self.threshold = threshold


    def recognize(
        self,
        embedding: np.ndarray
    ) -> RecognitionResult:

        candidates = (
            self.embedding_repository
            .search_similar(
                embedding.tolist(),
                limit=100
            )
        )

        if not candidates:
            return RecognitionResult(
                person_name=None,
                confidence=0.0,
                distance=999.0,
                status="unknown"
            )

        grouped = defaultdict(list)

        # Group distances by person
        for candidate in candidates:

            candidate_embedding = np.array(
                candidate.embedding,
                dtype=np.float32
            )

            distance = np.linalg.norm(
                embedding - candidate_embedding
            )

            grouped[
                candidate.person.name
            ].append(distance)

        best_person = None
        best_distance = float("inf")

        # Use nearest embedding per person
        for person_name, distances in grouped.items():

            person_distance = min(distances)

            print(
                f"Person: {person_name} | "
                f"Best Distance: {person_distance:.4f}"
            )

            if person_distance < best_distance:
                best_distance = person_distance
                best_person = person_name

        confidence = self.calculate_confidence(
            best_distance
        )

        print(
            f"Selected: {best_person} | "
            f"Distance: {best_distance:.4f} | "
            f"Confidence: {confidence}"
        )

        if best_distance <= self.threshold:

            return RecognitionResult(
                person_name=best_person,
                confidence=confidence,
                distance=round(best_distance, 4),
                status="recognized"
            )

        return RecognitionResult(
            person_name=None,
            confidence=confidence,
            distance=round(best_distance, 4),
            status="unknown"
        )

    def calculate_confidence(
        self,
        distance: float
    ) -> float:

        confidence = max(
            0.0,
            min(
                100.0,
                ((1.5 - distance) / 1.5) * 100
            )
        )

        return round(
            confidence,
            2
        )