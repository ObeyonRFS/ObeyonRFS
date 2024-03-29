from typing import TYPE_CHECKING, Dict, NoReturn, Tuple
from obeyon_rfs.components.nodes import Node

from asyncio import StreamReader, StreamWriter
from obeyon_rfs.components import ORFS_Message, ORFS_MessageType

import socket
import asyncio
import obeyon_rfs

class CoreNode(Node):
    def __init__(self,node_name:str,use_port:int=7134):
        super().__init__(
            node_name=node_name,
            receiver_host=socket.gethostbyname(socket.gethostname()),
            receiver_port=use_port
        )
        self._listener_nodes:Dict[str,Tuple[str,int]] = {}
        self.additional_handle_client_callbacks.append(self.__additional_handle_client)
    async def __additional_handle_client(self,model:ORFS_Message,reader:StreamReader,writer:StreamWriter):
        print("additional",model)
        match model.message_type:
            case ORFS_MessageType.CORE_PING:
                # print("pong")
                writer.write(ORFS_Message(
                    message_type=ORFS_MessageType.CORE_PONG,
                    message_name='pong',
                    message_content={},
                    node_name=self.node_name,
                    node_receiver_host=self.receiver_host,
                    node_receiver_port=self.receiver_port
                ).base64_encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            case ORFS_MessageType.REGISTER_NODE:

                if model.node_name in self._listener_nodes:
                    obeyon_rfs.log_info("removed",model.node_name)
                    del self._listener_nodes[model.node_name]
                if model.node_receiver_host==self.receiver_host and model.node_receiver_port==self.receiver_port:
                    return
                obeyon_rfs.log_info("register",model.node_name,model.node_receiver_host,model.node_receiver_port)
                self._listener_nodes[model.node_name]=(model.node_receiver_host,model.node_receiver_port)

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
                try:
                    dest_reader,dest_writer = await asyncio.open_connection(dest_host,dest_port)
                except ConnectionRefusedError as e:
                    continue
                dest_writer.write(model.base64_encode())
                await dest_writer.drain()
                dest_writer.close()
                await dest_writer.wait_closed()