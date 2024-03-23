from typing import Callable
from obeyon_rfs.comm_obj.CommObj import *
from pydantic import BaseModel

from obeyon_rfs.RFS_SocketType import RFS_Socket_Request_Publish, RFS_Socket_Request_RegisterPublisher, RFS_Socket_Request_RegisterSubscriber, RFS_Socket_RequestContent, RFS_Socket_RequestContent_Register, RFS_Socket_RequestFrom, RFS_Socket_RequestType
from obeyon_rfs.comm_type.msgs import MessageType

import threading

class Publisher(CommObj):
    def __init__(self,node,topic_name:str, msg_type:MessageType):
        super().__init__()
        self.node = node
        self.topic_name = topic_name
        self.msg_type = msg_type
        self.register_to_core()
        self.check_core_loop_task=threading.Thread(target=self.check_core_loop,daemon=True)
        self.check_core_loop_task.start()
    def register_to_core(self):
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        self.client_to_core_socket.send(
            RFS_Socket_Request_RegisterPublisher(
                request_name=self.topic_name,
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
    def publish(self,msg:MessageType):
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        self.client_to_core_socket.send(
            RFS_Socket_Request_Publish(
                request_type=RFS_Socket_RequestType.PUBLISH,
                request_name=self.topic_name,
                request_content=msg.model_dump(),
                request_from=RFS_Socket_RequestFrom(
                    #It's hard for the server to response back really
                    #but provided more information is always good
                    node_name=self.node.name,
                    host=request_from_host,
                    port=request_from_port
                )
            ).model_dump_json()
        )
    def check_core_loop(self):
        while True:
            request_dict = self.obtain_json()
            if request_dict is None:
                continue
            if request_dict is not None:
                continue

class Subscriber(CommObj):
    def __init__(self,node,topic_name:str, msg_type:BaseModel,callback:Callable[[MessageType],None]):
        super().__init__()
        self.node = node
        self.topic_name = topic_name
        self.msg_type = msg_type
        self.callback = callback
        self.register_to_core()
        self.subscribe_loop_task=threading.Thread(target=self.subscribe_loop,daemon=True)
        self.subscribe_loop_task.start()
        
    def register_to_core(self):
        self.client_to_core_socket.renew_socket()
        request_from_host,request_from_port = self.client_to_core_socket.get_host_port()
        # print(f"registering publisher {self.topic_name} to core at {self.host}:{self.port}...")
        self.client_to_core_socket.send(
            RFS_Socket_Request_RegisterSubscriber(
                # request_type=RFS_Socket_RequestType.REGISTER_SUBSCRIBER,
                request_name=self.topic_name,
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
    def subscribe_loop(self):
        while True:
            request_dict = self.obtain_json()
            
            # print(request_dict)
            if request_dict is None:
                continue
            request=RFS_Socket_Request_Publish(**request_dict)
            #verify condition
            if request.request_type in [RFS_Socket_RequestType.PUBLISH]:
                msg=self.msg_type(**request.request_content)
                self.callback(msg)