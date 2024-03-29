from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from obeyon_rfs.components import ORFS_Component, ORFS_MessageType
    from obeyon_rfs.components.nodes import Node

class HttpNode(Node):
    def __init__(self):
        super().__init__()