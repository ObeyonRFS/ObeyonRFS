from asyncio import StreamReader, StreamWriter
import socket
from typing import (Any, Coroutine, List,TYPE_CHECKING, NoReturn, Type,Callable)

import obeyon_rfs
import asyncio
from obeyon_rfs.components import ORFS_Component, ORFS_MessageType, ORFS_Message
from obeyon_rfs.comm_type.msgs import MessageType
from obeyon_rfs.comm_type.srvs import (
    ServiceType, ServiceRequestType, ServiceResponseType
)
from obeyon_rfs.comm_type.actions import (
    ActionType, ActionRequestType, ActionFeedbackType, ActionResultType
)
 
from obeyon_rfs.components.communicators import *

import numpy
numpy.set_printoptions(threshold=numpy.inf)

class Node(ORFS_Component):
    """
        Base Node class for all nodes\n
        This class is used to create a node for the system\n
        Node = "Application" or "Sequence of instructions to run on the system"\n
        - node_name : str
            name of the node, used to identify the node in the system
        - receiver_host : str
            host name to receive ORFS_Message (default: obeyon_rfs.get_local_ip_address())
        - receiver_port : int
            port number to receive ORFS_Message
        - domain_name (str, optional)
            name of the domain, used to separate nodes in the same network (can make CoreNode to do some filtering)\n
        
    """
    def __init__(self,node_name:str,receiver_host:str,receiver_port:int,domain_name=""):
        super().__init__()
        self.domain_name=domain_name
        self.node_name=node_name
        self.publishers:List['Publisher'] = []
        self.subscribers:List['Subscriber'] = []
        self.service_servers:List['ServiceServer'] = []
        self.service_clients:List['ServiceClient'] = []
        self.action_servers:List['ActionServer'] = []
        self.action_clients:List['ActionClient'] = []
        self.timers:List['Timer'] = []
        #added to solve serve_forever problem(KeyboardInterrupt not register)
        self.prevent_stuck_timer=self.create_timer(0.01,self.empty_func)

        self.receiver_host:str=receiver_host
        self.receiver_port:int=receiver_port
        self.receiver_server=None
        self.additional_handle_client_callbacks:List[Callable[[ORFS_Message,StreamReader,StreamWriter],Coroutine[Any,Any,None]]]=[]
        self.additional_start_callbacks:List[Callable[[],Coroutine[Any,Any,None]]]=[]
    async def empty_func(self):
        pass
    async def _start_receiver_server(self):
        self.receiver_server=await asyncio.start_server(
            self._handle_client,
            self.receiver_host,
            self.receiver_port,
        )
        self.receiver_host,self.receiver_port=self.receiver_server.sockets[0].getsockname()
        async with self.receiver_server:
            obeyon_rfs.log_info(f"{self.node_name}'s receiver {self.receiver_host}:{self.receiver_port} with domain {repr(self.domain_name)} started...")
            await self.receiver_server.serve_forever()
    async def _handle_client(self,reader:StreamWriter,writer:StreamReader):
        data = await reader.read(2048)
        # print("Received data:",data)
        model = ORFS_Message.base64_decode(data)
        if model is None:
            return
        if model.domain_name!=self.domain_name:
            #ignore other domain
            return
        
        # print(model)
        # if model.message_type!=ORFS_MessageType.CORE_PING:
        #     obeyon_rfs.log_info(model)
        match model.message_type:
            # case ORFS_MessageType.CORE_PING:
            # case ORFS_MessageType.REGISTER_NODE:
            case ORFS_MessageType.PUBLISH:
                await self._handle_publish(model)
            case ORFS_MessageType.SERVICE_REQUEST:
                await self._handle_service_request(model)
            case ORFS_MessageType.SERVICE_RESPONSE:
                await self._handle_service_response(model)
            case ORFS_MessageType.ACTION_REQUEST:
                await self._handle_action_request(model)
            case ORFS_MessageType.ACTION_FEEDBACK:
                await self._handle_action_feedback(model)
            case ORFS_MessageType.ACTION_RESULT:
                await self._handle_action_result(model)

        for handle_client in self.additional_handle_client_callbacks:
            await handle_client(model,reader,writer)
    async def _handle_publish(self,model:ORFS_Message):
        for sub in self.subscribers:
            if sub.topic==model.message_name:
                asyncio.create_task(sub.recv_model(model))
    async def _handle_service_request(self,model:ORFS_Message):
        for srv in self.service_servers:
            if srv.srv_name==model.message_name:
                asyncio.create_task(srv.recv_model(model))
    async def _handle_service_response(self,model:ORFS_Message):
        for srv in self.service_clients:
            if srv.srv_name==model.message_name:
                asyncio.create_task(srv.recv_model(model))
    async def _handle_action_request(self,model:ORFS_Message):
        for act in self.action_servers:
            if act.action_name==model.message_name:
                asyncio.create_task(act.recv_model(model))
    async def _handle_action_feedback(self,model:ORFS_Message):
        for act in self.action_clients:
            if act.action_name==model.message_name:
                asyncio.create_task(act.recv_model(model))
    async def _handle_action_result(self,model:ORFS_Message):
        for act in self.action_clients:
            if act.action_name==model.message_name:
                asyncio.create_task(act.recv_model(model))

    async def _start(self) -> NoReturn:
        tasks = []
        for timer in self.timers:
            tasks.append(asyncio.create_task(timer._start()))
        tasks.append(asyncio.create_task(self._start_receiver_server()))
        for start_callback in self.additional_start_callbacks:
            tasks.append(asyncio.create_task(start_callback()))
        await asyncio.gather(*tasks,return_exceptions=True)
    def start_as_main(self,exit_time:float=float('inf')) -> NoReturn | None:
        if exit_time!=float('inf'):
            self.create_timer(exit_time,self.stop_main)
            try:
                asyncio.run(self._start())
            except RuntimeError as e:
                # obeyon_rfs.log_error(repr(e))
                pass
        else:
            asyncio.run(self._start())
    async def start_as_task(self):
        return asyncio.create_task(self._start())
    async def stop_main(self):
        asyncio.get_event_loop().stop()


    
    def create_publisher(self,topic:str,msg_type:Type[MessageType]|None)->'Publisher':
        p=Publisher(topic,msg_type)
        p.parent=self
        self.publishers.append(p)
        return p
    def create_subscriber(self,topic:str,msg_type:Type[MessageType],coroutine_callback:Callable[[],Coroutine[Any,Any,None]]=None)->'Subscriber':
        s=Subscriber(topic,msg_type,coroutine_callback)
        s.parent=self
        self.subscribers.append(s)
        return s
    def create_service_server(self,srv_name:str,srv_type:Type[ServiceType],coroutine_callback:Callable[[],Coroutine[Any,Any,None]]=None)->'ServiceServer':
        s=ServiceServer(srv_name,srv_type,coroutine_callback)
        s.parent=self
        self.service_servers.append(s)
        return s
    def create_service_client(self,srv_name:str,srv_type:Type[ServiceType])->'ServiceClient':
        s=ServiceClient(srv_name,srv_type)
        s.parent=self
        self.service_clients.append(s)
        return s
    def create_action_server(self,action_name:str,action_type:Type[ActionType],coroutine_callback:Callable[[ActionRequestType,ActionFeedbackSender],Coroutine[Any,Any,ActionResultType]])->'ActionServer':
        s=ActionServer(action_name,action_type,coroutine_callback)
        s.parent=self
        self.action_servers.append(s)
        return s
    def create_action_client(self,action_name:str,action_type:Type[ActionType])->'ActionClient':
        s=ActionClient(action_name,action_type)
        s.parent=self
        self.action_clients.append(s)
        return s
    def create_timer(self,timer_interval:float,coroutine_callback:Callable[[],Coroutine[Any,Any,None]]=None,max_count=-1) -> 'Timer':
        t=Timer(timer_interval=timer_interval,coroutine_callback=coroutine_callback,max_count=max_count)
        t.parent=self
        self.timers.append(t)
        return t
    


from obeyon_rfs.components.nodes.core import *
from obeyon_rfs.components.nodes.core_searcher import *
from obeyon_rfs.components.nodes.client import *