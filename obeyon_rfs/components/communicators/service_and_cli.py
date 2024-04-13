import asyncio
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, Type
from uuid import UUID
from obeyon_rfs.components import (
    ORFS_Component,
    ORFS_MessageType,
    ORFS_Message
)
from obeyon_rfs.comm_type.srvs import (
    ServiceType, ServiceRequestType, ServiceResponseType
)
from obeyon_rfs.components.communicators.future import FutureType, Future
if TYPE_CHECKING:
    from obeyon_rfs.components import ClientNode, LocalNetworkCoreNode


class ServiceServer(ORFS_Component):
    def __init__(self,srv_name:str,srv_type:Type[ServiceType],coroutine_callback:Callable[[],Coroutine[Any,Any,None]]=None):
        super().__init__()
        self.parent:ClientNode = None
        self.srv_name = srv_name
        self.srv_type = srv_type
        self.srv_request_type = ServiceType.get_request_type(srv_type)
        self.srv_response_type = ServiceType.get_response_type(srv_type)
        self.coroutine_callback=coroutine_callback
    async def recv_model(self,model:ORFS_Message):
        if model.message_name!=self.srv_name:
            return
        srv_request=self.srv_request_type.validate(model.message_content)
        srv_response=await self.coroutine_callback(srv_request)
        await self.parent.sent_model_to_core(ORFS_Message(
            message_type=ORFS_MessageType.SERVICE_RESPONSE,
            message_name=self.srv_name,
            message_content=srv_response,
            node_name=self.parent.node_name,
            node_receiver_host=self.parent.receiver_host,
            node_receiver_port=self.parent.receiver_port,
            message_uuid=model.message_uuid
        ))

class ServiceClient(ORFS_Component):
    def __init__(self,srv_name:str,srv_type:Type[ServiceType]):
        super().__init__()
        self.parent:ClientNode = None
        self.srv_name = srv_name
        self.srv_type = srv_type
        self.srv_request_type = ServiceType.get_request_type(srv_type)
        self.srv_response_type = ServiceType.get_response_type(srv_type)
        self._futures:Dict[UUID,Future] = {}
        
    async def recv_model(self,model:ORFS_Message):
        if model.message_name!=self.srv_name:
            return
        if not isinstance(model.message_content,self.srv_response_type):
            raise TypeError('message type is not matched')
        else:
            for uuid,f in self._futures.items():
                if uuid==model.message_uuid:
                    # asyncio.create_task(self.future_with_model(model,f))
                    f.response=model.message_content
                    # if f.response_callback is not None:
                    #     f.response_callback(model.message_content)
    async def future_with_model(self,model:ORFS_Message,response):
        pass
    async def send_request(self,req:ServiceRequestType,timeout=5.0) -> Future:
        if not isinstance(req,self.srv_request_type):
            raise TypeError('message type is not matched')
        
        model=ORFS_Message(
            message_type=ORFS_MessageType.SERVICE_REQUEST,
            message_name=self.srv_name,
            message_content=req,
            node_name=self.parent.node_name,
            node_receiver_host=self.parent.receiver_host,
            node_receiver_port=self.parent.receiver_port
        )
        new_future=Future()
        new_future.parent=self
        new_future.future_type=FutureType.SERVICE
        new_future.response_timeout=timeout
        self._futures[model.message_uuid]=new_future
        await self.parent.sent_model_to_core(model)

        # asyncio.create_task(self.clear_timeout_futures(new_future))
        
        return new_future
    async def clear_timeout_futures(self,future):
        await asyncio.sleep(future.response_timeout)
        for uuid,f in list(self._futures.items()):
            if f.is_timeout():
                self._futures.pop(uuid)