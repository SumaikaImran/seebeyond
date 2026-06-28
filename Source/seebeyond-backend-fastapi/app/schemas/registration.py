from pydantic import BaseModel


class RegisterResponse(BaseModel):
    person_id: str
    person_name: str
    total_embeddings: int
    message: str