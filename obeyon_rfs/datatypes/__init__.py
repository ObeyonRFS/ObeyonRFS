from pydantic import BaseModel

class Vector3D(BaseModel):
    x: float
    y: float
    z: float