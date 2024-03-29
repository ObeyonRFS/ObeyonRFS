from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Self
from uuid import UUID, uuid4
from pydantic import BaseModel, Extra, Field
import pickle
import base64


class ORFS_Component:
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
    REGISTER_NODE = 'REGISTER_NODE'
    PUBLISH = 'PUBLISH'
    SERVICE_REQUEST = 'SERVICE_REQUEST'
    SERVICE_RESPONSE = 'SERVICE_RESPONSE'
    ACTION_REQUEST = 'ACTION_REQUEST'
    ACTION_FEEDBACK = 'ACTION_FEEDBACK'
    ACTION_RESULT = 'ACTION_RESULT'
    CORE_PING = 'CORE_PING'
    CORE_PONG = 'CORE_PONG'

@dataclass
class ORFS_Message:
    message_type: ORFS_MessageType
    message_name: str   #like topic,srv_name,action_name
    message_content: Any
    node_name: str
    node_receiver_host: str
    node_receiver_port: int
    #responable by writer only. So no use
    # client_host: str
    # client_port: int
    message_uuid: UUID = field(default_factory=uuid4)
    def _serialize(self)->bytes:
        return pickle.dumps(self)
    def base64_encode(self)->bytes:
        return base64.b64encode(self._serialize())
    @staticmethod
    def _deserialize(data:bytes)->'ORFS_Message':
        return pickle.loads(data)
    @staticmethod
    def base64_decode(data:bytes)->'ORFS_Message':
        data=data.strip()
        try:
            return pickle.loads(base64.b64decode(data))
        except Exception as e:
            print(repr(e))
            return None



from obeyon_rfs.components.nodes import *
from obeyon_rfs.components.communicators import *