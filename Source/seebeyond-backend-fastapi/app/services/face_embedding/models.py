from dataclasses import dataclass
import numpy as np


@dataclass
class FaceEmbedding:
    embedding: np.ndarray