from typing import Type, get_type_hints
from pydantic import BaseModel
from obeyon_rfs.datatypes import *

class ServiceRequestType(BaseModel):
    pass

class ServiceResponseType(BaseModel):
    pass

class ServiceType(BaseModel):
    """
    ServiceType is a base class for all service types.\n
    It is used to define the request and response types of a service.
    """
    request: ServiceRequestType
    response: ServiceResponseType
    @staticmethod
    def get_request_type(srv_type:Type['ServiceType'])->Type[ServiceRequestType]:
        """
        Get the request type of the service type.
        This is done by using the get_type_hints function to get the type hints of the service type and then getting the request type from it.
        """
        return get_type_hints(srv_type)["request"]
    @staticmethod
    def get_response_type(srv_type:Type['ServiceType'])->Type[ServiceResponseType]:
        """
        Get the response type of the service type.
        This is done by using the get_type_hints function to get the type hints of the service type and then getting the response type from it.
        """
        return get_type_hints(srv_type)["response"]
    

class AddTwoIntsRequestType(ServiceRequestType):
    a:float
    b:float

class AddTwoIntsResponseType(ServiceResponseType):
    result:float

class AddTwoIntsType(ServiceType):
    request:AddTwoIntsRequestType
    response:AddTwoIntsResponseType
