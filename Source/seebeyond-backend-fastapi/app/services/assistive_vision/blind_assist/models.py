from dataclasses import dataclass


@dataclass
class BlindAssistResult:

    faces: list
    objects: list
    text: str
    summary: str