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
from obeyon_rfs.components.communicators.future import FutureType, Future
if TYPE_CHECKING:
    from obeyon_rfs.components.nodes import Node

class ActionInfoSender(ORFS_Component):
    def __init__(self):
        super().__init__()
        self.parent:Node = None
        self.uuid=None
        self.action_name=None
    def send_feedback(self,feedback:ActionFeedbackType):
        self.parent.sent_model_to_core(ORFS_Message(
            message_type=ORFS_MessageType.ACTION_FEEDBACK,
            message_name=self.action_name,
            message_content=feedback,
            node_name=self.parent.node_name,
            node_receiver_host=self.parent.receiver_host,
            node_receiver_port=self.parent.receiver_port,
            message_uuid=self.uuid
        ))
    def send_result(self,result:ActionResultType):
        self.parent.sent_model_to_core(ORFS_Message(
            message_type=ORFS_MessageType.ACTION_RESULT,
            message_name=self.action_name,
            message_content=result,
            node_name=self.parent.node_name,
            node_receiver_host=self.parent.receiver_host,
            node_receiver_port=self.parent.receiver_port,
            message_uuid=self.uuid
        ))

class ActionServer(ORFS_Component):
    def __init__(self,action_name:str,action_type:Type[ActionType],coroutine_callback:Callable[[ActionRequestType,ActionInfoSender],Coroutine[Any,Any,None]]):
        super().__init__()
        self.parent:Node = None
        self.action_name=action_name
        self.action_type=action_type
        self.action_request_type=ActionType.get_request_type(action_type)
        self.action_feedback_type=ActionType.get_feedback_type(action_type)
        self.action_result_type=ActionType.get_result_type(action_type)
        self.coroutine_callback=coroutine_callback
    async def recv_model(self,model:ORFS_Message):
        if model.message_name!=self.action_name:
            return
        if not isinstance(model.message_content,self.action_request_type):
            raise TypeError('message type is not matched')
        else:
            action_info_sender=ActionInfoSender()
            action_info_sender.parent=self.parent
            action_info_sender.uuid=model.message_uuid
            action_info_sender.action_name=self.action_name
            asyncio.create_task(self.coroutine_callback(model.message_content,action_info_sender))


class ActionClient(ORFS_Component):
    def __init__(self,action_name:str,action_type:Type[ActionType]):
        super().__init__()
        self.parent:Node = None
        self.action_name=action_name
        self.action_type=action_type
        self.action_request_type=ActionType.get_request_type(action_type)
        self.action_feedback_type=ActionType.get_feedback_type(action_type)
        self.action_result_type=ActionType.get_result_type(action_type)
        self._futures:Dict[UUID,asyncio.Future] = {}
    async def recv_model(self,model:ORFS_Message):
        if model.message_name!=self.action_name:
            return
        if model.message_type==ORFS_MessageType.ACTION_FEEDBACK:
            if not isinstance(model.message_content,self.action_feedback_type):
                raise TypeError('message type is not matched')
            else:
                for uuid,f in self._futures.items():
                    if uuid==model.message_uuid:
                        # asyncio.create_task(self.future_with_model(model,f))
                        f.new_feedback=model.message_content
                        f.last_feedback_time=time.time()
                        # if f.response_callback is not None:
                        #     f.response_callback(model.message_content)
        elif model.message_type==ORFS_MessageType.ACTION_RESULT:
            if not isinstance(model.message_content,self.action_result_type):
                raise TypeError('message type is not matched')
            else:
                for uuid,f in self._futures.items():
                    if uuid==model.message_uuid:
                        # asyncio.create_task(self.future_with_model(model,f))
                        f.result=model.message_content
                        # if f.response_callback is not None:
                        #     f.response_callback(model.message_content)
    async def future_with_model(self,model:ORFS_Message,response):
        pass
    def send_request(self,req:ActionRequestType)->ActionResultType:
        #work in progress
        new_future=self.send_request_async(req,None)
        return new_future.wait_for_result()
    def send_request_async(self,req:ActionRequestType,feedback_timeout=5.0,result_timeout=5.0) -> Future:
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
        self.parent.sent_model_to_core(model)
        new_future=Future()
        new_future.parent=self
        new_future.future_type=FutureType.ACTION
        new_future.feedback_timeout=feedback_timeout
        new_future.result_timeout=result_timeout

        self._futures[model.message_uuid]=new_future

        # asyncio.create_task(self.clear_timeout_futures(new_future))
        
        return new_future