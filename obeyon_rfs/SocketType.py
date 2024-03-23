import random
from typing import Any, Dict
from typing_extensions import Literal
from pydantic import BaseModel, Field
from enum import Enum
import socket
import obeyon_rfs

from obeyon_rfs.comm_type.msgs import MessageType
from obeyon_rfs.comm_type.srvs import ServiceType, ServiceRequestType, ServiceResponseType

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

class Socket_RequestFrom(BaseModel):
    node_name:str
    host:str
    port:int
    
class Socket_Request(BaseModel):
    request_type:Socket_RequestType
    request_name:str #name of service,topic,action
    request_id:int
    request_content:Dict[str,Any]
    request_from:Socket_RequestFrom

    def __init__(self,**data):
        if "request_id" not in data:
            data["request_id"] = obeyon_rfs.generate_random_id()
        # print(data)
        super().__init__(**data)


class Socket_RequestContent_Register(BaseModel):
    server_socket_host:str
    server_socket_port:int

class Socket_Request_Register(Socket_Request):
    request_content: Socket_RequestContent_Register

class Socket_Request_Communication(Socket_Request):
    request_type:Literal[
        Socket_RequestType.PUBLISH,
        Socket_RequestType.SERVICE_REQUEST,
        Socket_RequestType.SERVICE_RESPONSE,
        Socket_RequestType.ACTION_REQUEST,
        Socket_RequestType.ACTION_FEEDBACK,
        Socket_RequestType.ACTION_RESULT,
    ]
    request_content: Dict[str, Any]


