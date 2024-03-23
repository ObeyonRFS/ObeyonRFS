from pydantic import BaseModel

class ServiceRequestType(BaseModel):
    pass
class ServiceResponseType(BaseModel):
    pass
class ServiceType(BaseModel):
    request:ServiceRequestType = ServiceRequestType()
    response:ServiceResponseType = ServiceResponseType()
    

class ForwardBackwardRequest(ServiceRequestType):
    data:str="Hello, World!"
class ForwardBackwardResponse(ServiceResponseType):
    data:str="Hello, World!"
class ForwardBackward(ServiceType):
    request:ForwardBackwardRequest = ForwardBackwardRequest()
    response:ForwardBackwardResponse = ForwardBackwardResponse()
