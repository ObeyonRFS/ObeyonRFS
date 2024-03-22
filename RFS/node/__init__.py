from typing import Callable, Tuple
from RFS.RFS_Socket import *
import threading


import time

from RFS.comm_obj.PublisherAndSubscriber import Publisher, Subscriber
from RFS.comm_obj.ServiceAndClient import ServiceServer, ServiceClient
from RFS.comm_obj.ActionServerAndClient import ActionServer, ActionClient, ActionSubscriber   #Don't know how to use it yet

from RFS.comm_type.msgs import MessageType
from RFS.comm_type.srvs import ServiceType
from RFS.comm_type.actions import ActionType



class Node:
    def __init__(self, name: str):
        self.name = name
    def create_publisher(self, topic: str, msg_type: MessageType) -> Publisher:
        return Publisher(self, topic, msg_type)
    def create_subscriber(self, topic: str, msg_type: MessageType, callback: Callable[[MessageType],None]) -> Subscriber:
        return Subscriber(self, topic, msg_type, callback)
    def create_service(self, service: str, srv_type: ServiceType, callback: Callable[[ServiceRequestType],ServiceResponseType]) -> ServiceServer:
        return ServiceServer(self, service, srv_type, callback)
    def create_client(self, service: str, srv_type: ServiceType, futuer_handle) -> ServiceClient:
        return ServiceClient(self, service, srv_type)
    def create_action_server(self, action: str, act_type: ActionType, callback: Callable) -> ActionServer:
        return ActionServer(self, action, act_type, callback)
    def create_action_client(self, action: str, act_type: ActionType) -> ActionClient:
        return ActionClient(self, action, act_type)
    def create_action_subscriber(self, action: str, act_type: ActionType, callback: Callable) -> ActionSubscriber:
        return ActionSubscriber(self, action, act_type, callback)








