from typing import List, Tuple
from obeyon_rfs.datatypes import *

@dataclass
class MessageType:
    pass

@dataclass
class ScanMsg(MessageType):
    scan_vectors:List[Vector3D]

@dataclass
class OdometryMsg(MessageType):
    x:float
    y:float
    z:float
    yaw:float
    pitch:float
    roll:float

@dataclass
class SimpleMsg(MessageType):
    message:str
    utc_time:str