from dataclasses import dataclass
import numpy as np


@dataclass
class AlignedFace:
    image: np.ndarray
    rotation_angle: float
