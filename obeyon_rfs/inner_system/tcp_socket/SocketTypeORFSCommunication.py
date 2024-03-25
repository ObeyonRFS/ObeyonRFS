import datetime
import random
import time
from typing import Any, Dict
from typing_extensions import Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import socket
import obeyon_rfs
from obeyon_rfs.interface_system.time import get_UTC_timestamp

class Socket_RequestType(str, Enum):
    #register type
    REGISTER_PUBLISHER = "register_publisher"
    REGISTER_SUBSCRIBER = "register_subscriber"
    REGISTER_SERVICE_SERVER = "register_service_server"
    REGISTER_SERVICE_CLIENT = "register_service_client"
    REGISTER_ACTION_SERVER = "register_action_server"
    REGISTER_ACTION_CLIENT = "register_action_client"
    REGISTER_ACTION_SUBSCRIBER = "register_action_subscriber"
    #communication type
    PUBLISH = "publish"
    SERVICE_REQUEST = "service_request"
    SERVICE_RESPONSE = "service_response"
    ACTION_REQUEST = "action_request"
    ACTION_FEEDBACK = "action_feedback"
    ACTION_RESULT = "action_result"
    #unregister is made by the server.
    #The client does not need to send this request
    #That is when comm obj getting deleted

class Socket_RequestInfo(BaseModel):
    request_type:Socket_RequestType
    request_name:str #name of service,topic,action
    request_id:UUID = Field(default_factory=uuid4)
    request_start_UTCtimestamp:float = Field(default_factory=get_UTC_timestamp)
    request_timeout:float = 1.0

class Socket_RequestFrom(BaseModel):
    node_name:str
    host:str
    port:int
    
class Socket_Request(BaseModel):
    request_info: Socket_RequestInfo
    request_content: Dict[str,Any]
    request_from: Socket_RequestFrom


class Socket_RequestContent_Register(BaseModel):
    server_socket_host:str
    server_socket_port:int

class Socket_Request_Register(Socket_Request):
    request_info : Socket_RequestInfo
    request_content : Socket_RequestContent_Register

    @field_validator("request_info")
    def validate_request_info(cls, value):
        valid_types = [
            Socket_RequestType.REGISTER_PUBLISHER,
            Socket_RequestType.REGISTER_SUBSCRIBER,
            Socket_RequestType.REGISTER_SERVICE_SERVER,
            Socket_RequestType.REGISTER_SERVICE_CLIENT,
            Socket_RequestType.REGISTER_ACTION_SERVER,
            Socket_RequestType.REGISTER_ACTION_CLIENT,
            Socket_RequestType.REGISTER_ACTION_SUBSCRIBER,
        ]
        if value.request_type not in valid_types:
            raise ValueError("Invalid request type")
        return value

class Socket_Request_Communication(Socket_Request):
    request_info: Socket_RequestInfo

    @field_validator("request_info")
    def validate_request_info(cls, value):
        valid_types = [
            Socket_RequestType.PUBLISH,
            Socket_RequestType.SERVICE_REQUEST,
            Socket_RequestType.SERVICE_RESPONSE,
            Socket_RequestType.ACTION_REQUEST,
            Socket_RequestType.ACTION_FEEDBACK,
            Socket_RequestType.ACTION_RESULT,
        ]
        if value.request_type not in valid_types:
            raise ValueError("Invalid request type")
        return value


