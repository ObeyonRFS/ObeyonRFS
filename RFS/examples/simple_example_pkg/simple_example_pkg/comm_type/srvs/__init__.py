from RFS.comm_type.srvs import ServiceRequestType,ServiceResponseType,ServiceType

class AddTwoIntsRequest(ServiceRequestType):
    a: int = 0
    b: int = 0
class AddTwoIntsResponse(ServiceResponseType):
    result: int = 0
class AddTwoInts(ServiceType):
    request:AddTwoIntsRequest = AddTwoIntsRequest()
    response:AddTwoIntsResponse = AddTwoIntsResponse()