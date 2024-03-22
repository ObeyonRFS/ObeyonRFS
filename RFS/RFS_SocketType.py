import random
from typing import Any, Dict
from typing_extensions import Literal
from pydantic import BaseModel, Field
from enum import Enum
import socket
import RFS

from RFS.comm_type.msgs import MessageType
from RFS.comm_type.srvs import ServiceType, ServiceRequestType, ServiceResponseType

class RFS_Socket_RequestType(str, Enum):
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
    SERVICE_RESPONSE_CONNECTED = "service_response_connected"
    ACTION_GOAL = "action_goal"
    ACTION_RESULT = "action_result"
    ACTION_FEEDBACK = "action_feedback"
    #unregister is made by the server.
    #The client does not need to send this request
    #That is when comm obj getting deleted

class RFS_Socket_RequestContent(BaseModel):
    pass
class RFS_Socket_RequestFrom(BaseModel):
    node_name:str
    host:str
    port:int
    
class RFS_Socket_Request(BaseModel):
    request_type:RFS_Socket_RequestType
    request_name:str    #name of service,topic,action
    request_id:int
    request_content:RFS_Socket_RequestContent
    request_from:RFS_Socket_RequestFrom
    def __init__(self,**data):
        if "request_id" not in data:
            data["request_id"] = RFS.generate_random_id()
        # print(data)
        super().__init__(**data)

class RFS_Socket_RequestContent_Register(RFS_Socket_RequestContent):
    server_socket_host:str
    server_socket_port:int

class RFS_Socket_Request_Register(RFS_Socket_Request):
    request_content: RFS_Socket_RequestContent_Register

class RFS_Socket_Request_RegisterPublisher(RFS_Socket_Request_Register):
    request_type:RFS_Socket_RequestType = RFS_Socket_RequestType.REGISTER_PUBLISHER

class RFS_Socket_Request_RegisterSubscriber(RFS_Socket_Request_Register):
    request_type:RFS_Socket_RequestType = RFS_Socket_RequestType.REGISTER_SUBSCRIBER

class RFS_Socket_Request_RegisterServiceServer(RFS_Socket_Request_Register):
    request_type:RFS_Socket_RequestType = RFS_Socket_RequestType.REGISTER_SERVICE_SERVER

class RFS_Socket_Request_RegisterServiceClient(RFS_Socket_Request_Register):
    request_type:RFS_Socket_RequestType = RFS_Socket_RequestType.REGISTER_SERVICE_CLIENT


class RFS_Socket_Request_Publish(RFS_Socket_Request):
    request_type:Literal[RFS_Socket_RequestType.PUBLISH] = RFS_Socket_RequestType.PUBLISH
    request_content: Dict[str,Any]

class RFS_Socket_Request_ServiceRequest(RFS_Socket_Request):
    request_type:Literal[RFS_Socket_RequestType.SERVICE_REQUEST] = RFS_Socket_RequestType.SERVICE_REQUEST
    request_content: Dict[str,Any]

class RFS_Socket_Request_ServiceResponse(RFS_Socket_Request):
    request_type:Literal[RFS_Socket_RequestType.SERVICE_RESPONSE] = RFS_Socket_RequestType.SERVICE_RESPONSE
    request_content: Dict[str,Any]


