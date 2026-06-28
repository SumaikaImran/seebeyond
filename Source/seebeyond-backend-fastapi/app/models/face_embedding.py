import uuid

from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import Text
from sqlalchemy.sql import func

from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from pgvector.sqlalchemy import Vector

from app.database.base import Base


class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    person_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("known_persons.id"),
        nullable=False
    )

    embedding: Mapped[list] = mapped_column(
        Vector(512)
    )

    image_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    person = relationship(
        "KnownPerson",
        back_populates="embeddings"
    )