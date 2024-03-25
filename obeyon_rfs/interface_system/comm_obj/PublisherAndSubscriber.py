from typing import Callable, Optional, Type
from pydantic import BaseModel
import threading
from obeyon_rfs.interface_system.comm_obj.CommObj import CommObj
from obeyon_rfs.interface_system.comm_type.msgs import MessageType
from obeyon_rfs.interface_system.event import (
    EventHandlePublisher,
    EventHandleSubscriber,
)
from obeyon_rfs.inner_system.tcp_socket.SocketTypeORFSCommunication import *

from obeyon_rfs.node import Node


class Publisher(CommObj):
    def __init__(self,
                 comm_obj_server_host:str,
                 core_server_host:str,
                 core_server_port:int,
                 node:Node,
                 topic_name:str, 
                 msg_type:Type[MessageType],
                 event_handle:Optional[EventHandlePublisher],
                 ):
        super().__init__(
            comm_obj_server_host,
            core_server_host,
            core_server_port
        )
        self.node = node
        self.topic_name = topic_name
        self.msg_type = msg_type
        self.event_handle = event_handle
        self.register_to_core()
    def register_to_core(self):
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        self.client_to_core_socket.send_model(
            Socket_Request_Register(
                request_info=Socket_RequestInfo(
                    request_type=Socket_RequestType.REGISTER_PUBLISHER,
                    request_name=self.topic_name,
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
    def publish(self,msg:MessageType):
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        self.client_to_core_socket.send_model(
            Socket_Request_Communication(
                request_info=Socket_RequestInfo(
                    request_type=Socket_RequestType.PUBLISH,
                    request_name=self.topic_name,
                ),
                request_content=msg.model_dump(),
                request_from=Socket_RequestFrom(
                    node_name=self.node.name,
                    host=request_from_host,
                    port=request_from_port
                )
            )
        )
        self.event_handle.on_msg_sent()

class Subscriber(CommObj):
    def __init__(self,
                 comm_obj_server_host:str,
                 core_server_host:str,
                 core_server_port:int,
                 node:Node,
                 topic_name:str,
                 msg_type:Type[MessageType],
                 callback:Callable[[MessageType],None],
                 event_handle:Optional[EventHandleSubscriber],
                 ):
        super().__init__(
            comm_obj_server_host,
            core_server_host,
            core_server_port
        )
        self.node = node
        self.topic_name = topic_name
        self.msg_type = msg_type
        self.callback = callback
        self.event_handle = event_handle
        self.register_to_core()

        self.subscribe_loop_task=threading.Thread(target=self.subscribe_loop,daemon=True)
        self.subscribe_loop_task.start()
        
    def register_to_core(self):
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        self.client_to_core_socket.send_model(
            Socket_Request_Register(
                request_info=Socket_RequestInfo(
                    request_type=Socket_RequestType.REGISTER_SUBSCRIBER,
                    request_name=self.topic_name,
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

    def subscribe_loop(self):
        while True:
            income_request:Socket_Request_Communication = self.server_for_core_socket.recv_model(Socket_Request_Communication)
            if income_request is None:
                continue
            if income_request.request_info.request_type == Socket_RequestType.PUBLISH and income_request.request_info.request_name == self.topic_name:
                msg=self.msg_type.model_validate(income_request.request_content)
                self.callback(msg)
                self.event_handle.on_msg_received(msg)