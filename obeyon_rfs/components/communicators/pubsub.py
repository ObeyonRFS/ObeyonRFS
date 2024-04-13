from typing import TYPE_CHECKING, Any, Coroutine, Type, Callable


from obeyon_rfs.components import ORFS_Component, ORFS_MessageType, ORFS_Message
from obeyon_rfs.comm_type.msgs import MessageType
if TYPE_CHECKING:
    from obeyon_rfs.components.nodes import Node, ClientNode


class Publisher(ORFS_Component):
    def __init__(self,topic:str,msg_type:Type[MessageType]):
        super().__init__()
        self.parent:ClientNode = None
        self.topic=topic
        self.msg_type=msg_type
    def publish(self,msg:MessageType):
        if not isinstance(msg,self.msg_type):
            raise TypeError('message type is not matched')
        self.parent.sent_model_to_core(ORFS_Message(
            message_type=ORFS_MessageType.PUBLISH,
            message_name=self.topic,
            message_content=msg,
            node_name=self.parent.node_name,
            node_receiver_host=self.parent.receiver_host,
            node_receiver_port=self.parent.receiver_port
        ))
class Subscriber(ORFS_Component):
    def __init__(self,topic:str,msg_type:Type[MessageType],coroutine_callback:Callable[[],Coroutine[Any,Any,None]]=None):
        super().__init__()
        self.parent:Node = None
        self.topic=topic
        self.msg_type=msg_type
        self.coroutine_callback=coroutine_callback
    async def recv_model(self,model:ORFS_Message):
        if model.message_name!=self.topic:
            return
        await self.coroutine_callback(
            self.msg_type.validate(model.message_content)
        )
    def __repr__(self):
        return f'<Subscriber {self.topic} {self.msg_type} {self.callback}>'
    def __str__(self):
        return f'<Subscriber {self.topic} {self.msg_type} {self.callback}>'