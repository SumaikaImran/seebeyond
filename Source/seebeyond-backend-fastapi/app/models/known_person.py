import uuid

from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class KnownPerson(Base):
    __tablename__ = "known_persons"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    embeddings = relationship(
        "FaceEmbedding",
        back_populates="person",
        cascade="all, delete-orphan"
    )