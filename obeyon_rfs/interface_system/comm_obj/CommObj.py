import random
import time
from typing import Callable

from obeyon_rfs.inner_system.tcp_socket import (
    SocketBase,
    SocketTypeORFSCommunication,
    SocketTypeORFSLogging
)
from obeyon_rfs.inner_system.tcp_socket.SocketBase import (
    ServerSocket,
    ClientSocket
)


# import obeyon_rfs
# from obeyon_rfs.interface_system.comm_type.msgs import MessageType
# from obeyon_rfs.interface_system.comm_type.srvs import ServiceRequestType,ServiceResponseType,ServiceType
# from obeyon_rfs.interface_system.comm_type.actions import ActionType,ActionRequestType,ActionFeedbackType,ActionResultType


class CommObj():#communication object
    #every communication object must have its own server socket
    #every communication object should 
    def __init__(self,comm_obj_server_host:str,core_server_host:str,core_server_port:int):
        self.server_for_core_socket = ServerSocket(comm_obj_server_host, None)
        self.client_to_core_socket = ClientSocket(core_server_host,core_server_port)
    def obtain_json(self):
        return self.server_socket.recv_json()
    

    
    # def check_core_loop(self):
    #     while True:
    #         self.client_check_core_socket.renew_socket()
    #         self.client_check_core_socket.send(
    #             obeyon_rfs.Socket_Request(
    #                 request_type=obeyon_rfs.Socket_RequestType.CHECK_CORE,
    #                 request_name="",
    #                 request_content={},
    #                 request_from=obeyon_rfs.Socket_RequestFrom(
    #                     node_name="",
    #                     host="",
    #                     port=0
    #                 )
    #             ).model_dump_json()
    #         )

    #         time.sleep(0.5)