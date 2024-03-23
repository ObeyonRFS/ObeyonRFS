import socket
from typing import Any, Dict
import json



import obeyon_rfs
from obeyon_rfs.RFS_SocketType import *




class RFS_ClientSocket:
    def __init__(self, dest_host:str, dest_port:int):
        self.server_host = dest_host
        self.server_port = dest_port
        self.socket:socket.socket = None

    def renew_socket(self):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.server_host, self.server_port))
        except ConnectionRefusedError as e:
            print("Connection refused. The RFS core is not started yet?")
            raise e
        except socket.error as e:
            if e.errno==10061:
                print("Connection refused. The RFS core is not started yet?")
                raise e
        self.socket.settimeout(0.00001)
        # print("renewed socket")

    def send(self, data:str):
        if type(data) is str:
            data+="\n"
            data = data.encode()
        else:
            raise TypeError("data must be a string")
        self.socket.sendall(data)
    def get_host_port(self):
        client_host, client_port = self.socket.getsockname()
        return client_host, client_port

    #client's recv is unreliable, as server socket have to hold client socket
    #however it is good for HTTP protocol?
    #not used for publisher/subscriber ofc
    #service and client can probably used this...But that is some dynamic model level
    #action server and action client likely not used this
    # def recv(self, size):
    #     return self.socket.recv

    # def close(self):
    #     self.socket.close()

class RFS_CommObjToCoreClientSocket(RFS_ClientSocket):
    def __init__(self):
        super().__init__(obeyon_rfs.get_core_host(), obeyon_rfs.get_core_port())

    def renew_socket(self):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.server_host, self.server_port))
        except ConnectionRefusedError as e:
            print("Connection refused. The RFS core is not started yet?")
            raise e
        except socket.error as e:
            if e.errno==10061:
                print("Connection refused. The RFS core is not started yet?")
                raise e
        self.socket.settimeout(0.00001)

class RFS_CoreToCommObjClientSocket(RFS_ClientSocket):
    def __init__(self, comm_obj_host:str, comm_obj_port:int):
        super().__init__(comm_obj_host, comm_obj_port)

    def renew_socket(self):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.server_host, self.server_port))
        except ConnectionRefusedError as e:
            raise e
        except socket.error as e:
            if e.errno==10061:
                raise e
        self.socket.settimeout(0.00001)

class RFS_ServerSocket:
    def __init__(self, server_host:str, server_port:int):
        self.host = server_host
        self.port = server_port
        self.socket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        # self.socket.listen(1000)
        # queue of request inf
        self.socket.listen(socket.SOMAXCONN)
        # no blocking just throw error when found nothing
        self.socket.setblocking(False) 
        # set timeout for recv
        self.socket.settimeout(0.00001)

        self.stocked_msg:str = ""
    def recv(self):
        try:
            self.conn, self.addr = self.socket.accept()
        except socket.timeout:
            return None
        try:
            recv_msg = self.conn.recv(1024).decode()+"\n"
            # Protocol : The received message is json
            self.stocked_msg += recv_msg
        except socket.timeout as e:
            raise e
        except socket.error as e:
            #empty of decode
            if e.errno==10054:
                print(e)
            else:
                raise e
    
    def analyze_stocked_msg(self) -> Dict[str, Any]:
        self.recv()
        #analyze the stocked message
        if self.stocked_msg:
            try:
                newline_index=self.stocked_msg.index("\n")
                msg=self.stocked_msg[:newline_index]
                #remove "\n"
                self.stocked_msg=self.stocked_msg[newline_index+1:]
                try:
                    return json.loads(msg)
                except json.JSONDecodeError as e:
                    # print(e)
                    return None
            except IndexError as e:
                return None


class RFS_CoreServerSocket(RFS_ServerSocket):
    def __init__(self):
        super().__init__(obeyon_rfs.get_core_host(), obeyon_rfs.get_core_port())




class RFS_CommObjServerSocket(RFS_ServerSocket):
    def __init__(self, server_host:str, server_port:int):
        super().__init__(
            server_host=server_host,
            server_port=server_port
        )

