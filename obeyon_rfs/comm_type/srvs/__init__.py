from obeyon_rfs.datatypes import *
from typing import Type, get_type_hints

@dataclass
class ServiceRequestType:
    pass

@dataclass
class ServiceResponseType:
    pass

@dataclass
class ServiceType:
    request: ServiceRequestType
    response: ServiceResponseType
    @staticmethod
    def get_request_type(srv_type:Type['ServiceType'])->Type[ServiceRequestType]:
        return get_type_hints(srv_type)["request"]
    @staticmethod
    def get_response_type(srv_type:Type['ServiceType'])->Type[ServiceResponseType]:
        return get_type_hints(srv_type)["response"]
    

@dataclass
class AddTwoIntsRequestType(ServiceRequestType):
    a:float
    b:float
@dataclass
class AddTwoIntsResponseType(ServiceResponseType):
    result:float
@dataclass
class AddTwoIntsType(ServiceType):
    request:AddTwoIntsRequestType
    response:AddTwoIntsResponseType
