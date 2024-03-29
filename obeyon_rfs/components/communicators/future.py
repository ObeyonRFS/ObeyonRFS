from typing import TYPE_CHECKING, Any, Callable, List

if TYPE_CHECKING:
    from obeyon_rfs.components import ORFS_Component, ORFS_MessageType
    from obeyon_rfs.components.nodes import AppNode
    from obeyon_rfs.components.communicators import ServiceResponseType, ServiceRequestType, ActionType, ActionFeedbackType, ActionResultType

class FutureType(str,Enum):
    SERVICE = 'SERVICE'
    ACTION = 'ACTION'

@dataclass
class Future(ORFS_Component):
    def __init__(self):
        super().__init__()
        self.start_time:float = time.time()
        self.last_feedback_time:float = time.time()
        self.parent:AppNode = None
        self.future_type:FutureType = None
        #The word complete can include error or success
        self.feedback_callbacks:List[Callable[[],None]] = []
        self.result_callbacks:List[Callable[[],None]] = []

        self.response = None
        self.old_feedback = None
        self.new_feedback = None
        self.result = None
        self.response_timeout:float = None
        self.feedback_timeout:float = None
        self.result_timeout:float = None

    @property
    def feedback(self):
        r=self.new_feedback
        self.old_feedback=self.new_feedback
        self.new_feedback=None
        return r
    
    async def wait_for_response(self) -> ServiceResponseType|None:
        if self.future_type==FutureType.SERVICE:
            while True:
                await asyncio.sleep(0)
                if time.time()-self.start_time>self.response_timeout:
                    return None
                if self.response is not None:
                    return self.response
    async def wait_for_result(self) -> ActionResultType|None:
        if self.future_type==FutureType.ACTION:
            while True:
                await asyncio.sleep(0)
                if time.time()-self.start_time>self.result_timeout:
                    return None
                if self.result is not None:
                    return self.result
    async def wait_for_feedback(self) -> ActionFeedbackType|None:
        if self.future_type==FutureType.ACTION:
            while True:
                await asyncio.sleep(0)
                if time.time()-self.last_feedback_time>self.feedback_timeout:
                    return None
                if self.result is not None:
                    return
                elif self.new_feedback is not None:
                    return
        
    def is_timeout(self) -> bool:
        if self.future_type==FutureType.SERVICE:
            if time.time()-self.start_time>self.response_timeout:
                return True
        return False
    def add_complete_callback(self,callback:Callable[[ServiceResponseType],None]):
        self.response_callbacks.append(callback)
    def add_response_timeout_callback(self,callback:Callable[[],None]):
        self.response_timeout_callbacks.append(callback)