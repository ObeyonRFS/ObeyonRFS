
from typing import TYPE_CHECKING
import socket

import asyncio
import sys
import obeyon_rfs
from obeyon_rfs.components import ORFS_Component, ORFS_MessageType,ORFS_Message
from obeyon_rfs.components.nodes import Node

class ClientNode(Node):
    def __init__(self,node_name:str,core_host:str,core_port:int):
        super().__init__(
            node_name=node_name,
            receiver_host=obeyon_rfs.get_local_ip_address(),
            receiver_port=0
        )
        self.core_ping_timer=self.create_timer(0.01,self.ping_to_core)
        self.core_host=core_host
        self.core_port=core_port
        self.additional_start_callbacks.append(self.__additional_start_callback)
    async def ping_to_core(self):
        try:
            reader,writer = await asyncio.wait_for(asyncio.open_connection(self.core_host,self.core_port),timeout=0.5)
        
            writer.write(ORFS_Message(
                message_type=ORFS_MessageType.CORE_PING,
                message_name='ping',
                message_content={},
                node_name=self.node_name,
                node_receiver_host=self.receiver_host,
                node_receiver_port=self.receiver_port
            ).base64_encode())
            await writer.drain()
            await asyncio.sleep(2.0)
            # data = await reader.read(2048)
            data = await asyncio.wait_for(reader.read(2048),timeout=0.2)
            model = ORFS_Message.base64_decode(data)
            if model is not None:
                if model.message_type==ORFS_MessageType.CORE_PONG:
                    return
        except ConnectionRefusedError as e:
            sys.exit('CoreNode connection lost')
        except TimeoutError as e:
            sys.exit('CoreNode connection timeout')
    # async def register_to_core(self):
    #     while self.receiver_port==0:
    #         await asyncio.sleep(0)
    #     reader,writer = await asyncio.open_connection(self.core_host,self.core_port)
    #     writer.write(ORFS_Message(
    #         message_type=ORFS_MessageType.REGISTER_NODE,
    #         message_name='register',
    #         message_content={},
    #         node_name=self.node_name,
    #         node_receiver_host=self.receiver_host,
    #         node_receiver_port=self.receiver_port
    #     ).base64_encode())
    #     await writer.drain()
    #     writer.close()
    #     await writer.wait_closed()
    async def sent_model_to_core(self,model:ORFS_Message):
        model.domain_name=self.domain_name
        try:
            reader,writer = await asyncio.wait_for(asyncio.open_connection(self.core_host,self.core_port),timeout=0.5)
        except ConnectionRefusedError as e:
            sys.exit('CoreNode connection lost')
        except TimeoutError as e:
            sys.exit('CoreNode connection timeout')
        writer.write(model.base64_encode())
        await writer.drain()
        # obeyon_rfs.log_info("Sent model to core:",model)
        writer.close()
        await writer.wait_closed()
    async def __additional_start_callback(self):
        # await self.register_to_core()
        pass




from obeyon_rfs.components.nodes.client.app_node import AppNode
from obeyon_rfs.components.nodes.client.serial_driver_node import SerialDriverNode
from obeyon_rfs.components.nodes.client.http_node import HttpNode
from obeyon_rfs.components.nodes.client.statemachine_node import StateMachineNode

