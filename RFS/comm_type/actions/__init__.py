from pydantic import BaseModel


class ActionRequestType(BaseModel):
    pass
class ActionFeedbackType(BaseModel):
    pass
class ActionResultType(BaseModel):
    pass

class ActionType(BaseModel):
    request:ActionRequestType = ActionRequestType()
    feedback:ActionFeedbackType = ActionFeedbackType()
    result:ActionResultType = ActionResultType()