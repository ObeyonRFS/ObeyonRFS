from pydantic import BaseModel

class MessageType(BaseModel):
    pass

class SimpleMsg(MessageType):
    data : str = "Hello, World!"
    count: int = 0

