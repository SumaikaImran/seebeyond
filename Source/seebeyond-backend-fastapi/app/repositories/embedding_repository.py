from sqlalchemy.orm import Session


from app.models.face_embedding import FaceEmbedding
from sqlalchemy.orm import joinedload

from app.models.face_embedding import (
    FaceEmbedding
)

class EmbeddingRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        person_id,
        embedding,
        image_path=None
    ):
        record = FaceEmbedding(
            person_id=person_id,
            embedding=embedding,
            image_path=image_path
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return record

    def get_person_embeddings(
        self,
        person_id
    ):
        return (
            self.db.query(FaceEmbedding)
            .filter(
                FaceEmbedding.person_id == person_id
            )
            .all()
        )

    def get_all_embeddings(self):
        return self.db.query(FaceEmbedding).all()
    
    

    def search_similar(
        self,
        embedding,
        limit: int = 100
    ):

        return (
            self.db.query(FaceEmbedding)
            .options(
                joinedload(
                    FaceEmbedding.person
                )
            )
            .order_by(
                FaceEmbedding.embedding.cosine_distance(
                    embedding
                )
            )
            .limit(limit)
            .all()
        )