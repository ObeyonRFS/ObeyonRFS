from enum import Enum
import threading
import time
from typing import Any, Callable, Dict, NoReturn, Optional, Tuple, Type

import obeyon_rfs
from pydantic import BaseModel

from obeyon_rfs.interface_system.comm_obj.CommObj import CommObj
from obeyon_rfs.interface_system.comm_type.srvs import (
    ServiceRequestType,
    ServiceResponseType,
    ServiceType
)
from obeyon_rfs.interface_system.event import (
    EventHandleServiceServer,
    EventHandleServiceClient
)
from obeyon_rfs.inner_system.tcp_socket.SocketTypeORFSCommunication import *
from obeyon_rfs.node import Node


class ServiceClient(CommObj):
    def __init__(self,
                 comm_obj_server_host:str,
                 core_server_host:str,
                 core_server_port:int,
                 node:Node,
                 service_name:str,
                 service_type:Type[ServiceType],
                 event_handle:Optional[EventHandleServiceClient],
                 ):
        super().__init__(
            comm_obj_server_host,
            core_server_host,
            core_server_port
        )
        self.node = node
        self.service_name = service_name
        self.service_type:Type[ServiceType] = service_type
        self.service_request_type:Type[ServiceRequestType] = service_type.request_type
        self.service_response_type:Type[ServiceResponseType] = service_type.response_type
        self.event_handle = event_handle
        self.register_to_core()
    def register_to_core(self):
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        self.client_to_core_socket.send(
            Socket_Request_Register(
                request_info=Socket_RequestInfo(
                    request_type=Socket_RequestType.REGISTER_SERVICE_CLIENT,
                    request_name=self.service_name,
                ),
                request_content=Socket_RequestContent_Register(
                    server_socket_host=self.host,
                    server_socket_port=self.port
                ),
                request_from=Socket_RequestFrom(
                    node_name=self.node.name,
                    host=request_from_host,
                    port=request_from_port
                )
            )
        )

    def is_match_request_response(self,request:Socket_Request_Communication,income_request:Socket_Request_Communication) -> bool:
        if request.request_info.request_type == Socket_RequestType.SERVICE_REQUEST\
            and income_request.request_info.request_type == Socket_RequestType.SERVICE_RESPONSE\
            and request.request_info.request_name == income_request.request_info.request_name\
            and request.request_info.request_id == income_request.request_info.request_id:
            return True
        return False
        
    def send_request(self,request:ServiceRequestType,timeout:float=1.0) -> ServiceResponseType:
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        request=Socket_Request_Communication(
                request_info=Socket_RequestInfo(
                    request_type=Socket_RequestType.SERVICE_REQUEST,
                    request_name=self.service_name,
                    request_timeout=timeout
                ),
                request_content=request.model_dump(),
                request_from=Socket_RequestFrom(
                    node_name=self.node.name,
                    host=request_from_host,
                    port=request_from_port
                )
            )
        self.client_to_core_socket.send_model(request)
        self.event_handle.on_request_sent()
        start_time=get_UTC_timestamp()
        while True:
            if get_UTC_timestamp()-start_time>timeout:
                self.event_handle.on_timeout()
                return None
            income_request:Socket_Request_Communication = self.server_for_core_socket.recv_model(Socket_Request_Communication)
            if income_request is None:
                continue
            if self.is_match_request_response(request,income_request):
                return self.service_response_type.model_validate(income_request.request_content)
    def request_async(self,request:ServiceRequestType,timeout:float=1.0):
        '''
        It's hard to design, Work in Progress
        Required community's opinion
        '''
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        self.client_to_core_socket.send(
            Socket_Request_Communication(
                request_info=Socket_RequestInfo(
                    request_type=Socket_RequestType.SERVICE_REQUEST,
                    request_name=self.service_name,
                    request_timeout=timeout
                ),
                request_content=request.model_dump(),
                request_from=Socket_RequestFrom(
                    node_name=self.node.name,
                    host=request_from_host,
                    port=request_from_port
                )
            )
        )
        self.event_handle.on_request_sent()

class ServiceServer(CommObj):
    def __init__(self,
                 comm_obj_server_host:str,
                 core_server_host:str,
                 core_server_port:int,
                 node:Node,
                 service_name:str,
                 service_type:ServiceType,
                 callback:Callable[[ServiceRequestType],ServiceResponseType],
                 event_handle:Optional[EventHandleServiceServer],
                 ):
        super().__init__(
            comm_obj_server_host,
            core_server_host,
            core_server_port
        )
        self.node = node
        self.service_name = service_name
        self.service_type:Type[ServiceType] = service_type
        self.service_request_type:Type[ServiceRequestType] = service_type().request.__class__
        self.service_response_type:Type[ServiceResponseType] = service_type().response.__class__
        self.callback = callback
        self.event_handle = event_handle

        self.register_to_core()
        self.service_server_loop_task=threading.Thread(target=self.service_server_loop,daemon=True)
        self.service_server_loop_task.start()
    def register_to_core(self):
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        self.client_to_core_socket.send(
            Socket_Request_Register(
                request_info=Socket_RequestInfo(
                    request_type=Socket_RequestType.REGISTER_SERVICE_SERVER,
                    request_name=self.service_name,
                ),
                request_content=Socket_RequestContent_Register(
                    server_socket_host=self.host,
                    server_socket_port=self.port
                ),
                request_from=Socket_RequestFrom(
                    node_name=self.node.name,
                    host=request_from_host,
                    port=request_from_port
                )
            )
        )
    def service_server_loop(self):
        while True:
            request:Socket_Request_Communication = self.server_for_core_socket.recv_model(Socket_Request_Communication)
            if request is None:
                continue
            handle_request_thread=threading.Thread(target=self.handle_request,args=(request,))
            handle_request_thread.start()
    def handle_request(self,request:ServiceRequestType) -> NoReturn:
        if request.request_info.request_type == Socket_RequestType.SERVICE_REQUEST:
            response=self.callback(self.service_request_type.model_validate(request.request_content))
            response=Socket_Request_Communication(
                request_info=Socket_RequestInfo(
                    request_type=Socket_RequestType.SERVICE_RESPONSE,
                    request_name=self.service_name,
                    request_id=request.request_info.request_id
                ),
                request_content=response.model_dump(),
                request_from=Socket_RequestFrom(
                    node_name=self.node.name,
                    host=self.host,
                    port=self.port
                )
            )
            self.client_to_core_socket.renew_socket()
            self.client_to_core_socket.send_model(response)
            self.event_handle.on_request_received()
        else:
            pass