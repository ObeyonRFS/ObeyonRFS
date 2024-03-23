
import time
from typing import List
import obeyon_rfs
from obeyon_rfs.Socket import RFS_CoreServerSocket, RFS_CoreToCommObjClientSocket
from obeyon_rfs.SocketType import *
from pydantic import ValidationError,BaseModel
import threading


core_server_socket:RFS_CoreServerSocket = None
core_to_comm_obj_client_sockets:List[RFS_CoreToCommObjClientSocket] = []

def validable_check(model:BaseModel, data:Dict[str,Any]):
    try:
        model(**data)
    except ValidationError as e:
        # print(e)
        return False
    return True

def forward_to_comm_obj(request, client_socket:RFS_CoreToCommObjClientSocket):
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
            


    
def start_core():
    global core_server_socket
    core_server_socket= RFS_CoreServerSocket()
    # print("Core is started at ",RFS.get_core_host(),RFS.get_core_port(),"...")
    print(f"Core is started at {obeyon_rfs.get_core_host()}:{obeyon_rfs.get_core_port()}...")

    while True:
        core_server_socket.recv() #Command the socket to receive data
        # print("stocked_msg",core_server_socket.stocked_msg)
        json_dict=core_server_socket.analyze_stocked_msg()
        # print("json_dict",json_dict)
        # print(json_dict)
        # print(core_to_comm_obj_client_sockets)
        # for client_socket in core_to_comm_obj_client_sockets:
        #     print(client_socket.server_host,client_socket.server_port)
        if json_dict is None:
            continue
        # print(json_dict)


        if validable_check(RFS_Socket_Request_Register, json_dict) == True:
            request = RFS_Socket_Request_Register(**json_dict)
            if request.request_type in [
                RFS_Socket_RequestType.REGISTER_PUBLISHER,
                RFS_Socket_RequestType.REGISTER_SUBSCRIBER,
                RFS_Socket_RequestType.REGISTER_SERVICE_SERVER,
                RFS_Socket_RequestType.REGISTER_SERVICE_CLIENT,
                RFS_Socket_RequestType.REGISTER_ACTION_SERVER,
                RFS_Socket_RequestType.REGISTER_ACTION_CLIENT,
                RFS_Socket_RequestType.REGISTER_ACTION_SUBSCRIBER
            ]:  
                server_socket_host = request.request_content.server_socket_host
                server_socket_port = request.request_content.server_socket_port
                core_to_comm_obj_client_socket = \
                    RFS_CoreToCommObjClientSocket(
                        server_socket_host,
                        server_socket_port
                    )
                core_to_comm_obj_client_sockets.append(core_to_comm_obj_client_socket)
                print(f"New communication object {request.request_type.name} is registered, its server => {server_socket_host}:{server_socket_port}")
        elif validable_check(RFS_Socket_Request_Publish, json_dict) == True:
            request = RFS_Socket_Request_Publish(**json_dict)
            #forward request to the subscriber (basically forward to all)
            #and forward in parallel
            print("forwarding ",request)
            tasks=[]
            for client_socket in core_to_comm_obj_client_sockets:
                print(client_socket.server_host,client_socket.server_port)
                task = threading.Thread(target=forward_to_comm_obj,args=(request,client_socket))
                task.start()

                
        
            
        
        

            # if request.request_type == RFS.SERVICE_REQUEST:
            #     pass
            # elif request.request_type == RFS.SERVICE_RESPONSE:
            #     pass
            # elif request.request_type == RFS.SERVICE_RESPONSE_CONNECTED:
            #     pass
            # elif request.request_type == RFS.ACTION_GOAL:
            #     pass
            # elif request.request_type == RFS.ACTION_RESULT:
            #     pass
            # elif request.request_type == RFS.ACTION_FEEDBACK:
            #     pass
            # else:
            #     pass


        pass