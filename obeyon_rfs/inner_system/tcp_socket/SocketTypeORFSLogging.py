from enum import Enum
from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Socket_RequestType(str,Enum):
    DIRECT_FORWARD_LOG = "DIRECT_FORWARD_LOG"

class Socket_RequestFrom(BaseModel):
    request_from_host:str
    request_from_port:int

class Socket_RequestContent(BaseModel):
    log:str

class Socket_Request(BaseModel):
    request_type:Socket_RequestType
    request_name:str
    request_id:UUID = Field(default_factory=uuid4)
    request_content:Dict[str,Any]
    request_from:Socket_RequestFrom
