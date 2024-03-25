import socket
import time
from typing import List
import obeyon_rfs as orfs
# from obeyon_rfs.Socket import RFS_CoreServerSocket, RFS_CoreToCommObjClientSocket
# from obeyon_rfs.SocketType import *
from pydantic import ValidationError,BaseModel
import threading


core_server_socket:orfs.CoreServerSocket = None
core_to_comm_obj_client_sockets:List[orfs.CoreToCommObjClientSocket] = []


def forward_to_comm_obj(request, client_socket:orfs.CoreToCommObjClientSocket):
    try:
        client_socket.renew_socket()
        client_socket.send(request.model_dump_json())
    except ConnectionRefusedError as e:
        try:
            core_to_comm_obj_client_sockets.remove(client_socket)
        except ValueError as e: #can't use    x in list => remove x  due to multithread
            pass
        print("Connection refused. This communication object's socket is removed")
        # raise e
        
    except socket.socket as e:
        if e.errno==10061:
            try:
                core_to_comm_obj_client_sockets.remove(client_socket)
            except ValueError as e: #can't use    x in list => remove x  due to multithread
                pass
            print("Connection refused. This communication object's socket is removed")
            # raise e
            


    
def start_core(args:orfs.InitArgs=None):
    orfs.init(args)
    global core_server_socket
    global core_to_comm_obj_client_sockets

    core_server_socket= orfs.CoreServerSocket(
        orfs._init_args.ORFS_CORE_HOST,
        orfs._init_args.ORFS_CORE_PORT
    )
    print(f"Core is started at {orfs._init_args.ORFS_CORE_HOST}:{orfs._init_args.ORFS_CORE_PORT}...")
    while True:
        json_dict=core_server_socket.recv_json()
        if json_dict is None:
            continue

        if orfs.validable_check(orfs.RFS_Socket_Request_Register, json_dict) == True:
            request = orfs.Socket_Request_Register(**json_dict)
            if request.request_type in [
                orfs.Socket_RequestType.REGISTER_PUBLISHER,
                orfs.Socket_RequestType.REGISTER_SUBSCRIBER,
                orfs.Socket_RequestType.REGISTER_SERVICE_SERVER,
                orfs.Socket_RequestType.REGISTER_SERVICE_CLIENT,
                orfs.Socket_RequestType.REGISTER_ACTION_SERVER,
                orfs.Socket_RequestType.REGISTER_ACTION_CLIENT,
                orfs.Socket_RequestType.REGISTER_ACTION_SUBSCRIBER
            ]:  
                server_socket_host = request.request_content.server_socket_host
                server_socket_port = request.request_content.server_socket_port
                core_to_comm_obj_client_socket = \
                    orfs.CoreToCommObjClientSocket(
                        server_socket_host,
                        server_socket_port
                    )
                core_to_comm_obj_client_sockets.append(core_to_comm_obj_client_socket)
                print(f"New communication object {request.request_type.name} is registered, its server => {server_socket_host}:{server_socket_port}")

        elif orfs.validable_check(orfs.RFS_Socket_Request_Communication, json_dict) == True:
            request = orfs.RFS_Socket_Request_Communication(**json_dict)
            if request.request_type in [
                orfs.Socket_RequestType.PUBLISH,
                orfs.Socket_RequestType.SERVICE_REQUEST,
                orfs.Socket_RequestType.SERVICE_RESPONSE,
                orfs.Socket_RequestType.ACTION_REQUEST,
                orfs.Socket_RequestType.ACTION_FEEDBACK,
                orfs.Socket_RequestType.ACTION_RESULT
            ]:
                print("forwarding ",request)
                tasks=[]
                for client_socket in core_to_comm_obj_client_sockets:
                    print(client_socket.server_host,client_socket.server_port)
                    task = threading.Thread(target=client_socket.send,args=(request.model_dump_json()))
                    task.start()
                    tasks.append(task)