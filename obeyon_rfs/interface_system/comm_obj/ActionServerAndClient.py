from typing import Callable

from pydantic import BaseModel

from obeyon_rfs.interface_system.comm_obj.CommObj import CommObj
from obeyon_rfs.interface_system.comm_type.actions import (
    ActionRequestType,
    ActionFeedbackType,
    ActionResultType,
    ActionType
)
from obeyon_rfs.interface_system.event import (
    EventHandleActionServer,
    EventHandleActionClient
)

import threading


class ActionClient(CommObj):
    pass

class ActionFeedbackSender(CommObj):
    pass

class ActionServer(CommObj):
    pass

