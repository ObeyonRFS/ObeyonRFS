from obeyon_rfs.components.nodes.client import ClientNode

class SerialDriverNode(ClientNode):
    def __init__(self, node_name: str):
        super().__init__(node_name)