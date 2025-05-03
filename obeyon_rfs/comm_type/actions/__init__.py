from obeyon_rfs.datatypes import *
from typing import Type, get_type_hints


class ActionRequestType(BaseModel): # request with goal or task
    pass
class ActionFeedbackType(BaseModel):
    pass
class ActionResultType(BaseModel):
    pass
class ActionType(BaseModel):
    """
    ActionType is a base class for all action types.\n
    It is used to define the request, feedback and result types of an action.
    - request: The request type of the action.
    - feedback: The feedback type of the action.
    - result: The result type of the action.
    """

    request:ActionRequestType
    feedback:ActionFeedbackType
    result:ActionResultType
    @staticmethod
    def get_request_type(action_type:Type['ActionType'])->Type[ActionRequestType]:
        return get_type_hints(action_type)["request"]
    @staticmethod
    def get_feedback_type(action_type:Type['ActionType'])->Type[ActionFeedbackType]:
        return get_type_hints(action_type)["feedback"]
    @staticmethod
    def get_result_type(action_type:Type['ActionType'])->Type[ActionResultType]:
        return get_type_hints(action_type)["result"]

class MoveNumberToActionRequestType(ActionRequestType):
    """
    MoveNumberToActionRequestType is a request type for the MoveNumber action.\n
    It is used to define the request type of the action.
    - destination_number: The destination number to move to.
    - error_threshold: The error threshold for the action.
    """
    destination_number:float
    error_threshold:float

class MoveNumberToActionFeedbackType(ActionFeedbackType):
    """
    MoveNumberToActionFeedbackType is a feedback type for the MoveNumber action.\n
    It is used to define the feedback type of the action.
    - current_number: The current number of the action.
    """
    current_number:int

class MoveNumberToActionResultType(ActionResultType):
    """
    MoveNumberToActionResultType is a result type for the MoveNumber action.\n
    It is used to define the result type of the action.
    - final_number: The final number of the action.
    - error: The error of the action.
    """
    final_number:int
    error:float

class MoveNumberActionType(ActionType):
    """
    MoveNumberActionType is a action type for the MoveNumber action.\n
    It is used to define the request, feedback and result types of the action.
    - request: The request type of the action.
    - feedback: The feedback type of the action.
    - result: The result type of the action.
    """
    
    request:MoveNumberToActionRequestType
    feedback:MoveNumberToActionFeedbackType
    result:MoveNumberToActionResultType