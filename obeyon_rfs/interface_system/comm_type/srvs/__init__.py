from typing import ClassVar, Type
from pydantic import BaseModel

class ServiceRequestType(BaseModel):
    pass
class ServiceResponseType(BaseModel):
    pass
class ServiceType(BaseModel):
    request_type:ClassVar[Type[ServiceRequestType]] = ServiceRequestType
    response_type:ClassVar[Type[ServiceResponseType]] = ServiceResponseType
    

class ForwardBackwardRequest(ServiceRequestType):
    data:str="Hello, World!"
class ForwardBackwardResponse(ServiceResponseType):
    data:str="Hello, World!"
class ForwardBackward(ServiceType):
    request_type:ClassVar[Type[ForwardBackwardRequest]] = ForwardBackwardRequest
    response_type:ClassVar[Type[ForwardBackwardResponse]] = ForwardBackwardResponse
