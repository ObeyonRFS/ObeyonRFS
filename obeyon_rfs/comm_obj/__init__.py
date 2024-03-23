from typing import Callable
import obeyon_rfs

from obeyon_rfs.RFS_Socket import RFS_CommObjServerSocket
from obeyon_rfs.RFS_Socket import RFS_CommObjToCoreClientSocket


from obeyon_rfs.comm_type.msgs import MessageType
from obeyon_rfs.comm_type.srvs import ServiceRequestType,ServiceResponseType,ServiceType
from obeyon_rfs.comm_type.actions import ActionType,ActionRequestType,ActionFeedbackType,ActionResultType




class CommObj():#communication object
    def __init__(self):
        self.host = obeyon_rfs.get_current_device_ip()
        self.port = obeyon_rfs.generate_random_port(obeyon_rfs.get_current_device_ip())
        print(f"host: {self.host}, port: {self.port}")
        self.server_socket = RFS_CommObjServerSocket(self.host, self.port)
        self.client_to_core_socket = RFS_CommObjToCoreClientSocket()
    def obtain_json(self):
        return self.server_socket.analyze_stocked_msg()
    

class FutureHandle():#future handling for action 
    def __init__(self,
                **kwargs
                ):
        for key, value in kwargs.items():
            setattr(self, key, value)

class FutureHandleSubscriber(FutureHandle):
    def __init__(self,
                 on_received_msg:Callable[[bool],None],
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.on_received_msg = on_received_msg




class FutureHandleServiceClient(FutureHandle):
    def __init__(self,
                 on_request_sent:Callable[[ServiceRequestType],None],
                 on_connected:Callable[[ServiceRequestType],None],
                 on_timeout:Callable[[bool],None],
                 on_timeout_connected:Callable[[ServiceRequestType],None],
                 on_timeout_not_connected:Callable[[ServiceRequestType],None],
                 on_response:Callable[[ServiceResponseType],None],
                 on_finished:Callable[[None],None],
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.on_request_sent = on_request_sent
        self.on_connected = on_connected
        self.on_timeout = on_timeout
        self.on_timeout_connected = on_timeout_connected
        self.on_timeout_not_connected = on_timeout_not_connected
        self.on_response = on_response
        self.on_finished = on_finished

class FutureHandleServiceServer(FutureHandle):
    def __init__(self,
                 on_request_received:Callable[[ServiceRequestType],None],
                 on_timeout_excceded:Callable[[ServiceRequestType],None],
                 on_response:Callable[[ServiceResponseType],None],
                 on_finished:Callable[[None],None],
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.on_request = on_request
        self.on_response = on_response

class FutureHandleAction(FutureHandle):
    def __init__(self,
                 on_request:Callable[[bool],None],
                 on_result:Callable[[bool],None],
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.on_result = on_result

