from pydantic import BaseModel

from obeyon_rfs.interface_system.comm_obj.CommObj import CommObj


class Progress(BaseModel):
    request:Any
    feedback:Any
    _old_feedback:Any
    _new_feedback:Any
    response:Any
    