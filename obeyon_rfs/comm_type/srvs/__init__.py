from typing import Type, get_type_hints
from pydantic import BaseModel
from obeyon_rfs.datatypes import *

class ServiceRequestType(BaseModel):
    pass

class ServiceResponseType(BaseModel):
    pass

class ServiceType(BaseModel):
    request: ServiceRequestType
    response: ServiceResponseType
    @staticmethod
    def get_request_type(srv_type:Type['ServiceType'])->Type[ServiceRequestType]:
        return get_type_hints(srv_type)["request"]
    @staticmethod
    def get_response_type(srv_type:Type['ServiceType'])->Type[ServiceResponseType]:
        return get_type_hints(srv_type)["response"]
    

class AddTwoIntsRequestType(ServiceRequestType):
    a:float
    b:float

class AddTwoIntsResponseType(ServiceResponseType):
    result:float

class AddTwoIntsType(ServiceType):
    request:AddTwoIntsRequestType
    response:AddTwoIntsResponseType
