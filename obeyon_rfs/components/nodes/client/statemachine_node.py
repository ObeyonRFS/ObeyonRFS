
from typing import TYPE_CHECKING
import asyncio
import sys
from obeyon_rfs.components import ORFS_Message, ORFS_MessageType
from obeyon_rfs.components.nodes.client import ClientNode

class StateMachineNode(ClientNode):
    def __init__(self,node_name:str,core_host:str,core_port:int):
        super().__init__(
            node_name=node_name,
            core_host=core_host,
            core_port=core_port
        )