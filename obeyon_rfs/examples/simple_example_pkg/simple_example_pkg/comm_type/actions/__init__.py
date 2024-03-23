from obeyon_rfs.comm_type.actions import ActionRequestType,ActionFeedbackType,ActionResultType,ActionType

class CountingActionRequestType(ActionRequestType):
    goal:int
    pass
class CountingActionFeedbackType(ActionFeedbackType):
    pass
class CountingActionResultType(ActionResultType):
    pass

class CountingActionType(ActionType):
    request:CountingActionRequestType = CountingActionRequestType()
    feedback:CountingActionFeedbackType = CountingActionFeedbackType()
    result:CountingActionResultType = CountingActionResultType()