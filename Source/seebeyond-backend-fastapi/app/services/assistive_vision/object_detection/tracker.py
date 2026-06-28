from dataclasses import dataclass

@dataclass
class TrackedObject:

    track_id: int

    label: str

    confidence: float

    region: str