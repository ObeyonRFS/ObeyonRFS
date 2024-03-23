from enum import Enum
import threading
import time
from typing import Any, Callable, Dict, Tuple

import obeyon_rfs
from pydantic import BaseModel

from obeyon_rfs.comm_type.srvs import ServiceRequestType, ServiceType

from obeyon_rfs.RFS_SocketType import RFS_Socket_Request_RegisterServiceClient, RFS_Socket_Request_RegisterServiceServer, RFS_Socket_Request_ServiceRequest, RFS_Socket_Request_ServiceResponse, RFS_Socket_RequestContent_Register, RFS_Socket_RequestFrom, RFS_Socket_RequestType
from obeyon_rfs.comm_type.msgs import MessageType
from obeyon_rfs.comm_obj.CommObj import CommObj



class ServiceRequestStatus(int,Enum):
    REQUEST_SENT = 0
    TIMEOUT = 1
    RESPOND = 2
    REQUEST_ID_UNAVAILABLE = 3

class ServiceConnectionStatus(int,Enum):
    CONNECTED=0
    NOT_CONNECTED=1


class ServiceRequestInfo(BaseModel):
    request_id:int
    request:ServiceRequestType
    timeout:int
    connected:bool=False
    request_time:float

class ServiceClient(CommObj):
    def __init__(self,node,service_name:str, service_type:ServiceType, callback:Callable[[MessageType],None]):
        super().__init__()
        self.node = node
        self.service_name = service_name
        self.service_type = service_type
        self.service_request_type = service_type().request.__class__
        self.service_response_type = service_type().response.__class__
        self.callback = callback
        self.register_to_core()
        self.requests_info:Dict[int,ServiceRequestInfo]={}
        self.responses:Dict[int,Any]={}
        self.obtain_response_loop_task=threading.Thread(target=self.obtain_responses_loop,daemon=True)
        self.obtain_response_loop_task.start()
    def register_to_core(self):
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        self.client_to_core_socket.send(
            RFS_Socket_Request_RegisterServiceClient(
                request_name=self.service_name,
                request_content=RFS_Socket_RequestContent_Register(
                    server_socket_host=self.host,
                    server_socket_port=self.port
                ),
                request_from=RFS_Socket_RequestFrom(
                    #It's hard for the server to response back really
                    #but provided more information is always good
                    node_name=self.node.name,
                    host=request_from_host,
                    port=request_from_port
                )
            ).model_dump_json()
        )
    def request_async(self,request:ServiceRequestType,timeout=None) -> Tuple[ServiceRequestStatus,ServiceConnectionStatus,int]:
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        socket_request=RFS_Socket_Request_ServiceRequest(
                request_name=self.service_name,
                request_content=request,
                request_from=RFS_Socket_RequestFrom(
                    #It's hard for the server to response back really
                    #but provided more information is always good
                    node_name=self.node.name,
                    host=request_from_host,
                    port=request_from_port
                )
            )
        request_id=socket_request.request_id
        self.client_to_core_socket.send(socket_request.model_dump_json())
        self.requests_info[request_id]=ServiceRequestInfo(
            request_id=request_id,
            request=request,
            timeout=timeout,
            connected=False,
            request_time=time.time())
        self.responses[request_id]=None
        return ServiceRequestStatus.REQUEST_SENT,ServiceConnectionStatus.NOT_CONNECTED,socket_request.request_id
    def get_response_async(self,request_id:int) -> Tuple[ServiceRequestStatus,ServiceConnectionStatus,Any]:
        status1=ServiceRequestStatus.REQUEST_ID_UNAVAILABLE
        status2=ServiceConnectionStatus.NOT_CONNECTED
        response_value:self.service_response_type=None

        if request_id not in self.requests_info:
            return status1,status2,response_value
        request_info=self.requests_info[request_id]

        status2 = ServiceConnectionStatus.CONNECTED if request_info.connected else ServiceConnectionStatus.NOT_CONNECTED

        if time.time()-request_info.request_time>request_info.timeout:
            status1=ServiceRequestStatus.TIMEOUT
        else:
            if request_info.connected:
                response_value=self.responses[request_id]
                status1=ServiceRequestStatus.RESPOND

                #make a deletion?
                del self.requests_info[request_id]
                del self.responses[request_id]
            else:
                status1=ServiceRequestStatus.REQUEST_SENT
        return status1,status2,response_value
    def get_response(self):
        while True:
            status1,status2,response_value=self.get_response_async()
            if status1==ServiceRequestStatus.RESPOND:
                return response_value
            if status1==ServiceRequestStatus.TIMEOUT:
                return None
            if status1==ServiceRequestStatus.REQUEST_ID_UNAVAILABLE:
                return None
    def obtain_responses_loop(self):
        while True:
            request_dict = self.obtain_json()
            request=RFS_Socket_Request_ServiceResponse(request_dict)
            #verify condition
            if request.request_type == RFS_Socket_RequestType.SERVICE_RESPONSE:
                self.responses[request.request_id]=request.request_content
            if request.request_type == RFS_Socket_RequestType.SERVICE_RESPONSE_CONNECTED:
                self.requests_info[request.request_id].connected=True

class ServiceServer(CommObj):
    def __init__(self,node,service_name:str, service_type:ServiceType, callback:Callable[[ServiceType],MessageType]):
        super().__init__()
        self.node = node
        self.service_name = service_name
        self.service_type = service_type
        self.service_response_type = service_type().response.__class__
        self.callback = callback
        self.register_to_core()
        self.service_loop_task=threading.Thread(target=self.service_loop,daemon=True)
        self.service_loop_task.start()
    def register_to_core(self):
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        self.client_to_core_socket.send(
            RFS_Socket_Request_RegisterServiceServer(
                request_name=self.service_name,
                request_id=obeyon_rfs.generate_random_id(),
                request_content=RFS_Socket_RequestContent_Register(
                    server_socket_host=self.host,
                    server_socket_port=self.port
                ),
                request_from=RFS_Socket_RequestFrom(
                    #It's hard for the server to response back really
                    #but provided more information is always good
                    node_name=self.node.name,
                    host=request_from_host,
                    port=request_from_port
                )
            ).model_dump_json()
        )
    def service_loop(self):
        while True:
            request_dict = self.obtain_json()
            request=RFS_Socket_Request_ServiceRequest(request_dict)
            #verify condition
            if request.request_type == RFS_Socket_RequestType.SERVICE_REQUEST:
                response=self.callback(request.request_content)
                response=self.service_type(response)
                self.client_to_core_socket.renew_socket()
                request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
                self.client_to_core_socket.send(
                    RFS_Socket_Request_ServiceResponse(
                        request_name=self.service_name,
                        request_id=obeyon_rfs.generate_random_id(),
                        request_content=response,
                        request_from=RFS_Socket_RequestFrom(
                            #It's hard for the server to response back really
                            #but provided more information is always good
                            node_name=self.node.name,
                            host=request_from_host,
                            port=request_from_port
                        )
                    ).model_dump_json()
                )