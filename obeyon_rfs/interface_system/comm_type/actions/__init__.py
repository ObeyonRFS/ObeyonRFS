from typing import Type
from pydantic import BaseModel


class ActionRequestType(BaseModel):
    pass
class ActionFeedbackType(BaseModel):
    pass
class ActionResultType(BaseModel):
    pass

class ActionType(BaseModel):
    request_type:Type[ActionRequestType] = ActionRequestType
    feedback_type:Type[ActionFeedbackType] = ActionFeedbackType
    result_type:Type[ActionResultType] = ActionResultType
    # request:ActionRequestType = ActionRequestType()
    # feedback:ActionFeedbackType = ActionFeedbackType()
    # result:ActionResultType = ActionResultType()