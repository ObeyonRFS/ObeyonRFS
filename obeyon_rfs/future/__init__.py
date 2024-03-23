from typing import Callable, Optional

from obeyon_rfs.comm_type.msgs import MessageType
from obeyon_rfs.comm_type.srvs import ServiceRequestType, ServiceResponseType
from obeyon_rfs.comm_type.actions import ActionRequestType,ActionFeedbackType,ActionResultType


class FutureHandle():#future handling for action 
    def __init__(self,
                **kwargs
                ):
        for key, value in kwargs.items():
            setattr(self, key, value)


class FutureHandlePublisher(FutureHandle):
    def __init__(self,
                 on_msg_sent:Callable[[bool],None]=None,
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.on_msg_sent = on_msg_sent

class FutureHandleSubscriber(FutureHandle):
    def __init__(self,
                 on_msg_received:Callable[[bool],None]=None,
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.on_msg_received = on_msg_received




class FutureHandleServiceClient(FutureHandle):
    def __init__(self,
                 on_request_sent:Callable[[None],None]=None,
                 on_timeout:Callable[[None],None]=None,
                 on_timeout_to_response:Callable[[None],None]=None,
                 on_response_received:Callable[[ServiceResponseType],None]=None,
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.on_request_sent = on_request_sent
        self.on_timeout = on_timeout
        self.on_timeout_to_response = on_timeout_to_response
        self.on_response_received = on_response_received

class FutureHandleServiceServer(FutureHandle):
    def __init__(self,
                 on_request_received: Optional[Callable[[None],None]] = None,
                 on_timeout_to_response: Optional[Callable[[None],None]] = None,
                 on_response_sent: Optional[Callable[[None],None]] = None,
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.on_request_received = on_request_received
        self.on_timeout_to_response = on_timeout_to_response
        self.on_response_sent = on_response_sent


class FutureHandleActionClient(FutureHandle):
    def __init__(self,
                 on_request_sent: Optional[Callable[[None],None]] = None,
                 on_timeout: Optional[Callable[[None],None]] = None,
                 on_timeout_to_feedback: Optional[Callable[[None],None]] = None,
                 on_timeout_to_result: Optional[Callable[[None],None]] = None,
                 on_feedback: Optional[Callable[[ActionFeedbackType],None]] = None,
                 on_result: Optional[Callable[[ActionResultType],None]] = None,
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.on_request_sent = on_request_sent
        self.on_timeout = on_timeout
        self.on_timeout_to_feedback = on_timeout_to_feedback
        self.on_timeout_to_result = on_timeout_to_result
        self.on_feedback = on_feedback
        self.on_result = on_result


class FutureHandleActionServer(FutureHandle):
    def __init__(self,
                 on_request_received:Callable[[None],None]=None,
                 on_timeout_to_response:Callable[[None],None]=None,
                 on_response:Callable[[None],None]=None,
                 on_timeout_to_feedback:Callable[[None],None]=None,
                 on_send_feedback:Callable[[ActionFeedbackType],None]=None,
                 on_send_result:Callable[[ActionResultType],None]=None,
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.on_request_received = on_request_received
        self.on_timeout_to_response = on_timeout_to_response
        self.on_response = on_response
        self.on_timeout_to_feedback = on_timeout_to_feedback
        self.on_send_feedback = on_send_feedback
        self.on_send_result = on_send_result