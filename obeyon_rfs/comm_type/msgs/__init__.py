from typing import List, Tuple
from pydantic import BaseModel
from obeyon_rfs.datatypes import *


class MessageType(BaseModel):
    """
    MessageType is a base class for all message types.\n
    It is used to define the message type and its content.
    """
    pass

class ScanMsg(MessageType):
    """
    Scan message type.\n
    This message type is used to represent a scan of the environment.\n
    - scan_vectors: A list of 3D vectors representing the scan points.
    """
    scan_vectors:List[Vector3D]

class OdometryMsg(MessageType):
    """
    Odometry message type.\n
    This message type is used to represent the odometry of a robot.\n
    - x: The x coordinate of the robot in meters.
    - y: The y coordinate of the robot in meters.
    - z: The z coordinate of the robot in meters.
    - yaw: The yaw angle of the robot in radians.
    - pitch: The pitch angle of the robot in radians.
    - roll: The roll angle of the robot in radians. 
    """
    x:float
    y:float
    z:float
    yaw:float
    pitch:float
    roll:float

class SimpleMsg(MessageType):
    """
    Simple message type.\n
    This message type is used to represent a simple message.\n
    - message: The message content.
    - utc_time: The UTC time of the message in ISO 8601 format.
    """
    message:str
    utc_time:str