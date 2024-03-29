from typing import TYPE_CHECKING


from obeyon_rfs.components import ORFS_Component, ORFS_MessageType
from obeyon_rfs.components.nodes.client import ClientNode

class HttpNode(ClientNode):
    def __init__(self):
        super().__init__()