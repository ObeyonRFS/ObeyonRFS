from typing import List, Tuple
from pydantic import BaseModel
from obeyon_rfs.datatypes import *


class MessageType(BaseModel):
    pass

class ScanMsg(MessageType):
    scan_vectors:List[Vector3D]

class OdometryMsg(MessageType):
    x:float
    y:float
    z:float
    yaw:float
    pitch:float
    roll:float

class SimpleMsg(MessageType):
    message:str
    utc_time:str