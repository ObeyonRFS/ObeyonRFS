import json
import random
import socket
import threading
import time
from typing import Any, Dict, Type

from pydantic import BaseModel, ValidationError


class ClientSocket:
    def __init__(self, dest_host:str, dest_port:int):
        self.server_host = dest_host
        self.server_port = dest_port
        self.socket:socket.socket = None
        self.socket.settimeout(0.00001)

    def renew_socket(self):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.server_host, self.server_port))
        except socket.error as e:
            if e.errno==10061:
                raise ConnectionRefusedError(repr(e))
            else:
                raise e
        except ConnectionRefusedError as e:
            raise e

    def send(self, data:str):
        if type(data) is str:
            data+="\n"
            data = data.encode()
        else:
            raise TypeError("data must be a string")

        try:
            self.socket.sendall(data)
        except socket.error as e:
            if e.errno==10061:
                raise ConnectionRefusedError(repr(e))
        except ConnectionRefusedError as e:
            raise e
        
    def send_dict(self, data:Dict[str, Any]):
        data_str = json.dumps(data)
        self.send(data_str)
        
    def send_model(self, data:BaseModel):
        data_str = data.model_dump_json()
        self.send(data_str)
    
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


class ServerSocket:
    def __init__(self, server_host:str, server_port:int=None):
        self.host = server_host
        if self.port is None:
            self.port = self._generate_random_port(self.host)
        else:
            self.port = server_port
        self.socket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(socket.SOMAXCONN) # queue of request inf
        self.socket.setblocking(False) # no blocking just throw error when found nothing
        self.socket.settimeout(0.00001) # set timeout for recv

        self.stocked_msg:str = ""
        self.recv_loop_task=threading.Thread(target=self.recv_loop,daemon=True)
        self.recv_loop_task.start()

    def _is_port_in_use(self,ip_address, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((ip_address, port))
            except OSError:
                return True  # Port is in use
            else:
                return False  # Port is available
    
    def _generate_random_port(self,ip_address):
        while True:
            port = random.randint(1024, 65535)
            if not self._is_port_in_use(ip_address, port):
                return port
    def recv_loop(self):
        while True:
            self.recv()
            time.sleep(0.00001)
    def recv(self):
        try:
            self.conn, self.addr = self.socket.accept()
        except socket.timeout:
            return None

        try:
            recv_msg = self.conn.recv(4096).decode()+"\n"
            # Protocol : The received message is json
            self.stocked_msg += recv_msg
        except socket.timeout as e:
            return None
        except socket.error as e:
            if e.errno==10054:
                #empty of recv
                return None
            if e.errno==10061:
                # Connection refused
                raise ConnectionRefusedError(repr(e))
            else:
                raise e
        except ConnectionRefusedError as e:
            raise e
    
    
    def recv_dict(self) -> Dict[str, Any]:
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
            
    def recv_model(self,model_type:Type[BaseModel]) -> BaseModel:
        try:
            return model_type.model_validate(self.recv_dict())
        except ValidationError as e:
            return None
        

