import sys
from typing import TYPE_CHECKING, Dict, NoReturn, Tuple
from obeyon_rfs.components.nodes import Node

from asyncio import StreamReader, StreamWriter
from obeyon_rfs.components import ORFS_Message, ORFS_MessageType

import asyncio
import obeyon_rfs

class LocalNetworkCoreNode(Node):
    """
        Core node for local network communication
    """
    def __init__(self,node_name:str,use_port:int=7134,domain_name:str=""):
        super().__init__(
            node_name=node_name,
            receiver_host=obeyon_rfs.get_local_ip_address(),
            receiver_port=use_port,
            domain_name=domain_name
        )
        self._listener_nodes:Dict[str,Tuple[str,int]] = {}
        self.additional_handle_client_callbacks.append(self.__additional_handle_client)
    async def __additional_handle_client(self,model:ORFS_Message,reader:StreamReader,writer:StreamWriter):
        # print("additional",model)
        # register with model message instead (include every types)
        if model.node_name not in self._listener_nodes:
            self._listener_nodes[model.node_name]=(model.node_receiver_host,model.node_receiver_port)
            obeyon_rfs.log_info("registered",model.node_name,model.node_receiver_host,model.node_receiver_port)
        if model.node_name in self._listener_nodes:
            if self._listener_nodes[model.node_name]!=(model.node_receiver_host,model.node_receiver_port):
                self._listener_nodes[model.node_name]=(model.node_receiver_host,model.node_receiver_port)
                obeyon_rfs.log_info("updated",model.node_name,model.node_receiver_host,model.node_receiver_port)
        
        match model.message_type:
            case ORFS_MessageType.CORE_PING:
                writer.write(ORFS_Message(
                    message_type=ORFS_MessageType.CORE_PONG,
                    message_name='pong',
                    message_content={},
                    node_name=self.node_name,
                    node_receiver_host=self.receiver_host,
                    node_receiver_port=self.receiver_port,
                    domain_name=self.domain_name
                ).base64_encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            case ORFS_MessageType.BROADCAST_CORE_PING:
                try:
                    dest_reader,dest_writer = await asyncio.open_connection(model.node_receiver_host,model.node_receiver_port)
                    dest_writer.write(ORFS_Message(
                        message_type=ORFS_MessageType.CORE_PONG,
                        message_name='pong',
                        message_content={},
                        node_name=self.node_name,
                        node_receiver_host=self.receiver_host,
                        node_receiver_port=self.receiver_port,
                        domain_name=self.domain_name
                    ).base64_encode())
                except ConnectionRefusedError as e:
                    obeyon_rfs.log_info("ConnectionRefusedError")
                    return
                except TimeoutError as e:
                    obeyon_rfs.log_info("TimeoutError")
                    return
                except OSError as e:
                    if e.errno==10049:
                        obeyon_rfs.log_info(e)
                        return
                
            # case ORFS_MessageType.REGISTER_NODE:

            #     if model.node_name in self._listener_nodes:
            #         obeyon_rfs.log_info("removed",model.node_name)
            #         del self._listener_nodes[model.node_name]
            #     if model.node_receiver_host==self.receiver_host and model.node_receiver_port==self.receiver_port:
            #         return
            #     obeyon_rfs.log_info("register",model.node_name,model.node_receiver_host,model.node_receiver_port)
            #     self._listener_nodes[model.node_name]=(model.node_receiver_host,model.node_receiver_port)

        # print("Check bool",model.message_type in [
        #     ORFS_MessageType.PUBLISH,
        #     ORFS_MessageType.SERVICE_REQUEST,
        #     ORFS_MessageType.SERVICE_RESPONSE,
        #     ORFS_MessageType.ACTION_REQUEST,
        #     ORFS_MessageType.ACTION_FEEDBACK,
        #     ORFS_MessageType.ACTION_RESULT
        # ],model)
        #forward to registerd nodes
        if model.message_type in [
            ORFS_MessageType.PUBLISH,
            ORFS_MessageType.SERVICE_REQUEST,
            ORFS_MessageType.SERVICE_RESPONSE,
            ORFS_MessageType.ACTION_REQUEST,
            ORFS_MessageType.ACTION_FEEDBACK,
            ORFS_MessageType.ACTION_RESULT
        ]:
            if model.node_name not in self._listener_nodes:
                return
            
            for node_name,(dest_host,dest_port) in list(self._listener_nodes.items()):
                print("Forwarding model",model,"to",node_name,dest_host,dest_port)
                try:
                    dest_reader,dest_writer = await asyncio.wait_for(asyncio.open_connection(dest_host,dest_port),timeout=0.5)
                except ConnectionRefusedError as e:
                    #remove node
                    self._listener_nodes.pop(node_name,None)
                    obeyon_rfs.log_info("removed",node_name, "ConnectionRefusedError")
                    continue
                    
                except TimeoutError as e:
                    #remove node
                    self._listener_nodes.pop(node_name,None)
                    obeyon_rfs.log_info("removed",node_name, "ConnectionRefusedError")
                    continue
                except OSError as e:
                    if e.errno==10049:
                        #remove node
                        self._listener_nodes.pop(node_name,None)
                        obeyon_rfs.log_info("removed",node_name, "ConnectionRefusedError")
                        continue
                    raise e
                dest_writer.write(model.base64_encode())
                await dest_writer.drain()
                obeyon_rfs.log_info("forwarded to",node_name,dest_host,dest_port)
                dest_writer.close()
                await dest_writer.wait_closed()
    async def sent_model_to_core(self,model:ORFS_Message):
        model.domain_name=self.domain_name
        try:
            reader,writer = await asyncio.open_connection(self.receiver_host,self.receiver_port)
        except ConnectionRefusedError as e:
            sys.exit('CoreNode connection lost')
        writer.write(model.base64_encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()