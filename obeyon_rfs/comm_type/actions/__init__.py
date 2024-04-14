from obeyon_rfs.datatypes import *
from typing import Type, get_type_hints


class ActionRequestType(BaseModel): # request with goal or task
    pass
class ActionFeedbackType(BaseModel):
    pass
class ActionResultType(BaseModel):
    pass
class ActionType(BaseModel):
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
    destination_number:float
    error_threshold:float

class MoveNumberToActionFeedbackType(ActionFeedbackType):
    current_number:int

class MoveNumberToActionResultType(ActionResultType):
    final_number:int
    error:float

class MoveNumberActionType(ActionType):
    request:MoveNumberToActionRequestType
    feedback:MoveNumberToActionFeedbackType
    result:MoveNumberToActionResultType