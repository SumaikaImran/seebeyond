from sqlalchemy.orm import Session

from app.models.known_person import KnownPerson


class PersonRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, person_id):
        return (
            self.db.query(KnownPerson)
            .filter(KnownPerson.id == person_id)
            .first()
        )

    def get_by_name(self, name: str):
        return (
            self.db.query(KnownPerson)
            .filter(KnownPerson.name == name)
            .first()
        )

    def create(self, name: str):
        person = KnownPerson(name=name)

        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)

        return person

    def get_or_create(self, name: str):

        person = self.get_by_name(name)

        if person:
            return person

        return self.create(name)

    def list_all(self):
        return self.db.query(KnownPerson).all()