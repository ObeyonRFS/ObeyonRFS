from RFS.comm_type.msgs import MessageType

class CustomMsgType(MessageType):
    data:str = "Hello, World!"
    count:int = 0

