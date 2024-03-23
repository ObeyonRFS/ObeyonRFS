from typing import Callable
import obeyon_rfs

from obeyon_rfs.Socket import RFS_CommObjServerSocket
from obeyon_rfs.Socket import RFS_CommObjToCoreClientSocket


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
    

