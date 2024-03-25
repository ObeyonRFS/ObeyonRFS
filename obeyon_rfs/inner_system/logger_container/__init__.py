import logging
import threading
from typing import List
import obeyon_rfs as orfs
from obeyon_rfs.inner_system.tcp_socket.SocketBase import ServerSocket, ClientSocket
import obeyon_rfs.inner_system.tcp_socket.SocketTypeORFSLogging as orfs_logging_type

class LoggerContainer:
    def __init__(self, log_container_server_host:str, log_container_server_port:int):
        self.log_container_server_host = log_container_server_host
        self.log_container_server_port = log_container_server_port
        self.server_socket = ServerSocket(log_container_server_host, log_container_server_port)

        self.requested:List[orfs_logging_type.Socket_Request]=[]

        self.recv_loop_task = threading.Thread(target=self.recv_loop)
        self.recv_loop_task.start()

    def recv_loop(self):
        while True:
            request = self.server_socket.recv_model(orfs_logging_type.Socket_Request)
            if request is not None:
                self.requested.append(request)