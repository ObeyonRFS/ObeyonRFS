from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Extra, Field
import base64


class ORFS_Component:
    """
        Base class for all components in the ObeyonRFS framework.\n
        This class is used to define the common attributes and methods for all components.\n
        - parent: The parent component of this component.\n
    """
    def __init__(self,parent=None):
        self.parent=parent
    # def parent_init(self) -> Self:
    #     for k in self.model_fields.keys():
    #         if k=='parent':
    #             continue
    #         v=getattr(self,k)
    #         if v is None:
    #             continue
    #         if isinstance(v,ORFS_Component) or issubclass(v.__class__,ORFS_Component):
    #             v.parent=self
    #             v.parent_init()
    #     return self
    

class ORFS_MessageType(str,Enum):
    # REGISTER_NODE = 'REGISTER_NODE'
    PUBLISH = 'PUBLISH'
    SERVICE_REQUEST = 'SERVICE_REQUEST'
    SERVICE_RESPONSE = 'SERVICE_RESPONSE'
    ACTION_REQUEST = 'ACTION_REQUEST'
    ACTION_FEEDBACK = 'ACTION_FEEDBACK'
    ACTION_RESULT = 'ACTION_RESULT'
    CORE_PING = 'CORE_PING'
    CORE_PONG = 'CORE_PONG'
    BROADCAST_CORE_PING = 'BROADCAST_CORE_PING'
    BROADCAST_CORE_PONG = 'BROADCAST_CORE_PONG'

class ORFS_Message(BaseModel):
    """
        Message for communication between nodes
        This class is defined from pydantic.BaseModel.\n
        It is used to define the message format for communication between nodes.\n
        This class is not meant to be used directly, (The user shouldn't see this class)\n
        ---
        Fields
        ---

        - domain_name : str, default=""
          domain name of the message. which is used to identify the domain of the message.


        - message_type : ORFS_MessageType
          type of the message. which defined in ORFS_MessageType

        - message_name : str
          for example: topic (pub/sub),srv_name (srv/cli),action_name (action/cli)

        - message_content : Any
          content of the message. which can be any type.
          This will carry information of the message.

        - node_name : str
          name of the node which created this message.

        - message_former_node_tcp_host_port : str
          host and port of the node which created this message.

        - message_uuid : UUID
            uuid of the message. which is used to identify the message. (This will be auto-generated)
        
        ---
        Functions/Methods
        ---
        - ORFS_Message(---).base64_encode() -> bytes
            This function is used to encode the message to base64 format.
            This is used to send the message over the network.

        ---
        Static methods
        ---
        - ORFS_Message.base64_decode(data) -> ORFS_Message
            This function is used to decode the message from base64 format.
            This is used to receive the message over the network.
            This function will return None if the data is not a valid ORFS_Message.
            - data : bytes
              data is the base64 encoded message.
        

    """
    message_type: ORFS_MessageType
    message_name: str   #like topic,srv_name,action_name
    message_content: Any
    node_name: str
    node_receiver_host: str
    node_receiver_port: int
    #responable by writer only. So no use
    # client_host: str
    # client_port: int
    message_uuid: UUID = Field(default_factory=uuid4)
    domain_name:str = ""
    
    def base64_encode(self)->bytes:
        return base64.b64encode(self.json().encode())
    
    @staticmethod
    def base64_decode(data:bytes)->'ORFS_Message':
        data=data.strip()
        try:
            # print(data)
            json_str=base64.b64decode(data).decode()
            # print(json_str)
            return ORFS_Message.parse_raw(json_str)
        except Exception as e:
            print(repr(e))
            return None


from obeyon_rfs.components.nodes import *
from obeyon_rfs.components.communicators import *