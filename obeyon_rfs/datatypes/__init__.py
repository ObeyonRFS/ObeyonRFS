from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class Vector3D:
    x: float
    y: float
    z: float