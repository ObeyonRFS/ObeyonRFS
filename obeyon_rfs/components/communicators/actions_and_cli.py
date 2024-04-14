import asyncio
import time
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, Type
from uuid import UUID

from obeyon_rfs.comm_type.actions import (
    ActionRequestType,
    ActionFeedbackType,
    ActionResultType,
    ActionType
)
from obeyon_rfs.components import (
    ORFS_Component,
    ORFS_MessageType,
    ORFS_Message
)

if TYPE_CHECKING:
    from obeyon_rfs.components.nodes import ClientNode, ActionFuture

class ActionFeedbackSender(ORFS_Component):
    def __init__(self):
        super().__init__()
        self.parent:ClientNode = None
        self.uuid=None
        self.action_name=None
    async def send(self,feedback:ActionFeedbackType):
        if not isinstance(feedback,ActionFeedbackType):
            raise TypeError('feedback type is not matched')
        await self.parent.sent_model_to_core(ORFS_Message(
            message_type=ORFS_MessageType.ACTION_FEEDBACK,
            message_name=self.action_name,
            message_content=feedback,
            node_name=self.parent.node_name,
            node_receiver_host=self.parent.receiver_host,
            node_receiver_port=self.parent.receiver_port,
            message_uuid=self.uuid
        ))
    # async def send_result(self,result:ActionResultType):
    #     if not isinstance(result,ActionResultType):
    #         raise TypeError('result type is not matched')
    #     await self.parent.sent_model_to_core(ORFS_Message(
    #         message_type=ORFS_MessageType.ACTION_RESULT,
    #         message_name=self.action_name,
    #         message_content=result,
    #         node_name=self.parent.node_name,
    #         node_receiver_host=self.parent.receiver_host,
    #         node_receiver_port=self.parent.receiver_port,
    #         message_uuid=self.uuid
    #     ))

class ActionServer(ORFS_Component):
    def __init__(self,action_name:str,action_type:Type[ActionType],coroutine_callback:Callable[[ActionRequestType,ActionFeedbackSender],Coroutine[Any,Any,ActionResultType]]):
        super().__init__()
        self.parent:ClientNode = None
        self.action_name=action_name
        self.action_type=action_type
        self.action_request_type=ActionType.get_request_type(action_type)
        self.action_feedback_type=ActionType.get_feedback_type(action_type)
        self.action_result_type=ActionType.get_result_type(action_type)
        self.coroutine_callback=coroutine_callback
    async def recv_model(self,model:ORFS_Message):
        if model.message_name!=self.action_name:
            return
        action_req=ActionRequestType.validate(model.message_content)

        action_feedback_sender=ActionFeedbackSender()
        action_feedback_sender.parent=self.parent
        action_feedback_sender.uuid=model.message_uuid
        action_feedback_sender.action_name=self.action_name
        
        await self.coroutine_callback(model.message_content,action_info_sender)


class ActionClient(ORFS_Component):
    def __init__(self,action_name:str,action_type:Type[ActionType]):
        super().__init__()
        self.parent:ClientNode = None
        self.action_name=action_name
        self.action_type=action_type
        self.action_request_type=ActionType.get_request_type(action_type)
        self.action_feedback_type=ActionType.get_feedback_type(action_type)
        self.action_result_type=ActionType.get_result_type(action_type)
        self._futures:Dict[UUID,ActionFuture] = {}
    async def recv_model(self,model:ORFS_Message):
        if model.message_name!=self.action_name:
            return
        if model.message_type==ORFS_MessageType.ACTION_FEEDBACK:
            action_feedback=self.action_feedback_type.validate(model.message_content)
            for uuid,f in self._futures.items():
                if uuid==model.message_uuid:
                    f._push_info(action_feedback)
        elif model.message_type==ORFS_MessageType.ACTION_RESULT:
            action_result=self.action_result_type.validate(model.message_content)
            for uuid,f in self._futures.items():
                if uuid==model.message_uuid:
                    f._push_info(action_result)
    async def send_request(self,req:ActionRequestType,feedback_timeout=5.0,result_timeout=float('inf')) -> ActionFuture:
        if not isinstance(req,self.action_request_type):
            raise TypeError('message type is not matched')
        
        model=ORFS_Message(
            message_type=ORFS_MessageType.ACTION_REQUEST,
            message_name=self.action_name,
            message_content=req,
            node_name=self.parent.node_name,
            node_receiver_host=self.parent.receiver_host,
            node_receiver_port=self.parent.receiver_port
        )
        new_future=ActionFuture()
        new_future.parent=self
        new_future.feedback_timeout=feedback_timeout
        new_future.result_timeout=result_timeout
        self._future[model.message_uuid]=new_future
        await self.parent.sent_model_to_core(model)
        return new_future