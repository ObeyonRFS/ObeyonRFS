import asyncio
from dataclasses import dataclass
from enum import Enum
import time
from typing import TYPE_CHECKING, Any, Callable, List, Tuple

from obeyon_rfs.components import ORFS_Component, ORFS_MessageType

from obeyon_rfs.comm_type.actions import ActionType, ActionFeedbackType, ActionResultType
from obeyon_rfs.comm_type.srvs import ServiceRequestType, ServiceResponseType, ServiceType

if TYPE_CHECKING:
    from obeyon_rfs.components import ClientNode

class FutureType(str,Enum):
    SERVICE = 'SERVICE'
    ACTION = 'ACTION'


class Future(ORFS_Component):
    def __init__(self):
        super().__init__()
        self.start_time:float = time.time()
        self.parent:ClientNode = None
        self.future_type:FutureType = None

class ServiceFuture(Future):
    def __init__(self):
        super().__init__()
        self.future_type=FutureType.SERVICE
        self.request:ServiceRequestType = None
        self.response:ServiceResponseType = None
        self.response_timeout:float = None

    def is_timeout(self) -> bool:
        if time.time()-self.start_time>self.response_timeout:
            return True
        return False

    def is_ended(self) -> bool:
        if self.response is not None:
            return True
        if self.is_timeout():
            return True
        return False

    async def wait_for_response(self) -> ServiceResponseType|None:
        while True:
            await asyncio.sleep(0)
            if self.is_timeout():
                return None
            if self.response is not None:
                return self.response
    # def add_response_callback(self,callback:Callable[[ServiceResponseType],None]):
    #     self.response_callbacks.append(callback)
    # def add_response_timeout_callback(self,callback:Callable[[],None]):
    #     self.response_timeout_callbacks.append(callback)


class ActionFuture(Future):
    def __init__(self):
        super().__init__()
        self.future_type:FutureType = FutureType.ACTION
        self.result:ActionResultType = None

        self.feedback_timeout:float = None
        self.result_timeout:float = None

        self._action_infos:List[Tuple[float,ActionFeedbackType|ActionResultType]] = []

        self.consider_as_new_info_time_range=0.01

    def _push_info(self,info:ActionFeedbackType|ActionResultType):
        if self.is_ended()==False:
            self._action_infos.append((time.time(),info))
        else:
            raise Exception('Cannot push info to ended action future')
    @property
    def latest_info(self) -> ActionFeedbackType|ActionResultType|None:
        if len(self._action_infos)==0:
            return None
        return self._action_infos[-1][1]
    @property
    def latest_info_time(self) -> float:
        if len(self._action_infos)==0:
            return None
        return self._feedbacks[-1][0]
    @property
    def new_info(self) -> ActionFeedbackType|ActionResultType|None:
        if len(self._action_infos)==0:
            return None
        if time.time()-self.latest_info_time<self.consider_as_new_info_time_range:
            return self.latest_info
        else:
            return None
    @property
    def result(self):
        if isinstance(self.latest_info,ActionResultType):
            return self.latest_info
        else:
            return None
        
    def is_timeout(self) -> bool:
        if self.future_type==FutureType.SERVICE:
            if time.time()-self.start_time>self.response_timeout:
                return True
        return False
    def is_ended(self) -> bool:
        if self.result is not None:
            return True
        if self.is_timeout():
            return True
        return False

    async def wait_until_updated(self) -> ActionFeedbackType|ActionResultType|None:
        olength=len(self._action_infos)
        while True:
            await asyncio.sleep(0)
            if self.is_ended():
                return self.result
            if len(self._action_infos)!=olength:
                return self.latest_info

    async def wait_for_result(self) -> ActionResultType:
        while True:
            await asyncio.sleep(0)
            if self.is_ended():
                return self.result

    
        

    # def add_complete_callback(self,callback:Callable[[ServiceResponseType],None]):
    #     self.response_callbacks.append(callback)
    # def add_response_timeout_callback(self,callback:Callable[[],None]):
    #     self.response_timeout_callbacks.append(callback)